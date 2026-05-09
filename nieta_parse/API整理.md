# app.nieta.art 前端 API 静态解析整理

> 来源：公开前端静态资源，仅基于 JS 字符串与调用上下文推断；方法/参数不保证 100% 准确。未包含任何登录态或私有数据。

## 概览

- API 路径数量：358
- 默认生产 API：`https://api.talesofai.cn`（海外/neta 分支为 `https://api.talesofai.com`）
- 静态资源 CDN：`https://oss.talesofai.cn/static/nieta-app/assets/`

## 生成/Artifact/音视频（38）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/generate` | 未知 | character_uuid, collection_uuid, data, image, prompt, query, uuid | `index-Baw-x7k4.js, index-C6ybIWzf.js, index-CzwWqJ6a.js, index-DCLSf2DR.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js, index-zWptraxF.js, inherit-Qa2IZPlR.js, manga-CQejVOoY.js` |
| `/v1/artifact` | DELETE, GET, POST | data, headers, image, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/` | GET, POST, PUT | data, headers, image, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/artifact-detail` | GET | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/list` | GET | data, headers, image, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/modify-audio-name` | GET, PUT | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/picture` | DELETE, GET, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/picture-detail` | GET, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/task/` | GET, POST | data, headers, image, page_index, page_size, query, taskId | `index-C6ybIWzf.js, talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/task/${e.taskId}` | GET, POST | data, headers, prompt, taskId, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/artifact/tcp-permissions-for-same-style` | GET, POST, PUT | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/verse` | GET, PATCH, POST | image, images, page_index, page_size, prompt, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/verse/checkpoint` | GET, POST | data, prompt, query, taskId | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/artifact/verse/list` | GET, PATCH, POST | image, images, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/verse/task` | GET, PATCH, POST | image, images, page_index, page_size, prompt, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/video` | DELETE, GET, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/video-detail` | GET | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/video-stream-url` | GET | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/artifact/video-stream/` | GET | - | `index-C6ybIWzf.js` |
| `/v1/artifact/video-stream/${e}` | GET | - | `index-legacy-CXGuZtui.js` |
| `/v1/artifact/video_task/` | GET, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/audio/bgm` | GET | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/audio/bgm/list` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/audio/generate` | GET, POST, PUT | query, uuid | `index-Bhq9MIdG.js, thoumask-DHzXJUi8.js` |
| `/v1/prompt/full-prompt-tags` | GET | prompt, query, uuid | `index-Bhq9MIdG.js, talesofai-modules-generate-mkiii-BWxD3gnq.js` |
| `/v1/prompt/str2tags?query=` | GET | collection_uuid, prompt, query, record_uuid, uuid | `index-zWptraxF.js` |
| `/v3/ai_director_merge_video_submit_task` | GET, POST | data, headers, prompt, taskId, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v3/make_face_detailer` | DELETE, POST | data, headers, image, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/make_image` | POST, PUT | data, headers, image, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/make_oc_image_ref` | GET, POST | headers, image, taskId | `index--EYE-rMg.js` |
| `/v3/make_song` | GET, PATCH, POST | image, images, page_index, page_size, prompt, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/make_video` | GET, POST | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/merge_media/v3/submit_task` | GET, POST | data, headers, prompt, query, taskId, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v3/task-pool` | GET | - | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/task?taskId=` | GET, POST | headers, image, query, taskId | `index--EYE-rMg.js, index-C6ybIWzf.js` |
| `/v3/task?taskId=${e.taskId}` | GET, POST | data, headers, prompt, taskId, uuid | `index-legacy-CXGuZtui.js` |
| `/v3/video_model_list` | GET, POST | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/video_tool_adjust_speed` | POST | page_index, page_size, prompt, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |

## OC/角色设定（9）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/v2/oc/complete-oc-appearance?gender=` | GET | image, uuid | `index--EYE-rMg.js` |
| `/v2/oc/list-worlds` | GET | - | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/oc/make_oc_bio` | DELETE, GET, PATCH, POST | page_index, page_size, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/oc/oc` | DELETE, GET, PATCH, POST | page_index, page_size, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/oc/oc-previews` | GET, POST | data, image, images, uuid | `index--EYE-rMg.js` |
| `/v2/oc/oc/` | DELETE, GET, PATCH, POST | page_index, page_size, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/oc/oc_to_character_token` | POST | data, headers, uuid | `index--EYE-rMg.js` |
| `/v2/oc/tcp-expand` | GET, POST, PUT | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/oc/tcp-hashtag-candidates` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |

## 上传/OSS（2）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/v1/oss/anonymous-upload-token` | GET | query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/oss/sts-upload-token` | GET | query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |

## GPT/LLM/导演（6）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/v1/ai_director_audio_preset` | GET, POST | - | `index-Bhq9MIdG.js` |
| `/v3/gpt/dify/chat-complete` | 未知 | body, data, headers | `config-6thElw8f.js, index-zWptraxF.js` |
| `/v3/gpt/dify/chat-complete-preview` | 未知 | query | `manga-CQejVOoY.js` |
| `/v3/gpt/dify/text-complete` | 未知 | body, data, headers, image, prompt, query | `index-C6ybIWzf.js, talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/gpt/message/` | GET, POST | headers, taskId, uuid | `index-C6ybIWzf.js` |
| `/v3/gpt/message/${e}` | GET, POST | query, taskId, uuid | `index-legacy-CXGuZtui.js` |

## 用户/登录/设备/权限（31）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/v1/badge/me/active-avatar-frame` | GET, POST, PUT | query, user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/badge/me/badges` | GET, POST, PUT | query, user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/device/deregister` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/device/register` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/privilege/config/water_mark_remove` | GET, POST, PUT | query, user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/privilege/config/water_mark_remove?enable=` | POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/user/` | GET | - | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/user/?uuid=` | GET, POST | data, query, user_uuid, uuid | `index-C6ybIWzf.js, index-CWiELHpY.js` |
| `/v1/user/?uuid=${e}` | GET | uuid | `index-legacy-CXGuZtui.js` |
| `/v1/user/?uuid=${t}` | GET, POST | query, user_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/user/check_im?receiver=` | GET, POST | query, user_uuid, uuid | `index-C6ybIWzf.js` |
| `/v1/user/check_im?receiver=${t}&only_check=${n}` | GET, POST, PUT | query, user_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/user/logout` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/user/refresh-token` | 未知 | data, headers | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/user/request-verification-code` | DELETE, GET, POST | query | `index-C6LQCRQq.js, index-C6ybIWzf.js, index-DYPpzymH.js, index-legacy-CXGuZtui.js` |
| `/v1/user/search` | GET | page_index, page_size, query, user_uuid, uuid | `search-9THZ6j7f.js` |
| `/v1/user/user` | DELETE, POST, PUT | query, user_uuid, uuid | `index-C6LQCRQq.js, index-C6ybIWzf.js, index-DYPpzymH.js, index-legacy-CXGuZtui.js` |
| `/v1/user/user-blacklist` | GET, PUT | query, user_uuid, uuid | `creator-waterfall-Cf5F60J1.js, index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/user/user-subscribe` | GET, PUT | query, user_uuid, uuid | `creator-waterfall-Cf5F60J1.js, index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/user/verify-one-login` | GET, POST | data | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/user/verify-with-apple` | POST | - | `index-C6ybIWzf.js, index-DYPpzymH.js, index-legacy-CXGuZtui.js` |
| `/v1/user/verify-with-google` | POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/user/verify-with-phone-num` | DELETE, POST | - | `index-C6LQCRQq.js, index-C6ybIWzf.js, index-DYPpzymH.js, index-legacy-CXGuZtui.js` |
| `/v1/user/verify-with-wechat-app-connect` | POST | - | `index-C6ybIWzf.js, index-DYPpzymH.js, index-legacy-CXGuZtui.js` |
| `/v1/waitlist/apply` | GET, POST | query, user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/waitlist/status` | GET, POST, PUT | query, user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/users/` | GET | data, query, uuid | `index-GCFabZlw.js` |
| `/v2/users/anonymous` | GET, POST, PUT | query, user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/users/anonymous-ad` | GET, POST, PUT | query, user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/users/ap-delta-info` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/users/me/relation` | POST | data, user_uuid, uuid | `index-DCLSf2DR.js` |

## 作品/Story/Collection/图片（25）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/collection` | 未知 | data | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/collection/interaction` | GET | character_uuid, collection_uuid, data, mission_uuid, prompt, query, record_uuid, taskId, user_uuid, uuid | `history-BXFIOcpV.js, index-Bf6mS3J0.js, index-Bhq9MIdG.js, index-C6ybIWzf.js, index-CKOmzWqB.js, index-CVKoIdWB.js, index-CWiELHpY.js, index-Cdnr6WHU.js, index-Ch7YwaCM.js, index-CiFiVI9H.js, index-DCLSf2DR.js, index-DyqLr5qQ.js, index-EJLNo-eZ.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js` |
| `/collection/interaction?` | 未知 | page_index, page_size, uuid | `thoumask-DHzXJUi8.js` |
| `/collection/interaction?uuid=` | 未知 | data, uuid | `thoumask-DHzXJUi8.js` |
| `/collection/mission` | GET | character_uuid, collection_uuid, data, mission_uuid, query, record_uuid, uuid | `index-C11KU9PB.js, index-C6ybIWzf.js, index-CKOmzWqB.js, index-GCFabZlw.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js, start-page-BhBFYtOE.js` |
| `/collection/mission?seed_campaign_uuid=` | 未知 | character_uuid, mission_uuid, uuid | `index-DL0T13Kg.js` |
| `/collection/profile` | 未知 | collection_uuid, data, query, uuid | `index-Bf6mS3J0.js, index-C6ybIWzf.js, index-EJLNo-eZ.js, index-legacy-CXGuZtui.js` |
| `/collection/promotion` | 未知 | collection_uuid, data, query, uuid | `index-C6ybIWzf.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js` |
| `/collection/promotion/history` | 未知 | collection_uuid, data, query, uuid | `index-BPA1KEnv.js, index-C6ybIWzf.js, index-Ch7YwaCM.js, index-legacy-CXGuZtui.js` |
| `/collection/publish` | DELETE, GET | collection_uuid, data, endpoint, image, prompt, query, record_uuid, user_uuid, uuid | `history-D4Kin9IG.js, index-Baw-x7k4.js, index-Bf6mS3J0.js, index-Bhq9MIdG.js, index-C11KU9PB.js, index-C6ybIWzf.js, index-CVKoIdWB.js, index-Ch7YwaCM.js, index-DCLSf2DR.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js, mkiii-Dbg_1CSy.js` |
| `/v1/picture/search` | GET | page_index, page_size, query, user_uuid, uuid | `search-9THZ6j7f.js` |
| `/v3/story/` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/collection` | DELETE, GET, PUT | data, image, images, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/collection-pin-status/` | GET | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/collection_review_status` | GET | collection_uuid, query, uuid | `internal-review-CZQIblBH.js` |
| `/v3/story/feeds` | GET, POST | image, images, page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/generate-story-title` | GET, PATCH, POST, PUT | page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/modify_collection_review` | POST | collection_uuid, uuid | `internal-review-CZQIblBH.js` |
| `/v3/story/pin` | GET, POST | image, images, page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/same-style-stories` | GET | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/search` | GET | page_index, page_size, query, user_uuid, uuid | `search-9THZ6j7f.js` |
| `/v3/story/story` | DELETE, GET, POST, PUT | data, page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/story-detail` | GET, PATCH, POST, PUT | data, image, images, page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/tcp-permissions-for-same-style` | GET | page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/story/travel` | GET | page_index, page_size, query, record_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |

## Verse/Agent（21）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/v1/agent/` | DELETE, POST | collection_uuid, data, endpoint, headers, image, images, query, uuid | `index-C6ybIWzf.js` |
| `/v1/agent/${$.uuid}` | DELETE | endpoint, query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/agent/${e.manuscript.uuid}` | POST | collection_uuid, endpoint, image, images, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/agent/limit-exceeded` | GET | collection_uuid, data, endpoint, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/verse/artifact/` | DELETE, GET, POST | query, uuid | `index-C6ybIWzf.js` |
| `/v1/verse/artifact/${e}/claim` | DELETE, GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/verse/artifact/${e}/write_lock` | DELETE, GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/verse/background_is_running/` | GET | character_uuid, collection_uuid, taskId, uuid | `index-C6ybIWzf.js` |
| `/v1/verse/background_is_running/${e.task_uuid}` | GET | character_uuid, collection_uuid, taskId, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/verse/background_should_stop/` | GET, POST | query, uuid | `index-C6ybIWzf.js` |
| `/v1/verse/background_should_stop/${e.artifact_load_uuid}` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/verse/background_start` | POST | character_uuid, collection_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/verse/background_stop` | GET, POST | uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/verse/catalog` | GET, POST | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/verse/catalog/` | GET, POST | query, uuid | `index-C6ybIWzf.js` |
| `/v1/verse/catalog/${e.catalog_uuid}/entries` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/verse/modifyhtml` | GET, POST | data, prompt, query, taskId, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/verse/preset/` | GET, POST | taskId, uuid | `index-C6ybIWzf.js` |
| `/v1/verse/preset/${e.uuid}` | GET, POST | data, headers, prompt, taskId, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/verse/screenshot` | GET, POST | data, headers, prompt, taskId, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/verse/tool` | GET, POST | data, prompt, query, taskId, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |

## Travel/Campaign（36）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/v2/travel/campaign-search` | GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/travel/campaign/bulk/list?` | GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js` |
| `/v2/travel/campaign/bulk/list?${t.map((e=>` | GET | page_index, page_size, query, uuid | `index-legacy-CXGuZtui.js` |
| `/v2/travel/campaign/catalog/` | DELETE, GET | page_index, page_size, query, record_uuid, uuid | `index-C6ybIWzf.js` |
| `/v2/travel/campaign/catalog/${n}/entries` | DELETE, GET | page_index, page_size, query, record_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v2/travel/campaign/catalogs` | GET | page_index, page_size, query, record_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/travel/characters` | DELETE, GET, PATCH, POST | page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/characters/` | GET, PATCH, POST | character_uuid, mission_uuid, page_index, page_size, prompt, query, record_uuid, uuid | `index-C6ybIWzf.js, index-zWptraxF.js, talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/characters/${t.character_uuid}/mission-records` | GET, POST | character_uuid, mission_uuid, prompt, record_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v2/travel/characters/${t.character_uuid}/recent-mission-record-briefs` | GET | character_uuid, mission_uuid, prompt, uuid | `index-legacy-CXGuZtui.js` |
| `/v2/travel/characters/${t}/campaigns/${n}` | GET | page_index, page_size, query, record_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v2/travel/mission-records/` | GET, PATCH, PUT | character_uuid, data, mission_uuid, page_index, page_size, prompt, query, record_uuid, uuid | `index-C6ybIWzf.js, index-zWptraxF.js, talesofai-modules-core-cSUdSjKQ.js, thoumask-DHzXJUi8.js` |
| `/v2/travel/mission-records/${t.record_uuid}/progress` | PATCH | character_uuid, mission_uuid, prompt, record_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v2/travel/mission-records/${t}` | GET | page_index, page_size, query, record_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v2/travel/parent` | DELETE, GET, PATCH, POST | page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent-catalog` | GET | page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent-catalog/` | GET | query | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent-catalog/entries` | GET | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent-search` | GET, PATCH, PUT | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent-search-community` | GET, PATCH, PUT | page_index, page_size, query | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent-search-under-hashtag` | GET, PATCH, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent/` | DELETE, GET, PATCH, POST | collection_uuid, image, images, page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent/bulk/list?in_editor=` | GET | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent/modify-review` | POST | data, uuid | `index-DCLSf2DR.js` |
| `/v2/travel/parent/parent-favor` | GET, PUT | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent/parent-favor/groups` | GET | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/travel/parent/parent-favor/list` | GET | query | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v3/travel/campaign` | PATCH, POST | character_uuid, data, mission_uuid, uuid | `index-DL0T13Kg.js` |
| `/v3/travel/campaign/` | DELETE, GET, PATCH, POST | character_uuid, data, mission_uuid, page_index, page_size, prompt, query, record_uuid, uuid | `index-C6ybIWzf.js, index-DL0T13Kg.js` |
| `/v3/travel/campaign/${t}` | DELETE, GET | page_index, page_size, query, record_uuid, uuid | `index-legacy-CXGuZtui.js` |
| `/v3/travel/campaign/${t}/custom-prompt` | GET, POST | character_uuid, mission_uuid, prompt, uuid | `index-legacy-CXGuZtui.js` |
| `/v3/travel/campaign/recommend` | GET | page_index, page_size, query, record_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v3/travel/campaign/rewrite` | 未知 | body, data, headers | `index-DL0T13Kg.js` |
| `/v3/travel/campaigns` | DELETE, GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v3/travel/mission-record/` | GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js` |
| `/v3/travel/mission-record/${t}/conversation` | DELETE, GET | page_index, page_size, query, uuid | `index-legacy-CXGuZtui.js` |

## 首页/推荐/排行/搜索/活动（18）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/search` | 未知 | body, character_uuid, collection_uuid, data, headers, query, uuid | `index-Bf6mS3J0.js, index-C6ybIWzf.js, index-CKOmzWqB.js, index-legacy-CXGuZtui.js, talesofai-modules-litellm-DFSSRCuD.js` |
| `/v1/activities` | GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/activities/` | GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js` |
| `/v1/activities/${a}/selected-stories/highlights?page_index=0&page_size=10&sort_by=highlight_mark_time` | GET | page_index, page_size, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/activities/${n}/selected-stories/${r}` | GET | page_index, page_size, query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/activities/${t}` | GET | page_index, page_size, query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/activities/${t}/stories` | GET | page_index, page_size, query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/home/collection/` | GET | headers, image, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/home/draft` | GET, POST, PUT | page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/home/feature/record` | GET, POST, PUT | page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/home/feed/dynamic` | GET, POST, PUT | page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/home/feed/interactive` | GET, POST, PUT | collection_uuid, page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js, talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/home/feed/mainlist` | GET | page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/home/search/character` | GET | character_uuid, page_index, page_size, query, uuid | `index-Bf6mS3J0.js` |
| `/v1/home/status_queue` | GET, POST, PUT | page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/rank/stories/` | GET, PUT | query, user_uuid, uuid | `creator-waterfall-Cf5F60J1.js` |
| `/v1/rank/travel_character_parent/` | GET, PUT | data, query, user_uuid, uuid | `creator-waterfall-Cf5F60J1.js` |
| `/v1/rank/users/` | GET, PUT | query, user_uuid, uuid | `creator-waterfall-Cf5F60J1.js` |

## 糖豆/推广/曝光（6）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/v1/exposure/candy-account` | GET, POST | query | `candy-Cbx8fJUA.js` |
| `/v1/exposure/candy-items` | GET | query | `candy-Cbx8fJUA.js` |
| `/v1/exposure/collection-exposure-detail` | GET | query | `candy-Cbx8fJUA.js` |
| `/v1/exposure/consume-candy` | GET, POST | query | `candy-Cbx8fJUA.js` |
| `/v1/exposure/consumption_records_v2` | GET, POST | query | `candy-Cbx8fJUA.js` |
| `/v1/exposure/has-permission` | GET | query | `candy-Cbx8fJUA.js` |

## 支付/微信（9）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/pay` | 未知 | body, data, query, uuid | `index-C6ybIWzf.js, index-MQeRC-w3.js, index-legacy-CXGuZtui.js` |
| `/pay?uuid=` | 未知 | query, uuid | `index-C6ybIWzf.js` |
| `/payment/` | POST | query, uuid | `index-C6ybIWzf.js` |
| `/v1/commerce/orders` | GET, POST | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/commerce/orders/` | GET, POST | query, uuid | `index-C6ybIWzf.js` |
| `/v1/commerce/orders/${n}/payment/${r}` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/commerce/orders/${t.orderUuid}/capture` | GET, POST | uuid | `index-legacy-CXGuZtui.js` |
| `/v1/commerce/orders/${t.orderUuid}/capture-stripe` | POST | uuid | `index-legacy-CXGuZtui.js` |
| `/v1/commerce/orders/${t}` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |

## 其他（157）

| 路径 | 方法推断 | 参数/上下文线索 | 所在文件 |
|---|---:|---|---|
| `/agent` | 未知 | - | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/audio/speech` | DELETE, POST | body, data, headers | `talesofai-modules-litellm-DFSSRCuD.js` |
| `/audio/transcriptions` | POST | body, data, headers | `talesofai-modules-litellm-DFSSRCuD.js` |
| `/audio/translations` | POST | body, data | `talesofai-modules-litellm-DFSSRCuD.js` |
| `/character/create` | DELETE | collection_uuid, data, image, query, uuid | `index-B_Ob4gwH.js, index-C6ybIWzf.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js, mkiii-Dbg_1CSy.js` |
| `/character/discover` | 未知 | character_uuid, data, image, page_index, page_size, query, uuid | `entry-AeZtvmCX.js, index-Baw-x7k4.js, index-Bf6mS3J0.js, index-Bhq9MIdG.js, index-C6ybIWzf.js, index-Cdnr6WHU.js, index-DL0T13Kg.js, index-legacy-CXGuZtui.js, index-zWptraxF.js, mkiii-Dbg_1CSy.js` |
| `/character/discover/search` | 未知 | query, uuid | `index-B_Ob4gwH.js, index-C6ybIWzf.js, index-legacy-CXGuZtui.js, mkiii-Dbg_1CSy.js` |
| `/character/profile` | 未知 | data, image, images, prompt, query, taskId, uuid | `index--EYE-rMg.js, index-Bhq9MIdG.js, index-C11KU9PB.js, index-C6ybIWzf.js, index-Ch7YwaCM.js, index-DCLSf2DR.js, index-legacy-CXGuZtui.js` |
| `/characters` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/comment` | 未知 | data, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/home` | 未知 | headers | `talesofai-modules-mqtt-C3VSOOaa.js` |
| `/manga` | 未知 | collection_uuid, data, mission_uuid, page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/oc` | 未知 | character_uuid, collection_uuid, data, mission_uuid, prompt, query, record_uuid, uuid | `index-B_Ob4gwH.js, index-Bf6mS3J0.js, index-C11KU9PB.js, index-C6ybIWzf.js, index-CWiELHpY.js, index-Ch7YwaCM.js, index-DCLSf2DR.js, index-DR9GxcMh.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js` |
| `/picture` | GET | collection_uuid, data, image, images, page_index, page_size, query, user_uuid, uuid | `index-Bf6mS3J0.js, index-C11KU9PB.js, index-C6ybIWzf.js, index-CzwWqJ6a.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js` |
| `/picture-editor` | 未知 | collection_uuid, data, image, query, uuid | `index-C6ybIWzf.js, index-EJLNo-eZ.js, index-legacy-CXGuZtui.js` |
| `/picture-selector` | 未知 | character_uuid, collection_uuid, data, image, page_index, page_size, prompt, query, record_uuid, user_uuid, uuid | `entry-AeZtvmCX.js, history-D4Kin9IG.js, index--EYE-rMg.js, index-Baw-x7k4.js, index-Bf6mS3J0.js, index-Bhq9MIdG.js, index-C11KU9PB.js, index-C6ybIWzf.js, index-Cdnr6WHU.js, index-DCLSf2DR.js, index-DL0T13Kg.js, index-DYPpzymH.js, index-DqlujJi6.js, index-EJLNo-eZ.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js, mkiii-Dbg_1CSy.js` |
| `/ranking` | 未知 | collection_uuid, data, prompt, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/task-center` | 未知 | data | `index-C6ybIWzf.js, index-Ch7YwaCM.js, index-legacy-CXGuZtui.js` |
| `/travel` | 未知 | character_uuid, collection_uuid, data, mission_uuid, page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-Cdnr6WHU.js, index-DCLSf2DR.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js` |
| `/user` | GET | character_uuid, collection_uuid, data, page_index, page_size, query, user_uuid, uuid | `chat-DG3zzIdK.js, creator-waterfall-Cf5F60J1.js, index-Bf6mS3J0.js, index-C11KU9PB.js, index-C6ybIWzf.js, index-CKOmzWqB.js, index-CVKoIdWB.js, index-CWiELHpY.js, index-Ch7YwaCM.js, index-DCLSf2DR.js, index-DyqLr5qQ.js, index-QSp7kGC0.js, index-legacy-CXGuZtui.js` |
| `/user-security` | 未知 | - | `index-C6ybIWzf.js, index-DYPpzymH.js, index-legacy-CXGuZtui.js` |
| `/user/subscribe` | 未知 | - | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/user/subscribe?mode=fan` | 未知 | - | `index-Ch7YwaCM.js` |
| `/user/subscribe?mode=fan&uuid=` | 未知 | uuid | `index-CWiELHpY.js` |
| `/user/subscribe?mode=subscribe` | 未知 | - | `index-Ch7YwaCM.js` |
| `/user/subscribe?mode=subscribe&uuid=` | 未知 | uuid | `index-CWiELHpY.js` |
| `/user?uuid=` | 未知 | data, query, uuid | `index-DCLSf2DR.js` |
| `/v1/ab-experiment/get-or-join/all-running` | POST | user_uuid, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/app-release/latest-release` | GET | query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/app/loads` | GET | - | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/assignment/assignment-list` | GET, POST | uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/assignment/complete-assignment-action` | GET, POST, PUT | uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/assignment/user-assignment` | GET, POST, PUT | uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/cchat/conversation/` | GET, POST | collection_uuid, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/cchat/conversation/casual` | POST | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/cchat/conversation/primary` | DELETE, POST | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/cchat/conversation/travel` | POST | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/cchat/conversations/` | GET, POST | collection_uuid, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/checkin/manual` | GET, POST | data, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/checkin/status` | GET, POST | data, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/collection-interactive` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/collection-interactive/char_roll?num=` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/collection-interactive/collection_uuid=` | GET | collection_uuid, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/collection-interactive/search` | GET | page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/collection-interactive/text_reply` | GET, PUT | page_index, page_size, query | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/collection-interactives/video-input` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/collection-interactives/vtokens` | GET, PUT | collection_uuid, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/comment/comment` | DELETE, GET, POST | query, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/comment/comment-list` | DELETE, GET, POST | query, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/comment/comment?uuid=` | DELETE, GET, POST | query, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/comment/like` | POST, PUT | query, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/comment/location` | DELETE, GET, POST | query, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/comment/pin` | POST, PUT | uuid | `thoumask-DHzXJUi8.js` |
| `/v1/comment/typeahead` | DELETE, GET, POST | query, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/commerce/gift_list` | GET, POST | uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/commerce/purchase_spu_by_ap/` | GET, POST | character_uuid, data, user_uuid, uuid | `index-C6ybIWzf.js, index-DCLSf2DR.js` |
| `/v1/commerce/purchase_spu_by_ap/${t.spu_uuid}` | GET, POST | uuid | `index-legacy-CXGuZtui.js` |
| `/v1/commerce/spu-detail/` | GET, PATCH, POST | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/commerce/spu-list` | GET, PATCH | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/commerce/user-items` | GET, PATCH | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/commerce/user-items/` | GET, PATCH | query, uuid | `index-C6ybIWzf.js` |
| `/v1/commerce/user-items/${t.sku_uuid}` | GET, PATCH | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/configs/config` | GET | query | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/configs/config-list` | GET | query | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/coupon/create` | POST | uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/coupon/redeem` | POST | uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/` | GET, POST | collection_uuid, data, page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/${encodeURIComponent(i)}/campaigns` | GET | page_index, page_size, query | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/${encodeURIComponent(i)}/stories` | GET, POST | page_index, page_size, query | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/${encodeURIComponent(i)}/stories/scored` | GET | page_index, page_size, query | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/${encodeURIComponent(i)}/tcp-list` | GET | page_index, page_size, query | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/${encodeURIComponent(t)}/stories/review/${r}` | GET, POST | page_size, query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/community-top` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/feed_hashtags` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/hashtag_info/` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js` |
| `/v1/hashtag/hashtag_info/${encodeURIComponent(t)}` | GET, POST | page_index, page_size, query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/hot-collections` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/latest-hottest-collection` | GET, POST | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/lore` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/lore/delete` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/lore/event/sort-index-bulk` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/lore/events` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/lore/modify` | GET, POST | page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/lores-count` | GET, POST | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/modify` | GET, POST | page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/remove-top/` | GET, POST | data, query | `index-C6ybIWzf.js` |
| `/v1/hashtag/remove-top/${encodeURIComponent(t)}` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/subscribe` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/subscribe-bulk` | GET, POST | page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/subscribe-count` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/subscribe/collection-count` | GET, POST | page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/tcp-count` | GET | query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/hashtag/typeahead-v2/` | GET | query | `index-C6ybIWzf.js` |
| `/v1/hashtag/typeahead-v2/${encodeURIComponent(t)}` | GET, POST | page_index, page_size, query | `index-legacy-CXGuZtui.js` |
| `/v1/hashtag/typeahead/` | GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js` |
| `/v1/hashtag/typeahead/${encodeURIComponent(t)}` | GET | page_index, page_size, query | `index-legacy-CXGuZtui.js` |
| `/v1/image_edit_v1/task` | GET, POST | image, images, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/manuscript` | DELETE, GET, PATCH, POST | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/manuscript/` | DELETE, GET, PATCH, POST, PUT | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/manuscript/list` | GET, PATCH, POST, PUT | query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/message/message` | GET, PUT | data, page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/message/message-count` | GET | page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/message/message-list` | GET, PUT | data, page_index, page_size, query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/moderate/appeal` | GET, POST | query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/mqtt/client` | POST | data | `talesofai-modules-mqtt-C3VSOOaa.js` |
| `/v1/rag/cached-inspiration` | GET | data | `talesofai-modules-generate-mkiii-BWxD3gnq.js` |
| `/v1/rag/rag-recommend-stories` | POST | data, page_size, prompt, query | `talesofai-modules-generate-mkiii-BWxD3gnq.js` |
| `/v1/space/admin/moment/ban` | DELETE, GET, POST | data, page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/space/collection/feed?page_index=` | GET, POST | page_index, page_size, uuid | `index-C6ybIWzf.js` |
| `/v1/space/collection/feed?page_index=${t}&page_size=${n}&hashtag_name=${encodeURIComponent(r)}${i?` | GET, POST | data, page_index, page_size, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/space/footprint?space_uuid=` | GET, POST | page_index, page_size, uuid | `index-C6ybIWzf.js` |
| `/v1/space/footprint?space_uuid=${t}` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/space/get-by-hashtag?hashtag_name=` | GET | page_index, page_size, query, uuid | `index-C6ybIWzf.js` |
| `/v1/space/get-by-hashtag?hashtag_name=${encodeURIComponent(t)}` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/space/increase/footprint` | GET, POST | page_index, page_size, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/space/moment/comment` | DELETE, GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/space/moment/comment/delete?uuid=` | DELETE, POST | query, uuid | `index-C6ybIWzf.js` |
| `/v1/space/moment/comment/delete?uuid=${t.uuid}` | DELETE, POST | data, page_index, page_size, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/space/moment/delete` | DELETE, GET, POST | page_index, page_size, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/space/moment/detail?moment_uuid=` | DELETE, GET, POST | uuid | `index-C6ybIWzf.js` |
| `/v1/space/moment/detail?moment_uuid=${t}` | GET, POST | page_index, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/space/moment/like` | DELETE, GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/space/moment/publish` | GET, POST | page_size, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/space/playground/list?space_uuid=` | GET, POST | page_index, page_size, uuid | `index-C6ybIWzf.js` |
| `/v1/space/playground/list?space_uuid=${t}${n?` | GET, POST | uuid | `index-legacy-CXGuZtui.js` |
| `/v1/space/remove` | DELETE, GET, POST | data, page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/space/topics?space_uuid=` | GET, POST | page_index, page_size, query, uuid | `index-C6ybIWzf.js` |
| `/v1/space/topics?space_uuid=${t}` | GET, POST | query, uuid | `index-legacy-CXGuZtui.js` |
| `/v1/story/new-story` | DELETE, GET, PUT | data, image, images, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/story/story-favor` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/story/story-like` | PUT | page_index, page_size, query, uuid | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js, talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/story/story-publish?storyId=` | PUT | data, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/story/story-share` | PUT | page_index, page_size, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/tc_mem/cchat-messages` | GET, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/tc_mem/context-messages` | DELETE, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/tc_mem/experiences` | GET, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/tc_mem/experiences/abstracts/sample` | GET, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/tc_mem/memory` | GET, PATCH, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/tc_mem/reflection` | GET, PATCH, POST | data, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/thoumask/masks?` | GET, PATCH, POST | image, images, page_index, page_size, prompt, query, uuid | `talesofai-modules-core-cSUdSjKQ.js, thoumask-DHzXJUi8.js` |
| `/v1/thoumask/tcp/` | GET | page_index, page_size, uuid | `thoumask-DHzXJUi8.js` |
| `/v1/travel/characters/` | GET, PUT | page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/travel/mission-records/` | GET, PATCH, POST | image, images, page_index, page_size, query, user_uuid, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v1/util/get-readable` | GET, POST | query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/util/original-url` | GET, POST | query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v1/util/short-url` | GET, POST | query | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/story/bulk-list?` | GET | collection_uuid, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/story/favor-list-cursor` | GET, PUT | page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/story/liked-list` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/story/liked-list-cursor` | GET, PUT | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/story/newbie/tcp-feed?` | GET | collection_uuid, page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/story/story` | PUT | - | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/v2/story/user-stories` | GET | page_index, page_size, query, uuid | `talesofai-modules-core-cSUdSjKQ.js` |
| `/v2/user/ap_info` | GET | - | `talesofai-modules-core-cSUdSjKQ.js` |
| `/verse` | 未知 | character_uuid, collection_uuid, data, endpoint, image, images, prompt, query, taskId, user_uuid, uuid | `entry-AeZtvmCX.js, index-Baw-x7k4.js, index-Bf6mS3J0.js, index-C11KU9PB.js, index-C6ybIWzf.js, index-CKOmzWqB.js, index-Cdnr6WHU.js, index-legacy-CXGuZtui.js, inherit-Qa2IZPlR.js, mkiii-Dbg_1CSy.js, thoumask-DHzXJUi8.js` |
| `/verse/entry` | 未知 | - | `index-C6ybIWzf.js, index-legacy-CXGuZtui.js` |
| `/verse_template/` | GET, POST | character_uuid, headers, prompt, taskId, uuid | `index-C6ybIWzf.js` |

## 重点观察

- 生图/任务链路主要围绕 `/v3/make_image`、`/v3/task?taskId=`、`/v1/artifact/task/`、`/v1/artifact/picture*`。
- 角色/OC 相关主要集中在 `/v2/oc/*` 与 `/v3/make_oc_image_ref`。
- 上传依赖 `/v1/oss/sts-upload-token` 与 `/v1/oss/anonymous-upload-token`。
- LLM/Dify 相关接口为 `/v3/gpt/dify/*`。
- 前端使用 `nieta/apiConfig` 统一配置请求头与 endpoint，默认带 `x-platform`、`x-nieta-app-version`、`x-teen-mode` 等头。