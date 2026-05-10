---
name: nieta-login
description: 捏Ta 手机号验证码登录获取 token，并用 token 调用图库 API 获取作品图片直链。前端通过 page_phone_login.js 库完成登录，后端 3000 端口提供 session 管理。
---

# 捏Ta 登录与图库

捏Ta（`talesofai.cn` / `nieta.art`）用户图库 API。通过手机号验证码登录获取 token，调用图库接口获取作品列表及图片直链。

## 前端登录（新版：page_phone_login.js）

前端使用 `page_phone_login.js` 库处理登录 UI 和 API 调用：

```html
<script src="https://claw-annuonie-pages.talesofai.com/phone-login/page-phone-login.js"></script>
```

库会自动创建全屏登录页面（白色背景 + 手机号/验证码输入框 + 用户协议 + 登录按钮），内部直接调用 `https://api.talesofai.cn` 的登录 API。

### 前端 → 后端连接流程

```
1. page_phone_login() 完成登录 → 返回 token
2. LoginView.vue 用 token 调 fetchNetaProfile → 获取用户信息
3. POST /api/session/create → 后端 3000 端口创建 session
4. 后端返回 { session, me, role, title, signature }
5. 存 localStorage → emit('logged-in') → App.vue 切换到主界面
```

### 后端部署

后端在 `pages/server.py`，端口 3000：

```bash
cd /workspace/pages && python3 server.py
```

后端同时提供：
- 静态文件服务（`dist/` 目录）
- API 路由（`/api/session/create`, `/api/members`, `/api/forum/posts` 等）
- 捏Ta API 代理（`/api/proxy/request-code`, `/api/proxy/verify-code`）

### 开发环境代理

Vite 开发服务器需要代理 `/api` 到 3000 端口：

```js
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:3000',
      changeOrigin: true,
      secure: false,
    },
  },
},
```

### 登录获取 Token（旧版代理方式，已弃用）

~~手机号 + 4位验证码登录，详见 `index.html` / `/workspace/pages/server.py` 中内置页面。~~

| 前端调用 | 3000 后端代理到 | 说明 |
|------|------|------|
| `POST /api/proxy/request-code` | `POST /v1/user/request-verification-code` | body: `{ phone_num }` |
| `POST /api/proxy/verify-code` | `POST /v1/user/verify-with-phone-num` | body: `{ phone_num, code }` |
| `GET /api/health` | 本地健康检查 | 返回 `{ ok: true, service, port }` |

## 图库 API

- **Base**: `https://api.talesofai.cn`
- **Auth**: `x-token: <token>`（**不是** `Authorization: Bearer`）
- **OpenAPI**: `https://api.talesofai.cn/openapi.json`

### 作品列表

```
GET /v1/artifact/list?page_index=0&page_size=20&modality=PICTURE
```

参数：

| 参数 | 说明 |
|------|------|
| `page_index` | 页码，0 起始 |
| `page_size` | 每页数量，≤100 |
| `modality` | `PICTURE` / `VIDEO` / `AUDIO` |
| `status` | `SUCCESS` 等 |
| `is_starred` | `true` 仅收藏 |

返回的 `url` 字段即为图片直链，可直接用于 `<img src="...">`。

### 示例

```bash
curl -s -H "x-token: <TOKEN>" \
  "https://api.talesofai.cn/v1/artifact/list?page_index=0&page_size=3&modality=PICTURE"
```

返回：

```json
{
  "total": 999999,
  "list": [
    {
      "uuid": "9d01c24b-1e7d-4118-99ce-d8f115b08003",
      "status": "SUCCESS",
      "url": "https://oss.talesofai.cn/sts/b91c3751186d4f649576686168347900/107d5f5b-9d50-405c-9d2f-398bb25840ad.png",
      "modality": "PICTURE",
      "ctime": "2026-05-08 21:00:55",
      "platform": "nieta-app"
    }
  ]
}
```

### 图片直链格式

两种 URL 格式，均来自 `/v1/artifact/list` 返回的 `url` 字段：

- `https://oss.talesofai.cn/sts/<user_uuid>/<file_uuid>.<ext>`
- `https://oss.talesofai.cn/picture/<artifact_uuid>.<ext>`

直接嵌入 HTML：

```html
<img src="https://oss.talesofai.cn/sts/b91c3751186d4f649576686168347900/107d5f5b-9d50-405c-9d2f-398bb25840ad.png" />
```

无需额外鉴权，可直接访问。

### 上传图片到图库

三步完成：

**Step 1：获取预签名上传 URL**

```bash
curl -s -H "x-token: <TOKEN>" \
  "https://api.talesofai.cn/v1/oss/upload-signed-url?suffix=png"
```

返回：

```json
{
  "upload_url": "http://talesofai.oss-cn-shanghai.aliyuncs.com/upload/<user_uuid>/<file_uuid>.png?...",
  "view_url": "https://oss.talesofai.cn/upload/<user_uuid>/<file_uuid>.png"
}
```

**Step 2：PUT 上传文件到 OSS**

```bash
curl -s -X PUT -T image.png "<upload_url>"
```

**Step 3：注册到图库**

```bash
curl -s -H "x-token: <TOKEN>" -H "Content-Type: application/json" \
  -d '{"url": "<view_url>"}' \
  "https://api.talesofai.cn/v1/artifact/picture"
```

返回 artifact 对象（含 `uuid`、`url`、`detail.width/height` 等）。

### 其他接口

| 接口 | 说明 |
|------|------|
| `GET /v1/artifact/artifact-detail?uuids=<uuid>` | 作品详情（含尺寸、OSS 信息） |
| `GET /v1/artifact/picture-detail?uuid=<uuid>` | 图片详情 |
| `DELETE /v1/artifact?uuid=<uuid>` | 删除作品 |
| `GET /v1/user/` | 用户信息（昵称、粉丝数、作品数等） |

## 浏览器上传关键坑

### OSS 签名校验

PUT 到 OSS 时**不能带 `Content-Type` 头**，否则 `SignatureDoesNotMatch` → 403。

OSS 签名不含 Content-Type，任何自定义 Content-Type 都会破坏签名。

### 浏览器 fetch 自动加 Content-Type

`fetch(url, { method: "PUT", body: file })` 中，浏览器会根据 File/Blob 的 `.type` 属性自动添加 `Content-Type` 头（如 `image/png`）。即使代码里不写，浏览器也会自动加。

**解决：** 用空 type 的 Blob 包裹：

```javascript
const rawBlob = new Blob([file], { type: "" });
await fetch(uploadUrl, { method: "PUT", body: rawBlob });
```

### CORS

OSS bucket 配置了 `Access-Control-Allow-Origin: *`，允许任意域名 PUT。403 只来自签名问题，不是跨域。

### 官方 App 的上传方式

`app.nieta.art` 使用 STS token + 阿里云 OSS JS SDK 做分片上传（multipart），而非 `upload-signed-url`。两者都可以用，STS 方式支持进度回调和分片断点续传。
