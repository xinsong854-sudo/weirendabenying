# Web Design Skill 学习笔记

来源：https://github.com/ConardLi/web-design-skill/ （仓库实际内容为 Garden Skills，重点：`skills/web-design-engineer`）

## 核心定位
把 AI 做网页从“能用”提升到“有设计判断”：网页、落地页、dashboard、交互原型、HTML slides、动画、UI mockup、数据可视化、设计系统探索。

核心标准：不是 functional，而是 stunning；每个像素、每个交互都要有意图。

## 工作流
1. 理解需求：信息足够就直接做；不够才问，不机械问长列表。
2. 获取设计上下文：用户素材 > 产品现有页面/代码 > 行业参考 > 从零建立临时系统。
3. 写代码前声明设计系统：颜色、字体、间距、圆角、阴影、动效。
4. 尽早给 v0：布局、token、占位符、关键假设；先让用户纠偏。
5. 完整构建：组件、状态、动效；重大决策暂停确认。
6. 验证：控制台、响应式、状态、无溢出、无 rogue color、无 AI 俗套。

## 反 AI 俗套
避免：
- 紫粉蓝渐变背景泛滥
- 大圆角卡片 + 渐变按钮套路
- 卡片左侧彩色竖条
- emoji 充当图标
- Inter/Roboto/Arial/Fraunces/system-ui 默认审美（除非品牌已有）
- 编造 logo 墙、好评、数据、icon spam
- 没意义的 SVG 假插画

## 占位符哲学
缺素材时，专业占位比瞎画更好：
- 缺图标：`[icon]` / 方块标签
- 缺头像：首字母圆形头像
- 缺图片：标注比例的 placeholder card
- 缺数据：问用户，不编造
- 缺 logo：文字品牌名 + 简单几何

## CSS / 技术规则
- 用 CSS custom properties 管理 tokens。
- 优先 Grid + Flexbox。
- 用 `oklch()` 派生协调色，不乱 invent hex。
- `clamp()` 做流体字号；`text-wrap: pretty` 优化排版。
- 支持 container queries、prefers-reduced-motion、prefers-color-scheme。
- React CDN 原型要 pin 版本；不要用 `const styles = {}`，要命名空间如 `heroStyles`。
- 多个 Babel script 不共享作用域，组件要 `Object.assign(window, {...})`。
- 不用 `scrollIntoView`，iframe 预览里会干扰外层滚动。
- 大文件 >1000 行拆分；重大改版用 v2/v3 保留旧版。

## 输出类型规则
### 原型
- 不要 title screen，直接展示产品。
- 可用设备框增强真实感。
- 至少 3 个变体，放到 Tweaks 面板里切换。
- 覆盖 default / hover / active / focus / disabled / loading / empty / error。

### HTML 幻灯片
- 1920×1080 固定舞台，JS 缩放适配 viewport。
- 控制按钮放在缩放容器外。
- 键盘 ← → / Space；localStorage 记住进度。
- slide 编号显示从 1 开始；每页有 `data-screen-label`。

### 数据可视化
- Chart.js 简单图，D3 复杂图。
- 用 ResizeObserver。
- 深浅色切换。
- data-ink ratio 优先，去除多余网格/3D/阴影。
- 颜色表达语义，不做纯装饰。

### 动画
复杂度递进：CSS transition/animation → React state/RAF → 自定义 timeline → 必要时 Popmotion。默认不重度依赖 GSAP/Framer/Lottie，除非确实需要或用户要求。

## Tweaks 面板
- 右下浮动，标题固定叫 Tweaks。
- 关闭后完全隐藏。
- 多变体用 dropdown/toggle，而不是多个文件。
- 即使用户没要求，也可放 1–2 个有价值的创意参数。

## 设计原则
- 先建立视觉词汇，再动手。
- 新增元素要像原生设计系统的一部分。
- 用设计语言解释决策：如“收紧间距增强工具感”。
- 少即是多，留白是设计，不用内容硬填。
- 页面空不是内容问题，多半是构图、比例、节奏问题。

## 推荐视觉起点
- 现代科技：Space Grotesk + Inter，蓝紫（但避免俗套渐变）
- 优雅杂志：Newsreader + Outfit，暖棕
- 高端品牌：Sora + Plus Jakarta Sans，近黑
- 活泼消费：Plus Jakarta Sans + Outfit，珊瑚
- 极简专业：Outfit + Space Grotesk，青蓝
- 手作温度：Caveat + Newsreader，焦糖

## 交付前检查
- 控制台无 error/warning。
- 目标 viewport 正常。
- 交互状态齐全。
- 无文字溢出；`text-wrap: pretty`。
- 所有颜色来自已声明系统。
- 无 `scrollIntoView`。
- 无 `const styles = {}`。
- 无 AI 俗套、无编造数据、无 filler。
- 结构语义清楚，后续易改。
- 视觉质量目标：Dribbble / Behance 展示级。
