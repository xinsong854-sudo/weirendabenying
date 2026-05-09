# 个人主页后端（端口 3000）

这个后端负责：

- 托管 `/workspace/my-page/index.html`
- 计数器与笔记数据持久化
- 通过后端代理调用 OpenAI-compatible LLM，避免前端暴露密钥
- 使用用户自己的 Neta Token 读取角色分享资料，并生成 CoC 7版车卡

## 启动

```bash
cd /workspace/backend
npm install
npm start
```

也可以使用启动脚本：

```bash
./start.sh
```

默认地址：

```text
http://localhost:3000
```

## 环境变量

复制示例配置：

```bash
cp .env.example .env
```

然后填写：

```env
PORT=3000
LLM_URL=https://litellm.talesofai.cn/v1/chat/completions
LLM_API_KEY=sk-你的key
LLM_MODEL=qwen3.5-plus-no-think
NETA_API_BASE_URL=https://api.talesofai.cn
```

如果没有 `backend/.env`，服务会尝试复用 `../dtags-backend/.env` 里的 LLM 配置。

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/data` | 获取计数器和笔记 |
| GET | `/api/notes` | 获取笔记列表 |
| POST | `/api/counter` | 更新计数器 |
| POST | `/api/notes` | 添加笔记 |
| DELETE | `/api/notes/:id` | 删除笔记 |
| GET | `/api/config` | 查看 LLM 配置状态 |
| POST | `/api/chat` | 后端 LLM 聊天代理 |
| POST | `/api/neta/character-profile` | 用用户 Neta Token 读取角色资料 |
| POST | `/api/coc/character-card` | 读取 Neta 角色并生成 CoC 车卡 |

## 测试

```bash
curl http://localhost:3000/api/config

curl -X POST http://localhost:3000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"你好"}]}'
```
