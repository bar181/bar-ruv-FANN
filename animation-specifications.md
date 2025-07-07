# Animation & Micro-interaction Specifications

## 🎬 Animation Principles

### Core Guidelines
1. **Purpose-Driven**: Every animation must serve a purpose
2. **Performance-First**: 60 FPS minimum, no jank
3. **Accessibility**: Respect prefers-reduced-motion
4. **Consistency**: Use standardized timing and easing
5. **Subtlety**: Enhance, don't distract

### Timing Standards
```css
:root {
  /* Duration Scale */
  --duration-instant: 100ms;
  --duration-fast: 200ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-slower: 700ms;
  
  /* Easing Functions */
  --ease-in: cubic-bezier(0.55, 0.055, 0.675, 0.19);
  --ease-out: cubic-bezier(0.215, 0.61, 0.355, 1);
  --ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1);
  --ease-back: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-elastic: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  
  /* Standard Ease (Preferred) */
  --ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-decelerate: cubic-bezier(0, 0, 0.2, 1);
  --ease-accelerate: cubic-bezier(0.4, 0, 1, 1);
}
```

## 🎯 Micro-interactions Catalog

### Button Interactions
```css
/* Primary Button */
.btn-primary {
  position: relative;
  transform: translateY(0);
  transition: all var(--duration-fast) var(--ease-standard);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition-duration: var(--duration-instant);
}

/* Ripple Effect */
.btn-primary::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(circle, rgba(255,255,255,0.5) 0%, transparent 70%);
  transform: scale(0);
  opacity: 0;
}

.btn-primary:active::after {
  animation: ripple var(--duration-normal) var(--ease-out);
}

@keyframes ripple {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(1.5);
    opacity: 0;
  }
}
```

### Card Hover Effects
```css
.card {
  transform: translateY(0);
  transition: all var(--duration-normal) var(--ease-standard);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Scale variation for image cards */
.card-image {
  overflow: hidden;
}

.card-image img {
  transform: scale(1);
  transition: transform var(--duration-slow) var(--ease-standard);
}

.card:hover .card-image img {
  transform: scale(1.05);
}

/* 3D tilt effect */
.card-3d {
  transform-style: preserve-3d;
  transform: perspective(1000px) rotateX(0) rotateY(0);
  transition: transform var(--duration-normal) var(--ease-standard);
}

.card-3d:hover {
  transform: perspective(1000px) rotateX(var(--tilt-x)) rotateY(var(--tilt-y));
}
```

### Form Input Animations
```css
/* Floating Label */
.form-field {
  position: relative;
}

.form-label {
  position: absolute;
  top: 50%;
  left: 16px;
  transform: translateY(-50%);
  transition: all var(--duration-fast) var(--ease-standard);
  pointer-events: none;
  color: var(--text-muted);
}

.form-input:focus ~ .form-label,
.form-input:not(:placeholder-shown) ~ .form-label {
  top: -8px;
  left: 12px;
  transform: translateY(0) scale(0.85);
  background: var(--surface);
  padding: 0 4px;
  color: var(--primary);
}

/* Border Animation */
.form-input {
  border: 2px solid var(--border);
  transition: border-color var(--duration-fast) var(--ease-standard);
}

.form-input:focus {
  border-color: var(--primary);
  outline: none;
}

/* Underline Style */
.form-input-underline {
  border: none;
  border-bottom: 2px solid var(--border);
  position: relative;
}

.form-input-underline::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--primary);
  transition: width var(--duration-normal) var(--ease-standard);
}

.form-input-underline:focus::after {
  width: 100%;
}
```

## 🔄 Loading Animations

### Spinner Variations
```css
/* Classic Spinner */
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin var(--duration-slower) linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Dots Loading */
.dots-loading {
  display: flex;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--primary);
  border-radius: 50%;
  animation: dotPulse 1.4s ease-in-out infinite both;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes dotPulse {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Progress Bar */
.progress-bar {
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  transform-origin: left;
  animation: progressFill 2s var(--ease-standard) forwards;
}

@keyframes progressFill {
  from { transform: scaleX(0); }
  to { transform: scaleX(var(--progress, 1)); }
}

/* Skeleton Loading */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--skeleton-base) 25%,
    var(--skeleton-shine) 50%,
    var(--skeleton-base) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

## 📜 Scroll-Triggered Animations

### Fade In on Scroll
```css
.fade-in-scroll {
  opacity: 0;
  transform: translateY(30px);
  transition: all var(--duration-normal) var(--ease-standard);
}

.fade-in-scroll.in-view {
  opacity: 1;
  transform: translateY(0);
}

/* Stagger children */
.stagger-children > * {
  opacity: 0;
  transform: translateY(20px);
  transition: all var(--duration-normal) var(--ease-standard);
}

.stagger-children.in-view > * {
  opacity: 1;
  transform: translateY(0);
}

.stagger-children.in-view > *:nth-child(1) { transition-delay: 0ms; }
.stagger-children.in-view > *:nth-child(2) { transition-delay: 100ms; }
.stagger-children.in-view > *:nth-child(3) { transition-delay: 200ms; }
.stagger-children.in-view > *:nth-child(4) { transition-delay: 300ms; }
```

### Parallax Effects
```css
.parallax-container {
  overflow: hidden;
  position: relative;
}

.parallax-element {
  will-change: transform;
  transition: transform 0ms linear;
}

/* Subtle parallax - performant */
.parallax-slow {
  transform: translateY(calc(var(--scroll-y) * -0.2));
}

.parallax-medium {
  transform: translateY(calc(var(--scroll-y) * -0.5));
}

.parallax-fast {
  transform: translateY(calc(var(--scroll-y) * -0.8));
}
```

## 🎪 Page Transitions

### Route Transitions
```css
/* Fade transition */
.page-transition-fade-enter {
  opacity: 0;
}

.page-transition-fade-enter-active {
  opacity: 1;
  transition: opacity var(--duration-normal) var(--ease-standard);
}

.page-transition-fade-exit {
  opacity: 1;
}

.page-transition-fade-exit-active {
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-standard);
}

/* Slide transition */
.page-transition-slide-enter {
  transform: translateX(100%);
}

.page-transition-slide-enter-active {
  transform: translateX(0);
  transition: transform var(--duration-normal) var(--ease-decelerate);
}

.page-transition-slide-exit {
  transform: translateX(0);
}

.page-transition-slide-exit-active {
  transform: translateX(-100%);
  transition: transform var(--duration-normal) var(--ease-accelerate);
}
```

## 🎨 Advanced Interactions

### Magnetic Hover Effect
```javascript
// Magnetic button effect
class MagneticButton {
  constructor(element) {
    this.element = element;
    this.boundingRect = element.getBoundingClientRect();
    
    element.addEventListener('mousemove', this.onMouseMove.bind(this));
    element.addEventListener('mouseleave', this.onMouseLeave.bind(this));
  }
  
  onMouseMove(e) {
    const { left, top, width, height } = this.boundingRect;
    const x = (e.clientX - left - width / 2) * 0.15;
    const y = (e.clientY - top - height / 2) * 0.15;
    
    this.element.style.transform = `translate(${x}px, ${y}px)`;
  }
  
  onMouseLeave() {
    this.element.style.transform = 'translate(0, 0)';
  }
}
```

### Morphing Shapes
```css
.morph-shape {
  clip-path: polygon(0 0, 100% 0, 100% 75%, 0 100%);
  transition: clip-path var(--duration-normal) var(--ease-standard);
}

.morph-shape:hover {
  clip-path: polygon(0 25%, 100% 0, 100% 100%, 0 75%);
}

/* SVG morphing */
.svg-morph path {
  transition: d var(--duration-normal) var(--ease-standard);
}

.svg-morph:hover path {
  d: path('M 10 10 Q 50 0 90 10 L 90 90 Q 50 100 10 90 Z');
}
```

## ♿ Accessibility Considerations

### Reduced Motion Support
```css
/* Respect user preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
  
  /* Keep essential animations */
  .spinner {
    animation-duration: 1s !important;
  }
  
  /* Remove parallax */
  .parallax-element {
    transform: none !important;
  }
}

/* Alternative for reduced motion */
@media (prefers-reduced-motion: reduce) {
  .fade-in-scroll {
    opacity: 1;
    transform: none;
  }
  
  .card:hover {
    transform: none;
    box-shadow: 0 0 0 2px var(--primary);
  }
}
```

### Focus Animations
```css
/* Animated focus ring */
.focus-ring {
  position: relative;
}

.focus-ring::after {
  content: '';
  position: absolute;
  inset: -4px;
  border: 2px solid var(--primary);
  border-radius: inherit;
  opacity: 0;
  transform: scale(0.95);
  transition: all var(--duration-fast) var(--ease-standard);
}

.focus-ring:focus::after {
  opacity: 1;
  transform: scale(1);
}

/* Pulsing focus for critical actions */
@keyframes focusPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0.4);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(var(--primary-rgb), 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--primary-rgb), 0);
  }
}

.critical-action:focus {
  animation: focusPulse 1.5s infinite;
}
```

## 🎭 Gesture Animations

### Swipe Interactions
```css
.swipeable {
  touch-action: pan-y;
  will-change: transform;
  transition: transform var(--duration-normal) var(--ease-standard);
}

.swipeable.swiping {
  transition: none;
}

.swipeable.swipe-left {
  transform: translateX(-100%);
}

.swipeable.swipe-right {
  transform: translateX(100%);
}

.swipeable.snap-back {
  transform: translateX(0);
}
```

### Pull to Refresh
```css
.pull-to-refresh {
  position: absolute;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  transition: all var(--duration-normal) var(--ease-standard);
}

.pull-to-refresh.pulling {
  transition: none;
}

.pull-to-refresh.refreshing {
  top: 20px;
}

.pull-to-refresh.refreshing .spinner {
  animation: spin var(--duration-slower) linear infinite;
}
```

## 🚀 Performance Optimization

### Animation Performance Rules
```css
/* Use GPU-accelerated properties only */
.performant-animation {
  /* ✅ Good - GPU accelerated */
  transform: translateX(100px);
  opacity: 0.5;
  
  /* ❌ Bad - Causes reflow/repaint */
  /* left: 100px; */
  /* width: 200px; */
}

/* Optimize with will-change */
.will-animate {
  will-change: transform, opacity;
}

/* Remove will-change after animation */
.animation-complete {
  will-change: auto;
}

/* Use transform3d for GPU activation */
.gpu-accelerated {
  transform: translate3d(0, 0, 0);
}
```

### Batch DOM Updates
```javascript
// Use requestAnimationFrame for smooth animations
function smoothAnimation() {
  requestAnimationFrame(() => {
    // Batch all DOM reads
    const scrollY = window.scrollY;
    const viewportHeight = window.innerHeight;
    
    // Then batch all DOM writes
    elements.forEach(el => {
      el.style.transform = `translateY(${scrollY * 0.5}px)`;
    });
  });
}

// Debounce scroll events
let scrollTimeout;
window.addEventListener('scroll', () => {
  clearTimeout(scrollTimeout);
  scrollTimeout = setTimeout(smoothAnimation, 10);
}, { passive: true });
```