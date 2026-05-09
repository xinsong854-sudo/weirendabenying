#!/bin/bash

# =============================================================================
# DTags Backend 启动脚本
# =============================================================================

# 设置环境变量（从 .env 文件读取，如果不存在则使用默认值）
if [ -f .env ]; then
    echo "✅ 加载 .env 文件..."
    export $(grep -v '^#' .env | xargs)
fi

# 必需的配置检查
if [ -z "$LLM_API_KEY" ]; then
    echo "❌ 错误：未设置 LLM_API_KEY 环境变量！"
    echo ""
    echo "请在 .env 文件中添加："
    echo "  LLM_API_KEY=YOUR_LLM_API_KEY"
    echo ""
    echo "或直接运行："
    echo "  export LLM_API_KEY=YOUR_LLM_API_KEY"
    exit 1
fi

# 设置默认值
export LLM_URL=${LLM_URL:-"https://litellm.talesofai.cn/v1/chat/completions"}
export LLM_MODEL=${LLM_MODEL:-"qwen3.5-plus-no-think"}
export LLM_THINKING_MODEL=${LLM_THINKING_MODEL:-"qwen3.5-plus"}

# 安全配置（可选）
export DTAGS_API_KEY=${DTAGS_API_KEY:-""}
export RATE_LIMIT=${RATE_LIMIT:-"20"}
export RATE_LIMIT_HOUR=${RATE_LIMIT_HOUR:-"100"}
export ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-"http://localhost:3000,http://localhost:8080"}

# 打印配置信息（隐藏 API Key 的大部分）
echo ""
echo "🚀 启动 DTags Backend..."
echo ""
echo "📡 LLM 配置："
echo "  URL: $LLM_URL"
echo "  Key: ${LLM_API_KEY:0:10}...${LLM_API_KEY: -4}"
echo "  默认模型: $LLM_MODEL"
echo "  思考模型: $LLM_THINKING_MODEL"
echo ""
echo "🔒 安全配置："
echo "  频率限制: $RATE_LIMIT 次/分钟, $RATE_LIMIT_HOUR 次/小时"
echo "  API Key 验证: $([ -z "$DTAGS_API_KEY" ] && echo "禁用" || echo "启用")"
echo ""

# 启动服务
node server.js
