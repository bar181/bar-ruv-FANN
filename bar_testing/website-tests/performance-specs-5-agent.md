# Performance Optimization Specifications for 5-Agent Landing Page

## Performance Budgets

### Core Web Vitals Targets
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms  
- **CLS (Cumulative Layout Shift)**: < 0.1
- **Total Page Load**: < 3s (hard requirement)
- **Time to Interactive**: < 3.5s

### Resource Budgets
- **HTML**: < 15KB (gzipped)
- **CSS**: < 20KB (gzipped)
- **JavaScript**: < 30KB (gzipped)
- **Images**: < 200KB total (optimized)
- **Fonts**: < 50KB (subset, woff2)
- **Total Page Weight**: < 315KB

## Image Optimization Requirements

### Format Strategy
- **Hero Images**: WebP with JPEG fallback
- **Icons**: Inline SVG for < 2KB, external SVG for larger
- **Decorative Images**: CSS gradients/patterns where possible
- **Agent Avatars**: WebP 64x64px max

### Loading Strategy
```html
<!-- Critical hero image -->
<img src="hero.webp" 
     srcset="hero-320w.webp 320w,
             hero-768w.webp 768w,
             hero-1200w.webp 1200w"
     sizes="100vw"
     loading="eager"
     fetchpriority="high"
     alt="ruv-swarm performance">

<!-- Below-fold images -->
<img src="agent.webp" 
     loading="lazy"
     decoding="async"
     alt="Agent visualization">
```

### Optimization Guidelines
- Use responsive images with srcset
- Implement lazy loading for below-fold content
- Preload critical images
- Use CSS sprites for small recurring icons
- Compress all images (85% quality for JPEG/WebP)

## CSS Optimization Strategy

### Critical CSS
```css
/* Inline in <head> - extracted critical path CSS */
:root {
  --primary: #00f0ff;
  --bg: #0a0e27;
  --text: #ffffff;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, sans-serif;
}

.hero {
  min-height: 100vh;
  display: grid;
  place-items: center;
}

/* GPU-accelerated animations */
.agent-card {
  transform: translateZ(0);
  will-change: transform;
}
```

### Non-Critical CSS Loading
```html
<!-- Preload non-critical CSS -->
<link rel="preload" href="styles.css" as="style">
<link rel="stylesheet" href="styles.css" media="print" onload="this.media='all'">
```

### Animation Performance
- Use only transform and opacity for animations
- Enable GPU acceleration with `transform: translateZ(0)`
- Use CSS containment for complex components
- Implement `will-change` sparingly
- Prefer CSS animations over JavaScript

## JavaScript Optimization

### Loading Strategy
```html
<!-- Critical inline script -->
<script>
  // Feature detection and critical path logic
  if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading supported
  }
</script>

<!-- Async non-critical scripts -->
<script src="animations.js" async></script>
<script src="analytics.js" defer></script>
```

### Code Splitting
- **Core**: Navigation, critical interactions (< 10KB)
- **Enhancements**: Animations, particles (< 15KB)
- **Analytics**: Tracking, monitoring (< 5KB)

### Performance Patterns
```javascript
// Debounce scroll events
let scrollTimeout;
window.addEventListener('scroll', () => {
  if (scrollTimeout) return;
  scrollTimeout = requestAnimationFrame(() => {
    updateScrollEffects();
    scrollTimeout = null;
  });
}, { passive: true });

// Intersection Observer for lazy loading
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { rootMargin: '50px' });
```

## 5-Agent Performance Metrics Display

### Metric Visualization
```html
<div class="performance-metrics">
  <h3>5-Agent Swarm Performance</h3>
  <div class="metric-grid">
    <div class="metric">
      <span class="value">-34.52%</span>
      <span class="label">Time Reduction</span>
    </div>
    <div class="metric">
      <span class="value">2.8x</span>
      <span class="label">Speed Improvement</span>
    </div>
    <div class="metric">
      <span class="value">84.8%</span>
      <span class="label">Task Success Rate</span>
    </div>
    <div class="metric">
      <span class="value">32.3%</span>
      <span class="label">Token Efficiency</span>
    </div>
  </div>
</div>
```

### Agent Activity Visualization
```css
/* Efficient agent status indicators */
.agent-status {
  --status-color: var(--idle, #666);
  background: radial-gradient(circle, var(--status-color) 0%, transparent 70%);
  animation: pulse 2s ease-in-out infinite;
}

.agent-status[data-status="active"] {
  --status-color: var(--active, #00f0ff);
  animation-duration: 1s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(0.95); }
  50% { opacity: 1; transform: scale(1.05); }
}
```

## Resource Loading Priority

### Critical Path
1. HTML document
2. Critical CSS (inline)
3. Hero image (preload)
4. Font subset (preload)
5. Core JavaScript

### Preload Strategy
```html
<link rel="preload" href="/fonts/inter-subset.woff2" as="font" crossorigin>
<link rel="preload" href="/img/hero.webp" as="image">
<link rel="preload" href="/css/styles.css" as="style">
```

### Resource Hints
```html
<link rel="dns-prefetch" href="https://cdn.example.com">
<link rel="preconnect" href="https://fonts.googleapis.com">
```

## Performance Monitoring

### Metrics Collection
```javascript
// Real User Monitoring (RUM)
if ('PerformanceObserver' in window) {
  // Web Vitals monitoring
  new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      console.log(`${entry.name}: ${entry.value}ms`);
      // Send to analytics
    }
  }).observe({ entryTypes: ['largest-contentful-paint'] });
}

// Custom metrics for 5-agent performance
const agentMetrics = {
  coordinationTime: 0,
  parallelExecution: true,
  taskCompletionRate: 0.848,
  tokenReduction: 0.323
};
```

## Build Optimization

### Minification & Compression
- HTML: Minify, remove comments
- CSS: Minify, remove unused styles (PurgeCSS)
- JS: Minify, tree-shake, bundle
- Enable Brotli/Gzip compression

### Caching Strategy
```
# .htaccess or nginx config
# Immutable assets
Cache-Control: public, max-age=31536000, immutable

# HTML
Cache-Control: no-cache, must-revalidate

# API responses
Cache-Control: private, max-age=300
```

## Testing & Validation

### Performance Testing Tools
- Lighthouse CI (target score: 95+)
- WebPageTest (Speed Index < 3000)
- Chrome DevTools Performance Panel

### Automated Checks
```json
{
  "lighthouse": {
    "performance": 95,
    "accessibility": 100,
    "best-practices": 100,
    "seo": 100
  },
  "budgets": [{
    "resourceSizes": [
      { "resourceType": "total", "budget": 315 },
      { "resourceType": "script", "budget": 30 },
      { "resourceType": "stylesheet", "budget": 20 }
    ]
  }]
}
```

## Implementation Checklist

- [ ] Inline critical CSS
- [ ] Implement lazy loading for images
- [ ] Optimize and convert images to WebP
- [ ] Set up resource preloading
- [ ] Configure async/defer for scripts
- [ ] Implement GPU-accelerated animations
- [ ] Add performance monitoring
- [ ] Set up build optimization pipeline
- [ ] Configure caching headers
- [ ] Test with throttled network conditions
- [ ] Validate Core Web Vitals
- [ ] Implement 5-agent performance metrics display