---
name: neta-character-resolve
description: Resolve Neta character UUIDs/short links into public OC profile and author info using the knight-resolve pattern. Use when a user asks why a Neta UUID/short link cannot find a character, when importing identity/role cards, or when needing character owner/creator UUID comparison.
---

# Neta Character Resolve / Knight Resolve Pattern

Use this skill whenever handling Neta character links, UUIDs, short links, identity-card imports, or creator UUID checks.

## Key lesson

Do **not** confuse “UUID extraction” with “character profile resolution”.

- `uuid-extractor` only does: short link → original URL → UUID.
- `knight-resolve` does: UUID/link → backend proxy → public Neta character profile + author.

For identity cards, use the `knight-resolve` pattern.

## Reference pages

- `https://claw-annuonie-pages.talesofai.com/knight-resolve/api-doc.html`
- `https://claw-annuonie-pages.talesofai.com/knight-resolve/`

## Correct API pattern

Browser frontend should call your own backend proxy:

```http
GET /api/knight/resolve?uuid=<uuid-or-link-or-shortlink>
```

The backend proxy should call Neta public profile API:

```http
GET https://api.talesofai.cn/v2/travel/parent/{uuid}/profile
```

Required headers:

```http
x-platform: nieta-app/web
x-nieta-app-version: 6.8.9
accept: application/json
user-agent: Mozilla/5.0
```

Important:

- This public profile endpoint does **not** require user token.
- Browsers cannot reliably call Neta API directly because of CORS.
- Use backend proxy, but do **not** send or store Neta user token for this character lookup.

## Short-link handling

If input contains a Neta short link:

```text
https://t.nieta.art/xxxx
```

First resolve it server-side:

```http
GET https://api.talesofai.cn/v1/util/original-url?short_url=<encoded short URL>
```

Then extract UUID from the returned URL.

Example:

```text
https://t.nieta.art/FqZn1Saa
```

resolves to:

```text
https://app.nieta.art/oc?uuid=424aad87-7ad7-4c9f-8c6c-5d0fed62260d&from_user=b91c3751186d4f649576686168347900
```

Character UUID:

```text
424aad87-7ad7-4c9f-8c6c-5d0fed62260d
```

Creator/author UUID may appear as:

```text
from_user=b91c3751186d4f649576686168347900
```

Also support these creator fields:

- `from_user`
- `creator_uuid`
- `owner_uuid`
- `user_uuid`
- `author_uuid`

## Expected response shape

Return a trimmed object for frontend use:

```json
{
  "oc": {
    "uuid": "...",
    "name": "...",
    "short_name": "...",
    "gender": "...",
    "status": "...",
    "accessibility": "PUBLIC",
    "heat_score": 0,
    "hashtags": [],
    "avatar_img": "...",
    "header_img": "...",
    "bio_summary": {
      "age": "...",
      "persona": "...",
      "background": "..."
    }
  },
  "author": {
    "uuid": "...",
    "nick_name": "...",
    "avatar_url": "...",
    "subscriber_count": 0,
    "story_count": 0
  },
  "raw": {}
}
```

## Identity card import rule

For identity/role cards:

1. Resolve input through `/api/knight/resolve`.
2. Use `author.uuid` as creator UUID.
3. Compare with current site's stored `creator_uuid` / user uuid.
4. If mismatch, reject with:

```text
你不是Ta，你扮演不了Ta
```

## Security rule

For this character lookup, **do not upload Neta token to backend**.

- Backend only proxies public profile and short-link resolution.
- Backend should not store Neta tokens.
- Site auth should use site session, not Neta token.

## Troubleshooting

If `/v2/travel/parent/{uuid}/profile` returns:

```text
此接口只接受app请求
```

then the backend proxy is missing required headers:

```http
x-platform: nieta-app/web
x-nieta-app-version: 6.8.9
```

If search by UUID returns empty, do not use parent-search for direct UUID resolution. Use the profile endpoint above.
