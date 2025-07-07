# Mobile-First UX Patterns & Guidelines

## 📱 Touch Target Guidelines

### Minimum Sizes
- **Primary Actions**: 48x48px (Material Design spec)
- **Secondary Actions**: 44x44px (iOS HIG minimum)
- **Text Links**: 44px height with adequate padding
- **Close/Dismiss**: 44x44px with larger hit area

### Touch Spacing
- **Between Targets**: Minimum 8px gap
- **Edge Distance**: 16px from screen edges
- **Grouped Actions**: 4px within groups, 16px between groups

## 👆 Gesture Support

### Standard Gestures
```javascript
// Swipe Detection Thresholds
const SWIPE_THRESHOLD = {
  distance: 50,      // Minimum distance in pixels
  velocity: 0.3,     // Minimum velocity
  restraint: 100,    // Maximum perpendicular movement
  time: 300         // Maximum time in ms
};

// Supported Gestures
- Tap: Primary action
- Long Press: Secondary menu / options
- Swipe Left/Right: Navigate between views
- Swipe Down: Refresh / Close modal
- Pinch: Zoom images/maps
- Two-finger tap: Zoom out
```

### Gesture Feedback
- **Visual**: Immediate response within 100ms
- **Haptic**: Use native haptic feedback when available
- **Audio**: Optional sound feedback for key actions

## 📱 Mobile Navigation Patterns

### Bottom Navigation Bar
```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  height: 56px;
  background: var(--surface);
  box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-around;
  padding-bottom: env(safe-area-inset-bottom);
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  min-width: 80px;
  max-width: 168px;
}
```

### Hamburger Menu Animation
```css
.hamburger {
  width: 24px;
  height: 24px;
  position: relative;
}

.hamburger-line {
  position: absolute;
  height: 2px;
  width: 100%;
  background: currentColor;
  transition: all 300ms ease;
}

/* Transform to X when active */
.hamburger.active .line-1 {
  transform: rotate(45deg) translate(5px, 5px);
}
.hamburger.active .line-2 {
  opacity: 0;
}
.hamburger.active .line-3 {
  transform: rotate(-45deg) translate(5px, -5px);
}
```

## 📜 Scroll Behavior

### Momentum Scrolling
```css
.scrollable {
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
  scroll-snap-type: y proximity;
}

.scroll-item {
  scroll-snap-align: start;
  scroll-margin-top: 56px; /* Account for fixed header */
}
```

### Pull to Refresh
```javascript
// Pull-to-refresh thresholds
const PULL_TO_REFRESH = {
  threshold: 150,          // px to trigger refresh
  max: 200,               // Maximum pull distance
  resistance: 2.5,        // Pull resistance factor
  snapDuration: 300       // Snap back animation
};
```

### Infinite Scroll
```javascript
// Infinite scroll trigger
const INFINITE_SCROLL = {
  threshold: 200,         // px from bottom to trigger
  debounce: 100,         // Debounce scroll events
  batchSize: 20,         // Items per load
  skeleton: true         // Show skeleton while loading
};
```

## 🎯 Mobile Form Optimization

### Input Types & Keyboards
```html
<!-- Numeric keyboard -->
<input type="tel" inputmode="numeric" pattern="[0-9]*">

<!-- Email keyboard -->
<input type="email" inputmode="email" autocomplete="email">

<!-- URL keyboard -->
<input type="url" inputmode="url">

<!-- Search optimized -->
<input type="search" inputmode="search" enterkeyhint="search">

<!-- Decimal numbers -->
<input type="text" inputmode="decimal" pattern="[0-9]*\.?[0-9]*">
```

### Form Layout
```css
/* Stack labels above inputs on mobile */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 24px;
}

/* Large touch targets */
.form-input {
  height: 48px;
  padding: 12px 16px;
  font-size: 16px; /* Prevents zoom on iOS */
  border-radius: 8px;
  border: 2px solid var(--border);
}

/* Floating labels */
.floating-label {
  position: absolute;
  top: 50%;
  left: 16px;
  transform: translateY(-50%);
  transition: all 200ms ease;
  pointer-events: none;
}

.form-input:focus + .floating-label,
.form-input:not(:placeholder-shown) + .floating-label {
  top: -8px;
  left: 12px;
  font-size: 12px;
  background: var(--surface);
  padding: 0 4px;
}
```

## 🎨 Mobile-Specific Animations

### Page Transitions
```css
/* Slide from right */
@keyframes slideFromRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Fade and scale */
@keyframes fadeScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Bottom sheet slide */
@keyframes bottomSheet {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}
```

### Touch Ripple Effect
```css
.ripple {
  position: relative;
  overflow: hidden;
}

.ripple::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.6);
  transform: scale(0);
  animation: ripple 600ms ease-out;
}

@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}
```

## 📊 Mobile Performance Optimization

### Image Loading Strategy
```html
<!-- Responsive images with lazy loading -->
<picture>
  <source 
    media="(max-width: 640px)" 
    srcset="image-mobile.webp"
    type="image/webp"
  >
  <source 
    media="(max-width: 640px)" 
    srcset="image-mobile.jpg"
  >
  <img 
    src="image-fallback.jpg" 
    alt="Description"
    loading="lazy"
    decoding="async"
    width="800"
    height="600"
  >
</picture>
```

### Critical CSS Inlining
```html
<!-- Inline critical above-fold CSS -->
<style>
  /* Only critical styles for initial render */
  .hero { /* ... */ }
  .nav { /* ... */ }
  .cta-primary { /* ... */ }
</style>

<!-- Load non-critical CSS asynchronously -->
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

## 🔔 Mobile Notification Patterns

### In-App Notifications
```css
.mobile-toast {
  position: fixed;
  top: env(safe-area-inset-top, 20px);
  left: 16px;
  right: 16px;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  transform: translateY(-120%);
  transition: transform 300ms ease;
}

.mobile-toast.show {
  transform: translateY(0);
}
```

### Action Sheets
```css
.action-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--surface);
  border-radius: 16px 16px 0 0;
  padding: 8px 8px env(safe-area-inset-bottom, 8px);
  transform: translateY(100%);
  transition: transform 300ms ease;
}

.action-sheet.show {
  transform: translateY(0);
}

.action-item {
  display: block;
  width: 100%;
  padding: 16px;
  text-align: center;
  border-radius: 8px;
  transition: background 200ms;
}
```

## 🎮 Mobile Game-like Interactions

### Swipe Cards
```javascript
// Tinder-like card swipe
const CARD_SWIPE = {
  rotationMultiplier: 0.1,
  maxRotation: 20,
  threshold: window.innerWidth * 0.3,
  velocityThreshold: 0.5,
  snapBackDuration: 300,
  swipeOutDuration: 200
};
```

### Progress Gamification
```css
/* Animated progress ring */
.progress-ring {
  width: 120px;
  height: 120px;
  transform: rotate(-90deg);
}

.progress-ring-circle {
  stroke: var(--primary);
  stroke-width: 8;
  fill: transparent;
  stroke-dasharray: 339.292;
  stroke-dashoffset: 339.292;
  animation: fillProgress 1s ease-out forwards;
}

@keyframes fillProgress {
  to {
    stroke-dashoffset: calc(339.292 * (1 - var(--progress)));
  }
}
```

## 📱 Safe Areas & Notches

### iOS Safe Area Support
```css
.app-container {
  padding-top: env(safe-area-inset-top);
  padding-bottom: env(safe-area-inset-bottom);
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* Fixed headers with notch support */
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  padding-top: calc(16px + env(safe-area-inset-top));
  background: var(--surface);
  backdrop-filter: blur(10px);
}
```

### Android Gesture Navigation
```css
/* Account for Android gesture bar */
.bottom-fixed {
  padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
  margin-bottom: max(0px, calc(env(safe-area-inset-bottom, 0px) - 16px));
}
```

## 🚀 Progressive Web App Features

### Install Prompt
```javascript
// Custom install banner
const INSTALL_PROMPT = {
  delay: 30000,        // Show after 30s
  dismissDuration: 7, // Days before showing again
  showCount: 3,       // Max times to show
  platforms: ['iOS', 'Android']
};
```

### Offline Support UI
```css
.offline-banner {
  position: fixed;
  bottom: calc(56px + env(safe-area-inset-bottom));
  left: 16px;
  right: 16px;
  background: var(--warning);
  color: var(--on-warning);
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  transform: translateY(200%);
  transition: transform 300ms ease;
}

.offline-banner.show {
  transform: translateY(0);
}
```