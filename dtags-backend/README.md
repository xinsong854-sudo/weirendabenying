# DTags Backend

Danbooru 标签智能匹配后端服务

## 功能

- 🤖 **智能匹配**: 使用 LLM 分析中文描述，匹配 Danbooru 标签
- ⚡ **快速匹配**: 本地标签数据库快速搜索
- 🔬 **标签诊断**: 分析已有标签，提供优化建议
- 🌐 **标签翻译**: 中英互译
- 📊 **数量统计**: 统计标签数量
- 💾 **智能缓存**: 缓存 LLM 响应，减少重复调用

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/config` | LLM 配置状态 |
| POST | `/api/chat` | OpenAI-compatible 聊天代理 |
| POST | `/api/match` | 智能标签匹配（LLM） |
| POST | `/api/analyze` | 标签智能诊断 |

## 启动

```bash
npm install
npm start
```

服务运行在 http://localhost:3002

## 环境变量

```bash
LLM_URL=https://litellm.talesofai.cn/v1/chat/completions
LLM_API_KEY=YOUR_LLM_API_KEY
LLM_MODEL=qwen3.5-plus-no-think
```

## 请求示例

### 智能匹配

```bash
curl -X POST http://localhost:3002/api/match \
  -H "Content-Type: application/json" \
  -d '{"query": "银发蓝眼的动漫女孩"}'
```

响应：
```json
{
  "success": true,
  "query": "银发蓝眼的动漫女孩",
  "intent": {
    "type": "character",
    "keys": ["silver", "blue", "hair"]
  },
  "tags": [
    {"name": "silver_hair", "zh": "银发", "source": "database", "reason": "..."},
    {"name": "blue_eyes", "zh": "蓝眼", "source": "database", "reason": "..."}
  ],
  "explanation": "根据描述匹配了银发、蓝眼等特征标签"
}
```

### 标签诊断

```bash
curl -X POST http://localhost:3002/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"tags": ["1girl", "solo", "long_hair"]}'
```
