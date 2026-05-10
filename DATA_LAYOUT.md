# 数据与目录整理规范

> 目标：以后数据变多时，能快速判断“该放哪、该不该提交、如何备份”。

## 1. 运行数据

### `pages/pseudo_human.db`

当前 3000 后端使用的 SQLite 主库。它是站内运行数据，不是缓存。

按表分类：

| 分类 | 表 | 说明 |
| --- | --- | --- |
| 成员资料 | `members` | 用户昵称、头像、权限、称号、头像框、签名、感悟、本真余额等站内资料 |
| 论坛内容 | `forum_posts`, `forum_channels` | 频道和帖子 |
| Wiki / 评论 | `entries`, `wiki_submissions`, `comments` | Wiki 数据、投稿审核、词条评论 |
| 身份卡 | `identity_cards` | 用户主动保存的角色/CoC 身份卡 |
| 经济/成长 | `currency_events`, `purchases`, `exp_events` | 本真流水、购买记录、感悟事件 |
| 悬赏/探索 | `bounty_tasks`, `bounty_submissions`, `explore_runs` | 每日悬赏、提交、里界探索记录 |
| 私聊 | `private_messages` | 站内私聊消息 |
| 兼容旧表 | `users` | 旧版/兼容数据 |

注意：数据库不应保存手机号、验证码、Token、IP、设备指纹。

### 数据库备份建议

不要随手复制到根目录。统一放到未跟踪的本地目录：

```txt
runtime/backups/db/YYYY-MM-DD/pseudo_human.db
```

该目录默认不提交 Git。需要迁移时再单独打包。

## 2. 静态种子数据

### `pages/pseudo-human-data.json`

前端内置 Wiki/档案种子数据。适合放：

- 初始世界观词条
- 默认展示用档案
- 可公开的静态资料

不适合放：

- 用户运行时发帖
- 私聊
- Token / 手机号 / 验证码
- 临时接口返回缓存

## 3. 前端源码与构建产物

| 路径 | 是否提交 | 说明 |
| --- | --- | --- |
| `pages/vue-app/src/` | 是 | Vue 前端源码 |
| `pages/vue-app/package.json` / `package-lock.json` | 是 | 依赖声明和锁定版本 |
| `pages/vue-app/node_modules/` | 否 | 本地依赖，可 `npm ci` 重装 |
| `pages/dist/` | 是 | GitHub Pages / 后端静态服务使用的构建产物 |

## 4. 后端源码与依赖

| 路径 | 是否提交 | 说明 |
| --- | --- | --- |
| `pages/server.py` | 是 | 当前 3000 后端主服务 |
| `backend/`, `dtags-backend/` | 视项目需要 | 旧/辅助项目源码 |
| `*/node_modules/` | 否 | 依赖目录不再提交，使用 lockfile 恢复 |

## 5. 临时目录与缓存

以下内容默认不提交：

```txt
node_modules/
__pycache__/
*.pyc
.pytest_cache/
.vite/
runtime/
tmp/
*.db-wal
*.db-shm
*.bak
```

如果临时目录里出现需要长期保留的资料，请移到明确分类目录，例如：

```txt
notes/               # 文字笔记
pages/vue-app/src/   # 前端源码
pages/               # 当前伪人大本营后端和数据
skills/              # 可复用技能说明
```

## 6. 清理原则

1. 依赖目录不提交，只提交 `package.json` / `package-lock.json`。
2. 运行缓存不提交。
3. 用户数据只进入数据库，不散落到根目录。
4. 大文件先判断是否是运行必需；不是就放 `runtime/` 或外部备份。
5. GitHub 和 Cohub 的 `main` 保持同一套源码历史；不要再单独维护根目录 Pages 分支作为主线。
