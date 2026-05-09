const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');

function loadEnvFile(filePath) {
    if (!fs.existsSync(filePath)) return;

    const content = fs.readFileSync(filePath, 'utf8');
    content.split(/\r?\n/).forEach(line => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) return;

        const eqIndex = trimmed.indexOf('=');
        if (eqIndex === -1) return;

        const key = trimmed.slice(0, eqIndex).trim();
        let value = trimmed.slice(eqIndex + 1).trim();

        if (!key || process.env[key] !== undefined) return;

        if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
            value = value.slice(1, -1);
        }

        process.env[key] = value;
    });
}

// 兼容本地 .env 和父级 .env
loadEnvFile(path.join(__dirname, '.env'));
loadEnvFile(path.join(__dirname, '../.env'));

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data.json');
const PUBLIC_DIR = path.join(__dirname, '../my-page');

const LLM_URL = process.env.LLM_URL || 'https://litellm.talesofai.cn/v1/chat/completions';
const LLM_API_KEY = process.env.LLM_API_KEY || '';
const LLM_MODEL = process.env.LLM_MODEL || 'qwen3.5-plus-no-think';
const NETA_CHAT_URL = process.env.NETA_CHAT_URL || 'https://neta.art/api/v1/chat/completions';

app.use(cors());
app.use(express.json({ limit: '5mb' }));

// 静态文件服务（前端页面）
app.use(express.static(PUBLIC_DIR));
app.get('/', (req, res) => res.sendFile(path.join(PUBLIC_DIR, 'index.html')));

// 初始化数据文件
function loadData() {
    if (fs.existsSync(DATA_FILE)) {
        return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
    }
    return { counter: 0, notes: [] };
}

function saveData(data) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

async function callOpenAICompatibleChat({ url, apiKey, model, messages, max_tokens, temperature }) {
    const payload = { model, messages };
    if (typeof max_tokens === 'number') payload.max_tokens = max_tokens;
    if (typeof temperature === 'number') payload.temperature = temperature;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {})
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const message = data?.error?.message || data?.error || data?.message || `请求失败 (${response.status})`;
        throw new Error(message);
    }

    const reply = data?.choices?.[0]?.message?.content ?? data?.reply ?? data?.output_text ?? '';
    return { data, reply };
}

// 获取所有数据
app.get('/api/data', (req, res) => {
    const data = loadData();
    res.json(data);
});

// 更新计数器
app.post('/api/counter', (req, res) => {
    const data = loadData();
    const { action, value } = req.body;

    if (action === 'set') {
        data.counter = Number(value) || 0;
    } else if (action === 'add') {
        data.counter += Number(value) || 1;
    } else if (action === 'subtract') {
        data.counter -= Number(value) || 1;
    }

    saveData(data);
    res.json({ counter: data.counter });
});

// 添加笔记
app.post('/api/notes', (req, res) => {
    const { text } = req.body;
    if (!text || typeof text !== 'string') {
        return res.status(400).json({ error: '请提供文本内容' });
    }

    const data = loadData();
    data.notes.unshift({ id: Date.now(), text: text.trim(), createdAt: new Date().toISOString() });
    saveData(data);
    res.json({ notes: data.notes });
});

// 删除笔记
app.delete('/api/notes/:id', (req, res) => {
    const data = loadData();
    data.notes = data.notes.filter(note => note.id !== Number(req.params.id));
    saveData(data);
    res.json({ notes: data.notes });
});

// 获取笔记列表
app.get('/api/notes', (req, res) => {
    const data = loadData();
    res.json({ notes: data.notes });
});

// Token 自动刷新
app.post('/api/refresh-token', async (req, res) => {
    const { client_id, client_secret } = req.body;
    if (!client_id || !client_secret) {
        return res.status(400).json({ error: '需要提供 client_id 和 client_secret' });
    }
    try {
        const response = await fetch('https://neta.art/oauth/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                grant_type: 'client_credentials',
                client_id: client_id,
                client_secret: client_secret
            })
        });
        const data = await response.json();
        if (!response.ok) {
            return res.status(response.status).json({ error: data.error || '刷新失败' });
        }
        res.json({ access_token: data.access_token, expires_in: data.expires_in });
    } catch (error) {
        console.error('Token refresh error:', error);
        res.status(500).json({ error: '刷新失败: ' + error.message });
    }
});

// 配置查询：方便前端判断是否启用了后端 LLM
app.get('/api/config', (req, res) => {
    res.json({
        llm_enabled: Boolean(LLM_API_KEY),
        llm_model: LLM_MODEL,
        llm_url: LLM_URL,
        chat_mode: LLM_API_KEY ? 'server-llm' : 'token-proxy'
    });
});

// LLM 聊天代理
app.post('/api/chat', async (req, res) => {
    const { token, messages, model = LLM_MODEL, max_tokens, temperature, mode } = req.body;

    if (!Array.isArray(messages) || messages.length === 0) {
        return res.status(400).json({ error: '请提供 messages 数组' });
    }

    try {
        const wantServerLLM = mode === 'llm' || (mode !== 'neta' && Boolean(LLM_API_KEY));

        if (wantServerLLM) {
            if (!LLM_API_KEY) {
                return res.status(503).json({ error: '后端未配置 LLM_API_KEY' });
            }

            const { reply } = await callOpenAICompatibleChat({
                url: LLM_URL,
                apiKey: LLM_API_KEY,
                model,
                messages,
                max_tokens,
                temperature
            });

            return res.json({
                reply,
                mode: 'server-llm',
                model
            });
        }

        if (!token) {
            return res.status(401).json({ error: '请提供 neta.art Access Token' });
        }

        const { reply } = await callOpenAICompatibleChat({
            url: NETA_CHAT_URL,
            apiKey: token,
            model,
            messages,
            max_tokens,
            temperature
        });

        res.json({
            reply,
            mode: 'neta-token',
            model
        });
    } catch (error) {
        console.error('LLM Error:', error);
        res.status(500).json({ error: '后端调用 LLM 失败: ' + error.message });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Backend running on http://localhost:${PORT}`);
    console.log(`📝 API endpoints:`);
    console.log(`   GET    /api/data      - 获取所有数据`);
    console.log(`   GET    /api/notes     - 获取笔记列表`);
    console.log(`   GET    /api/config    - LLM 配置状态`);
    console.log(`   POST   /api/counter   - 更新计数器`);
    console.log(`   POST   /api/notes     - 添加笔记`);
    console.log(`   DELETE /api/notes/:id - 删除笔记`);
    console.log(`   POST   /api/chat      - LLM 聊天代理`);
    console.log(`   POST   /api/refresh-token - 刷新 neta.art Token`);
});
