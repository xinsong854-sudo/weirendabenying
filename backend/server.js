const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const DATA_FILE = path.join(__dirname, 'data.json');
const PUBLIC_DIR = path.join(__dirname, '../my-page');

app.use(cors());
app.use(express.json());

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

// LLM 聊天代理
app.post('/api/chat', async (req, res) => {
    const { token, messages, model = 'gpt-4o-mini' } = req.body;

    if (!token) {
        return res.status(401).json({ error: '请提供 neta.art Access Token' });
    }

    try {
        const response = await fetch('https://neta.art/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                model: model,
                messages: messages
            })
        });

        const data = await response.json();

        if (!response.ok) {
            return res.status(response.status).json({ error: data.error || '请求失败' });
        }

        res.json({ reply: data.choices[0].message.content });
    } catch (error) {
        console.error('LLM Error:', error);
        res.status(500).json({ error: '后端调用 LLM 失败: ' + error.message });
    }
});

app.listen(PORT, () => {
    console.log(`🚀 Backend running on http://localhost:${PORT}`);
    console.log(`📝 API endpoints:`);
    console.log(`   GET    /api/data     - 获取所有数据`);
    console.log(`   GET    /api/notes    - 获取笔记列表`);
    console.log(`   POST   /api/counter  - 更新计数器`);
    console.log(`   POST   /api/notes    - 添加笔记`);
    console.log(`   DELETE /api/notes/:id - 删除笔记`);
});
