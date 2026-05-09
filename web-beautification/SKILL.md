---
name: web-beautification
description: Website beautification techniques covering layout, color, typography, animation, modern CSS effects, and responsive design.
---

# Web Beautification

Use this skill when a user wants to improve the visual appearance, aesthetics, or user experience of a website or web application.

## Core Principles

- **Less is more**: Restraint in design produces elegance.
- **Consistency**: Reuse spacing, colors, fonts, and component patterns.
- **Performance matters**: Beautiful sites must also load fast.
- **Accessibility**: Design for all users; respect `prefers-reduced-motion`, color contrast, and semantic HTML.

---

## 1. Layout & Spacing

### Whitespace (Negative Space)
- Generous `padding` and `margin` make content breathe.
- Use a spacing scale (4px/8px base): `4, 8, 12, 16, 24, 32, 48, 64`.

```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 48px;
  --space-2xl: 64px;
}
```

### Modern Layout Systems

**CSS Grid** — for 2-dimensional layouts:
```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-lg);
}
```

**Flexbox** — for 1-dimensional layouts:
```css
.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
}
```

### Visual Hierarchy
- Hero section → key content → supporting details → footer.
- Larger, bolder elements draw attention first.
- Group related items with proximity and shared styling.

---

## 2. Color & Contrast

### 60-30-10 Rule
- **60%** dominant color (background, large areas)
- **30%** secondary color (cards, sidebars)
- **10%** accent color (buttons, links, CTAs)

### CSS Custom Properties for Theming
```css
:root {
  --color-bg: #fafafa;
  --color-surface: #ffffff;
  --color-text: #1a1a2e;
  --color-text-muted: #6b7280;
  --color-primary: #6366f1;
  --color-accent: #f43f5e;
  --border-radius: 12px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f172a;
    --color-surface: #1e293b;
    --color-text: #f1f5f9;
    --color-text-muted: #94a3b8;
    --color-primary: #818cf8;
  }
}
```

### Gradient Techniques
```css
/* Subtle gradient backgrounds */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Mesh gradient effect */
background: 
  radial-gradient(at 40% 20%, rgba(99,102,241,0.15) 0, transparent 50%),
  radial-gradient(at 80% 0%, rgba(244,63,94,0.1) 0, transparent 50%),
  radial-gradient(at 0% 50%, rgba(34,211,238,0.1) 0, transparent 50%);

/* Animated gradient */
background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
background-size: 400% 400%;
animation: gradient 15s ease infinite;

@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
```

### Recommended Color Tools
- Coolors.co — palette generator
- Adobe Color — color wheel and harmony rules
- Realtime Colors — preview fonts + colors in browser
- Contrast checker — WCAG AA requires 4.5:1 for normal text

---

## 3. Typography

### Font Loading & Stacks
```css
/* System font stack (zero load time) */
font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;

/* With web font fallback */
font-family: "Inter", ui-sans-serif, system-ui, sans-serif;
```

### Typography Scale
```css
:root {
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
}
```

### Fluid Typography
```css
html {
  font-size: clamp(14px, 2vw, 18px);
}

h1 {
  font-size: clamp(1.8rem, 4vw + 1rem, 3.5rem);
}
```

### Readability Best Practices
- Line height: `1.5` for body, `1.2~1.3` for headings
- Line length: `max-width: 65ch` for body text
- Font weight: use 400/500 for body, 600/700 for emphasis

```css
.article-body {
  font-size: var(--text-base);
  line-height: 1.7;
  max-width: 65ch;
  color: var(--color-text);
}
```

---

## 4. Animation & Micro-interactions

### Libraries to Know (from GitHub)

| Library | Stars | Use Case |
|---|---|---|
| [animate.css](https://github.com/animate-css/animate.css) | 82k+ | Ready-made CSS animations, just add class |
| [popmotion](https://github.com/Popmotion/popmotion) | 20k+ | Spring & keyframe animations, tiny (~4.5kb) |
| [barba.js](https://github.com/barbajs/barba) | 13k+ | Smooth page-to-page SPA transitions |
| [lax.js](https://github.com/alexfoxy/lax.js) | 10k+ | Scroll-driven parallax animations, <4kb |
| [scenejs](https://github.com/daybrush/scenejs) | 2.8k+ | Timeline-based animation library |
| [animxyz](https://github.com/ingram-projects/animxyz) | 2.5k+ | Composable CSS animation library |
| [micron](https://github.com/webkul/micron) | 2.3k+ | Micro-interactions with CSS + JS |

### Smooth Transitions
```css
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}
```

### Keyframe Animations
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: fadeInUp 0.5s ease-out both;
}
```

### Staggered Animations
```css
.list-item:nth-child(1) { animation-delay: 0ms; }
.list-item:nth-child(2) { animation-delay: 80ms; }
.list-item:nth-child(3) { animation-delay: 160ms; }
.list-item:nth-child(4) { animation-delay: 240ms; }
```

### Respect Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Easing Functions
- `ease-out` — natural deceleration, good for entrances
- `ease-in-out` — smooth start and end, good for toggles
- `cubic-bezier(0.4, 0, 0.2, 1)` — Material Design standard
- `cubic-bezier(0.34, 1.56, 0.64, 1)` — playful bounce

### Page Transitions (Barba.js pattern)
```javascript
// Create SPA-like page transitions
import barba from '@barba/core';

barba.init({
  transitions: [{
    name: 'opacity-transition',
    leave(data) {
      return gsap.to(data.current.container, { opacity: 0 });
    },
    enter(data) {
      return gsap.from(data.next.container, { opacity: 0 });
    }
  }]
});
```

### Scroll Animations (Lax.js pattern)
```html
<div class="lax" data-lax-anchor="self" data-lax-opacity="0 1, 200 0">
  Fades out on scroll
</div>

<div class="lax" data-lax-translateY="0 0, 400 -100">
  Parallax moves up on scroll
</div>
```

---

## 5. Modern CSS Effects

### Glassmorphism (Frosted Glass)
```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--border-radius);
}
```

> Generator tool: [css.glass](https://github.com/miketromba/css.glass) (⭐430)

### Soft Shadows & Neumorphism
```css
/* Soft elevated shadow */
.card-elevated {
  box-shadow: 
    0 1px 2px rgba(0,0,0,0.04),
    0 4px 8px rgba(0,0,0,0.04),
    0 12px 24px rgba(0,0,0,0.06);
}

/* Neumorphic (soft UI) */
.neumorphic {
  background: #f0f0f3;
  box-shadow: 
    8px 8px 16px #d1d1d6,
    -8px -8px 16px #ffffff;
  border-radius: 16px;
}
```

### Scroll-Driven Animations (Modern Browsers)
```css
.scroll-fade {
  animation: fadeIn linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 30%;
}
```

### Container Queries
```css
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}
```

### Smooth Scrolling
```css
html {
  scroll-behavior: smooth;
  scroll-padding-top: 80px; /* Offset for fixed headers */
}
```

### Custom Scrollbar
```css
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(0,0,0,0.15);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(0,0,0,0.25);
}
```

---

## 6. Images & Media

### Responsive Images
```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Description" loading="lazy">
</picture>
```

### Aspect Ratio Boxes
```css
.aspect-video {
  aspect-ratio: 16 / 9;
  object-fit: cover;
}
```

### Image Hover Effects
```css
.img-zoom {
  overflow: hidden;
  border-radius: var(--border-radius);
}

.img-zoom img {
  transition: transform 0.4s ease;
}

.img-zoom:hover img {
  transform: scale(1.05);
}
```

### Loading Skeleton
```css
.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

---

## 7. Responsive Design

### Mobile-First Breakpoints
```css
/* Default: mobile styles */

@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

### Fluid Spacing
```css
section {
  padding: clamp(24px, 5vw, 80px) clamp(16px, 3vw, 48px);
}
```

---

## 8. UI Component Patterns

### Beautiful Button
```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}
```

### Beautiful Card
```css
.card {
  background: var(--color-surface);
  border-radius: var(--border-radius);
  padding: var(--space-lg);
  border: 1px solid rgba(0,0,0,0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
```

### Beautiful Badge / Tag
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  font-size: var(--text-xs);
  font-weight: 500;
  border-radius: 9999px;
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
}
```

### Beautiful Checkbox (from pretty-checkbox)
```html
<div class="pretty p-default p-curve p-thick">
  <input type="checkbox" />
  <div class="state p-primary">
    <label>Remember me</label>
  </div>
</div>
```
> Library: [pretty-checkbox](https://github.com/lokesh-coder/pretty-checkbox) (⭐1.8k)

---

## 9. UI Component Libraries to Reference

### Tailwind CSS Ecosystem
| Library | Stars | Description |
|---|---|---|
| [headlessui](https://github.com/tailwindlabs/headlessui) | 28k+ | Unstyled, accessible UI components |
| [floatui](https://github.com/MarsX-dev/floatui) | 3.6k+ | Beautiful React/Vue components + templates |
| [rippleui](https://github.com/Siumauricio/rippleui) | 1k+ | Clean, modern Tailwind CSS components |
| [seraui](https://github.com/seraui/seraui) | 1.3k+ | React/Next.js components with Tailwind |
| [smoothui](https://github.com/educlopez/smoothui) | 785 | Components with smooth animations |

### Bootstrap / General
| Library | Stars | Description |
|---|---|---|
| [shards-ui](https://github.com/DesignRevision/shards-ui) | 1.7k+ | Beautiful & modern Bootstrap 4 UI kit |

---

## 10. Quick Checklist

Before delivering a beautified page, verify:

- [ ] Consistent spacing scale used throughout
- [ ] Color contrast meets WCAG AA (4.5:1 for text)
- [ ] No more than 2 font families
- [ ] Dark mode support (`prefers-color-scheme`)
- [ ] Reduced motion support (`prefers-reduced-motion`)
- [ ] Responsive on mobile, tablet, and desktop
- [ ] Images optimized (WebP/AVIF, lazy loading)
- [ ] Hover/focus states on interactive elements
- [ ] Smooth scrolling enabled
- [ ] No layout shift (CLS) from images or fonts
- [ ] Page transitions feel smooth (consider barba.js for multi-page)

---

## Workflow

When asked to beautify a website or page:

1. **Assess current state** — read existing HTML/CSS files
2. **Identify improvements** — spacing, colors, typography, effects
3. **Apply systematically** — start with layout/spacing, then colors, then effects
4. **Ensure responsiveness** — test across breakpoints
5. **Verify accessibility** — contrast, motion preferences, focus states
6. **Deliver** — show the result, explain key changes

For creating demos or examples, use the `public-share` skill to publish to `/public` and return a public URL.
