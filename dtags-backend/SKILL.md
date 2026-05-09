---
name: dtags-llm
description: Danbooru 标签匹配网站的 LLM API 配置
---

# DTags LLM API 配置

## 端点信息

- **URL**: `https://litellm.talesofai.cn/v1/chat/completions`
- **Key**: `sk-fZrLXE0IEs6EDYJCOsLLaQ`
- **模型**: `qwen3.5-plus-no-think`
- **思考模型**: `qwen3.5-plus`

## 使用方法

```javascript
const LLM_URL = 'https://litellm.talesofai.cn/v1/chat/completions';
const LLM_KEY = 'sk-fZrLXE0IEs6EDYJCOsLLaQ';
const LLM_MODEL = 'qwen3.5-plus-no-think';
```

## 所属网站

- **项目**: DTags - Danbooru 标签智能匹配
- **前端**: `/workspace/dtags-frontend/index.html`
- **后端**: `/workspace/dtags-backend/`
- **后端端口**: 3002

## 安全说明

- Key 由用户 `claw-annuonie` 提供
- 仅用于 DTags 项目
- 后端通过 `.env` 文件加载，前端不暴露
