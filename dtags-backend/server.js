require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3002;
const LLM_URL = process.env.LLM_URL || 'https://litellm.talesofai.cn/v1/chat/completions';
const LLM_KEY = process.env.LLM_API_KEY || '';
const MODEL = 'qwen3.5-plus-no-think';

const D_CACHE = path.join(__dirname, 'd_cache');
const PUBLIC_DIR = path.join(__dirname, 'public');
if (!fs.existsSync(D_CACHE)) fs.mkdirSync(D_CACHE, { recursive: true });
if (!fs.existsSync(PUBLIC_DIR)) fs.mkdirSync(PUBLIC_DIR, { recursive: true });

app.use(cors({ origin: true }));
app.use(express.json({ limit: '5mb' }));
app.use(express.static(PUBLIC_DIR));

// Danbooru 搜索（修复：使用正确的前缀匹配）
async function dSearch(q, limit) {
    const key = 'd_' + q.replace(/[^a-z0-9]/gi, '_');
    const p = path.join(D_CACHE, key + '.json');
    if (fs.existsSync(p)) {
        const c = JSON.parse(fs.readFileSync(p, 'utf8'));
        if (Date.now() - c.t < 86400000) return c.data;
    }
    try {
        // 使用 *q* 模糊匹配，然后过滤
        const url = `https://danbooru.donmai.us/tags.json?search[name_matches]=${encodeURIComponent(q)}*&limit=${limit || 30}`;
        const r = await axios.get(url, { timeout: 6000 });
        if (!r.data || !Array.isArray(r.data)) return { q, tags: [], t: Date.now() };
        
        const clean = r.data
            .filter(t => t.category === 0) // 只要 general
            .filter(t => t.post_count >= 10) // 至少 10 帖
            .map(t => ({ name: t.name, post_count: t.post_count }));
            
        const res = { q, tags: clean.slice(0, 30), t: Date.now() };
        fs.writeFileSync(p, JSON.stringify(res));
        return res;
    } catch(e) { 
        console.error('Danbooru search error:', e.message);
        return { q, tags: [], t: Date.now() }; 
    }
}

async function dMulti(keys, perKey) {
    const all = [];
    const promises = keys.slice(0, 5).map(async k => {
        try { 
            const r = await dSearch(k, perKey); 
            all.push(...r.tags); 
        } catch(e) {}
    });
    await Promise.all(promises);
    
    const uniq = new Map();
    all.forEach(t => { 
        if (!uniq.has(t.name)) uniq.set(t.name, t); 
    });
    return Array.from(uniq.values())
        .sort((a, b) => b.post_count - a.post_count)
        .slice(0, 60);
}

// 角色拆解
async function charBreakdown(name) {
    try {
        const cr = await axios.get(`https://danbooru.donmai.us/tags.json?search[name_matches]=${encodeURIComponent(name)}&limit=3`, { timeout: 5000 });
        if (!cr.data || !cr.data.length) return null;
        
        const raw = await callLLM([
            { role: 'system', content: '只返回 JSON' },
            { role: 'user', content: `拆解 Danbooru 角色 "${name}" 的特征标签（hair/eyes/outfit/acc/style），每类 2-3 个，共 10-15 个。不要构图/背景/姿势。\n返回：{"tags":[{"name":"","zh":"","cat":"","reason":""}],"explanation":"说明"}` }
        ], 1024, 0.2);
        
        const d = parseJSON(raw);
        if (!d || !Array.isArray(d.tags) || d.tags.length === 0) return null;
        d.tags.forEach(t => { t.source = 'danbooru'; t.cat = t.cat || ''; t.reason = t.reason || ''; });
        return d;
    } catch(e) { return null; }
}

async function callLLM(msgs, maxT, temp) {
    const r = await axios.post(LLM_URL, {
        model: MODEL, messages: msgs, max_tokens: maxT || 512, temperature: temp ?? 0.2
    }, { 
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + LLM_KEY }, 
        timeout: 25000 
    });
    return (r.data?.choices?.[0]?.message?.content) || '';
}

function parseJSON(raw) {
    if (!raw) return null;
    try { return JSON.parse(raw); } catch(e) {}
    try { return JSON.parse(raw.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim()); } catch(e) {}
    try { 
        const m = raw.match(/\{[\s\S]*\}/); 
        return m ? JSON.parse(m[0]) : null; 
    } catch(e) {}
    return null;
}

app.get('/api/health', (req, res) => res.json({ ok: true }));

app.post('/api/match', async (req, res) => {
    const q = req.body?.query;
    if (!q) return res.status(400).json({ error: '请提供查询文本' });
    const t0 = Date.now();

    try {
        // 本地规则判断类型
        const charNames = ['初音未来','镜音铃','镜音连','巡音流歌','洛天依','言和','乐正绫','东方','原神','崩铁','鸣潮','赛马娘','偶像大师','hololive','hatsune miku','miku','ganyu','raiden','hu tao','zhongli','nahida','furina','vocaloid','vtuber'];
        const isChar = charNames.some(n => q.toLowerCase().includes(n.toLowerCase()));
        const isPrecise = q.length <= 8 && (q.includes('发') || q.includes('眼') || q.includes('瞳') || q.includes('色'));
        
        let intentType = 'vague';
        if (isChar) intentType = 'character';
        else if (isPrecise) intentType = 'precise';

        // 提取关键词（手动拆分 + LLM 辅助）
        let keys = [];
        
        // 简单拆分中文词
        if (q.includes('银发')) keys.push('silver');
        if (q.includes('白发')) keys.push('white');
        if (q.includes('黑发')) keys.push('black');
        if (q.includes('金发')) keys.push('blonde');
        if (q.includes('红发')) keys.push('red');
        if (q.includes('蓝发')) keys.push('blue');
        if (q.includes('粉发')) keys.push('pink');
        if (q.includes('紫发')) keys.push('purple');
        if (q.includes('绿发')) keys.push('green');
        if (q.includes('棕发')) keys.push('brown');
        if (q.includes('灰发')) keys.push('grey');
        if (q.includes('发')) { if (!keys.includes('hair')) keys.push('hair'); }
        
        if (q.includes('蓝眼') || q.includes('蓝瞳')) keys.push('blue');
        if (q.includes('红眼') || q.includes('红瞳')) keys.push('red');
        if (q.includes('绿眼') || q.includes('绿瞳')) keys.push('green');
        if (q.includes('紫眼') || q.includes('紫瞳')) keys.push('purple');
        if (q.includes('黄眼') || q.includes('金眼')) keys.push('yellow');
        if (q.includes('黑眼') || q.includes('黑瞳')) keys.push('black');
        if (q.includes('眼') || q.includes('瞳')) { if (!keys.includes('eyes')) keys.push('eyes'); }
        
        if (q.includes('猫')) keys.push('cat');
        if (q.includes('耳')) keys.push('ears');
        if (q.includes('尾')) keys.push('tail');
        if (q.includes('翼') || q.includes('翅膀')) keys.push('wings');
        if (q.includes('赛博')) keys.push('cyber');
        if (q.includes('朋克')) keys.push('punk');
        if (q.includes('机械')) keys.push('mecha');
        if (q.includes('霓虹')) keys.push('neon');
        if (q.includes('女仆')) keys.push('maid');
        if (q.includes('和服')) keys.push('kimono');
        if (q.includes('校服')) keys.push('school');
        if (q.includes('精灵')) keys.push('elf');
        if (q.includes('恶魔')) keys.push('demon');
        if (q.includes('天使')) keys.push('angel');
        if (q.includes('龙')) keys.push('dragon');
        if (q.includes('狐')) keys.push('fox');
        
        // LLM 补充
        if (keys.length < 2) {
            try {
                const raw = await callLLM([
                    { role: 'system', content: '只返回 JSON 数组' },
                    { role: 'user', content: `提取描述中的英文基础词（单个词，不要下划线）：\n"${q}"\n返回：["词 1","词 2","词 3"]` }
                ], 128, 0.1);
                const m = raw.match(/\[[\s\S]*\]/);
                if (m) {
                    const arr = JSON.parse(m[0]);
                    arr.forEach(k => {
                        if (typeof k === 'string' && !k.includes('_') && k.length > 1 && !keys.includes(k)) {
                            keys.push(k);
                        }
                    });
                }
            } catch(e) {}
        }
        
        if (keys.length === 0) keys = [q.replace(/[^a-zA-Z]/g, '')];
        if (keys.length === 0) keys = [q];
        keys = keys.slice(0, 5);

        const intent = { type: intentType, keys };
        console.log(`📋 [${intentType}] keys: ${keys.join(', ')}`);

        // 角色名分流
        if (intentType === 'character' && keys.length > 0) {
            console.log('🎭 角色:', keys[0]);
            const cd = await charBreakdown(keys[0]);
            if (cd) {
                return res.json({ success: true, query: q, intent, ...cd, duration_ms: Date.now() - t0 });
            }
        }

        // Danbooru 搜索
        const perKey = intentType === 'precise' ? 10 : 15;
        const dTags = await dMulti(keys, perKey);
        console.log(`✅ ${dTags.length} tags`);

        // LLM 匹配
        if (dTags.length === 0) {
            return res.json({ 
                success: true, 
                query: q, 
                intent, 
                tags: [], 
                explanation: '未在 Danbooru 词库中找到匹配标签，请尝试其他描述。', 
                duration_ms: Date.now() - t0 
            });
        }

        const tagsText = dTags.slice(0, 80).map(t => `- ${t.name} (${t.post_count})`).join('\n');
        const rules = intentType === 'precise'
            ? `精准描述：只返回 3-8 个最直接的核心标签。严禁添加构图/背景/姿势/风格标签。`
            : `开放描述：可返回 10-20 个。允许组合词、拟人类型、艺术风格。大胆发挥。`;

        const matchRaw = await callLLM([
            { role: 'system', content: '只返回 JSON' },
            { role: 'user', content: `Danbooru 标签专家。描述："${q}"\n${rules}\n词库：\n${tagsText}\n返回：{"tags":[{"name":"","zh":"","source":"danbooru","reason":""}],"explanation":""}` }
        ], 768, 0.2);

        const parsed = parseJSON(matchRaw);
        const tags = (parsed && Array.isArray(parsed.tags)) ? parsed.tags : [];
        const explanation = (parsed && parsed.explanation) ? parsed.explanation : '';

        console.log(`📦 ${tags.length} tags`);
        res.json({ success: true, query: q, intent, tags, explanation, duration_ms: Date.now() - t0 });
    } catch (err) {
        console.error('Error:', err.message);
        res.status(500).json({ success: false, error: err.message });
    }
});

app.post('/api/analyze', async (req, res) => {
    const tags = req.body?.tags;
    if (!Array.isArray(tags)) return res.status(400).json({ error: '请提供标签数组' });
    try {
        const raw = await callLLM([
            { role: 'system', content: '只返回 JSON' },
            { role: 'user', content: `分析标签：${tags.join(', ')}\n返回：{"score":0,"pain":[{"type":"","desc":""}],"suggest":[{"name":"","zh":"","reason":""}],"combos":[{"name":"","zh":"","type":"","reason":""}]}` }
        ], 768, 0.5);
        const parsed = parseJSON(raw);
        res.json({ success: true, ...parsed });
    } catch(e) { res.status(500).json({ error: e.message }); }
});

app.get('*', (req, res) => res.sendFile(path.join(PUBLIC_DIR, 'index.html')));

app.listen(PORT, () => console.log(`dtags :${PORT} | ${MODEL}`));
