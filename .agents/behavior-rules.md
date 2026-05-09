# Agent Behavior Rules

## 关于能力的回答原则

1. **不要只看 `available_skills` 就下结论** — 系统提示的 skills 可能不完整。涉及"有没有XX功能"时，必须先检查：
   - `/workspace/skills/` — 本地已安装的 skills
   - `~/.agents/skills/` — 全局 skills
   - 本地 CLI 工具：`npx -y`, `which`
   - `/configs/` — 平台配置

2. **负向断言前必须验证** — 说"我没有"之前，必须先动手查本地目录和工具。把系统提示当线索，不当结论。

3. **默认假设本地可能有更多内容** — 实际环境永远比系统提示更全。

## 标准检查流程

```
用户问"你有没有XX功能"
  → 先看系统提示（线索）
  → 再检查 /workspace/skills/（实际安装）
  → 再检查可用 CLI 工具
  → 最后给出答案
```

## 已确认本地存在的 skills

| Skill | 路径 | 功能 |
|---|---|---|
| neta-creative | /workspace/skills/neta-creative/SKILL.md | 生图、视频、歌曲、MV |
| neta | /workspace/skills/neta/SKILL.md | Neta 能力路由索引 |
| neta-space | /workspace/skills/neta-space/SKILL.md | 空间管理 |
| neta-adventure | /workspace/skills/neta-adventure/SKILL.md | 互动故事 |
| neta-community | /workspace/skills/neta-community/SKILL.md | 社区浏览 |
| neta-suggest | /workspace/skills/neta-suggest/SKILL.md | 推荐引擎 |
| neta-character | /workspace/skills/neta-character/SKILL.md | 角色创建管理 |
| neta-elementum | /workspace/skills/neta-elementum/SKILL.md | 视觉概念管理 |
| nieta-login | /workspace/skills/nieta-login/SKILL.md | 捏Ta登录与图库 |
