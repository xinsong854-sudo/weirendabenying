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

// 兼容本地 .env、父级 .env，以及已有 dtags-backend 的 LLM 配置
loadEnvFile(path.join(__dirname, '.env'));
loadEnvFile(path.join(__dirname, '../.env'));
loadEnvFile(path.join(__dirname, '../dtags-backend/.env'));

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'data.json');
const PUBLIC_DIR = path.join(__dirname, '../my-page');

const LLM_URL = process.env.LLM_URL || 'https://litellm.talesofai.cn/v1/chat/completions';
const LLM_API_KEY = process.env.LLM_API_KEY || '';
const LLM_MODEL = process.env.LLM_MODEL || 'qwen3.5-plus-no-think';
const NETA_API_BASE_URL = process.env.NETA_API_BASE_URL || 'https://api.talesofai.cn';

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

function parseLooseJSON(raw) {
    if (!raw) return null;
    try { return JSON.parse(raw); } catch(e) {}
    try { return JSON.parse(raw.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim()); } catch(e) {}
    try {
        const m = raw.match(/\{[\s\S]*\}/);
        return m ? JSON.parse(m[0]) : null;
    } catch(e) {}
    return null;
}

function extractUuid(input) {
    const text = String(input || '').trim();
    const uuidMatch = text.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);
    if (uuidMatch) return uuidMatch[0];

    try {
        const url = new URL(text);
        for (const key of ['uuid', 'tcp_uuid', 'parent_uuid', 'id']) {
            const value = url.searchParams.get(key);
            if (value && /^[0-9a-f-]{32,36}$/i.test(value)) return value;
        }
    } catch(e) {}

    return null;
}

function keywordFromLink(input) {
    const text = String(input || '').trim();
    try {
        const url = new URL(text);
        const parts = url.pathname.split('/').filter(Boolean);
        return decodeURIComponent(parts[parts.length - 1] || text).replace(/[-_]+/g, ' ').trim();
    } catch(e) {
        return text;
    }
}

function normalizeNetaCharacterProfile(tcp) {
    const bio = tcp?.oc_bio || {};
    const config = tcp?.config || {};
    return {
        type: tcp?.type === 'elementum' ? 'elementum' : 'character',
        uuid: tcp?.uuid,
        name: tcp?.name || bio.name || '',
        gender: tcp?.gender || bio.gender || '',
        age: bio.age || '',
        occupation: bio.occupation || '',
        interests: bio.interests || '',
        persona: bio.persona || '',
        description: bio.description || '',
        avatar_img: config.avatar_img || '',
        header_img: config.header_img || '',
        hashtags: tcp?.hashtags || [],
        accessibility: tcp?.accessibility || '',
        status: tcp?.status || ''
    };
}

async function fetchNetaCharacterProfile(userToken, input) {
    if (!userToken) throw new Error('请提供用户 Neta Token');
    if (!input) throw new Error('请提供角色链接、UUID 或角色名');

    const headers = { 'Authorization': `Bearer ${userToken}` };
    let uuid = extractUuid(input);

    if (!uuid) {
        const keywords = keywordFromLink(input);
        const params = new URLSearchParams({
            keywords,
            page_index: '0',
            page_size: '1',
            parent_type: 'oc',
            sort_scheme: 'exact'
        });
        const searchRes = await fetch(`${NETA_API_BASE_URL}/v2/travel/parent-search?${params.toString()}`, { headers });
        const searchData = await searchRes.json().catch(() => ({}));
        if (!searchRes.ok) throw new Error(searchData?.message || searchData?.error || `搜索角色失败 (${searchRes.status})`);
        uuid = searchData?.list?.[0]?.uuid;
        if (!uuid) throw new Error('没有找到对应角色，请确认链接/名称是否正确或角色是否可访问');
    }

    const profileRes = await fetch(`${NETA_API_BASE_URL}/v2/travel/parent/${uuid}/profile`, { headers });
    const profileData = await profileRes.json().catch(() => ({}));
    if (!profileRes.ok) throw new Error(profileData?.message || profileData?.error || `读取角色详情失败 (${profileRes.status})`);
    if (!profileData) throw new Error('角色详情为空');

    return normalizeNetaCharacterProfile(profileData);
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

// 配置查询：方便前端判断是否启用了后端 LLM
app.get('/api/config', (req, res) => {
    res.json({
        llm_enabled: Boolean(LLM_API_KEY),
        llm_model: LLM_MODEL,
        llm_url: LLM_URL,
        chat_mode: 'server-llm'
    });
});

// Neta 角色详情读取：使用用户自己的 Neta Token，不在后端保存
app.post('/api/neta/character-profile', async (req, res) => {
    const { token, link, uuid, name } = req.body || {};
    try {
        const profile = await fetchNetaCharacterProfile(token, link || uuid || name);
        res.json({ success: true, profile });
    } catch (error) {
        console.error('Neta character profile error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// 生成 CoC 跑团车卡：Neta 角色简介 + 图片 + LLM 无思考模式
app.post('/api/coc/character-card', async (req, res) => {
    const { token, link, uuid, name, profile: providedProfile, coc_version = 'CoC 7th', locale = 'zh-CN' } = req.body || {};

    try {
        if (!LLM_API_KEY) {
            return res.status(503).json({ success: false, error: '后端未配置 LLM_API_KEY' });
        }

        const profile = providedProfile || await fetchNetaCharacterProfile(token, link || uuid || name);
        const systemPrompt = `你是专业的克苏鲁的呼唤 ${coc_version} 守秘人与调查员车卡设计师。只输出 JSON，不要输出思考过程、Markdown 或解释。`;
        const userPrompt = `根据下方 Neta 角色资料，生成一张适合 ${coc_version} 跑团使用的调查员车卡。

要求：
1. 使用无思考、直接生成模式。
2. 保留角色图片信息：avatar_img/header_img。
3. 数值要符合 CoC 7版常见范围：属性一般 15-90，技能 0-90，SAN/HP/MP/DB/Build 合理。
4. 不要逐字照搬简介，要把角色转译为跑团可用人物。
5. 若资料不足，合理补全但不要过度夸张。
6. 输出必须是可解析 JSON。

返回 JSON 结构：
{
  "source_character": {
    "uuid": "",
    "name": "",
    "avatar_img": "",
    "header_img": ""
  },
  "investigator": {
    "name": "",
    "age": "",
    "gender": "",
    "occupation": "",
    "residence": "",
    "birthplace": "",
    "era": "现代/近代/维多利亚等"
  },
  "portrait": {
    "avatar_img": "",
    "header_img": "",
    "visual_summary": ""
  },
  "attributes": {
    "STR": 0, "CON": 0, "SIZ": 0, "DEX": 0, "APP": 0,
    "INT": 0, "POW": 0, "EDU": 0, "LUCK": 0
  },
  "derived": {
    "SAN": 0,
    "HP": 0,
    "MP": 0,
    "MOV": 0,
    "damage_bonus": "",
    "build": 0
  },
  "skills": [
    {"name":"", "value":0, "reason":""}
  ],
  "backstory": {
    "personal_description": "",
    "ideology_beliefs": "",
    "significant_people": "",
    "meaningful_locations": "",
    "treasured_possessions": "",
    "traits": "",
    "injuries_scars": "",
    "phobias_manias": "",
    "arcane_tomes_spells_artifacts": "",
    "encounters_with_strange_entities": ""
  },
  "equipment": [""],
  "cash_assets": "",
  "roleplay_notes": "",
  "keeper_notes": ""
}

Neta 角色资料：
${JSON.stringify(profile, null, 2)}

输出语言：${locale}`;

        const { reply } = await callOpenAICompatibleChat({
            url: LLM_URL,
            apiKey: LLM_API_KEY,
            model: LLM_MODEL,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
            ],
            max_tokens: 4096,
            temperature: 0.35
        });

        const card = parseLooseJSON(reply);
        if (!card) {
            return res.status(502).json({ success: false, error: 'LLM 返回内容不是有效 JSON', raw: reply });
        }

        res.json({ success: true, profile, card });
    } catch (error) {
        console.error('CoC character card error:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// LLM 聊天代理
app.post('/api/chat', async (req, res) => {
    const { messages, model = LLM_MODEL, max_tokens, temperature } = req.body;

    if (!Array.isArray(messages) || messages.length === 0) {
        return res.status(400).json({ error: '请提供 messages 数组' });
    }

    try {
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

        res.json({
            reply,
            mode: 'server-llm',
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
});
