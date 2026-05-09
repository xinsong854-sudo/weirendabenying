#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ -f .env ]; then
  echo "✅ 加载 backend/.env..."
  set -a
  source .env
  set +a
elif [ -f ../dtags-backend/.env ]; then
  echo "✅ 未找到 backend/.env，复用 dtags-backend/.env 的 LLM 配置..."
  set -a
  source ../dtags-backend/.env
  set +a
fi

export PORT=${PORT:-3000}
export LLM_URL=${LLM_URL:-"https://litellm.talesofai.cn/v1/chat/completions"}
export LLM_MODEL=${LLM_MODEL:-"qwen3.5-plus-no-think"}

if [ -z "$LLM_API_KEY" ]; then
  echo "⚠️  未配置 LLM_API_KEY，AI 聊天接口将返回 503。"
  echo "   请复制 .env.example 为 .env 后填入密钥。"
fi

echo "🚀 启动个人主页后端: http://localhost:$PORT"
echo "🤖 LLM 模型: $LLM_MODEL"
node server.js
