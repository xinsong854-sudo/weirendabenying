# LLM 后端验证指南

本仓库现在有两套后端，都已改为“前端不暴露 LLM Key，统一由后端代理调用 LLM”。

## 1. 个人主页后端（端口 3000）

路径：`/workspace/backend`

启动：

```bash
cd /workspace/backend
npm install
npm start
# 或 ./start.sh
```

验证配置：

```bash
curl http://localhost:3000/api/config
```

验证聊天：

```bash
curl -X POST http://localhost:3000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"用一句话介绍你自己"}]}'
```

访问页面：

```text
http://localhost:3000
```

## 2. DTags 后端（端口 3002）

路径：`/workspace/dtags-backend`

启动：

```bash
cd /workspace/dtags-backend
npm install
npm start
# 或 ./start.sh
```

验证配置：

```bash
curl http://localhost:3002/api/config
```

验证聊天代理：

```bash
curl -X POST http://localhost:3002/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"返回 JSON：{\"ok\":true}"}]}'
```

验证标签匹配：

```bash
curl -X POST http://localhost:3002/api/match \
  -H 'Content-Type: application/json' \
  -d '{"query":"银发蓝眼的动漫女孩"}'
```

访问 DTags 页面：

```text
http://localhost:3002
```

## 环境变量

推荐在对应后端目录放 `.env`：

```env
LLM_URL=https://litellm.talesofai.cn/v1/chat/completions
LLM_API_KEY=sk-你的key
LLM_MODEL=qwen3.5-plus-no-think
```

`/workspace/backend` 如果没有自己的 `.env`，会尝试复用 `/workspace/dtags-backend/.env`。
