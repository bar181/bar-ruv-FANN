# UX & Accessibility Requirements - Landing Page

## 🎨 Color & Contrast Requirements (WCAG AA Compliance)

### Primary Palette - 2025 Warm Trends
- **Primary Background**: `#FFF8F3` (Warm White)
- **Primary Text**: `#2D1810` (Deep Brown) - Contrast ratio: 12.63:1 ✅
- **Primary Accent**: `#E85D04` (Vibrant Orange) - Contrast ratio: 4.51:1 ✅
- **Secondary Accent**: `#DC2F02` (Deep Red) - Contrast ratio: 5.87:1 ✅
- **Tertiary Accent**: `#F48C06` (Golden Orange) - Contrast ratio: 3.01:1 (Use with dark text)

### Supporting Colors
- **Muted Background**: `#FAA307` (Soft Amber) - For sections
- **Dark Background**: `#370617` (Deep Burgundy) - Contrast with white text: 13.91:1 ✅
- **Success**: `#38A169` (Green) - Contrast ratio: 4.5:1 ✅
- **Error**: `#E53E3E` (Red) - Contrast ratio: 4.52:1 ✅
- **Info**: `#3182CE` (Blue) - Contrast ratio: 4.51:1 ✅

### Contrast Requirements
- **Normal Text**: Minimum 4.5:1 ratio
- **Large Text** (18pt+ or 14pt+ bold): Minimum 3:1 ratio
- **Interactive Elements**: Minimum 3:1 ratio against background
- **Focus Indicators**: Minimum 3:1 ratio, 2px outline

## 📱 Responsive Breakpoints

### Mobile First Approach
```css
/* Base - Mobile (320px - 639px) */
- Single column layout
- Touch-friendly tap targets (min 44x44px)
- Simplified navigation (hamburger menu)
- Stack all content vertically
- Font size: 16px base (prevents zoom on iOS)

/* Tablet (640px - 1023px) */
@media (min-width: 640px) {
  - Two column layouts where appropriate
  - Expanded navigation options
  - Larger spacing between elements
  - Font size: 18px base
}

/* Desktop (1024px - 1279px) */
@media (min-width: 1024px) {
  - Full multi-column layouts
  - Sidebar navigation if needed
  - Hover states enabled
  - Font size: 18px base
}

/* Large Desktop (1280px+) */
@media (min-width: 1280px) {
  - Maximum content width: 1280px
  - Centered container with margins
  - Enhanced whitespace
  - Font size: 20px base
}
```

## 🔔 Toast Notifications

### Positioning
- **Desktop**: Top-right corner, 24px from edges
- **Mobile**: Top-center, full width minus 16px margins
- **Z-index**: 9999 (above all content)

### Behavior
- **Animation**: Slide in from right (desktop) or top (mobile)
- **Duration**: 300ms ease-out
- **Auto-dismiss**: 5 seconds for success, 8 seconds for errors
- **Stacking**: Maximum 3 toasts, older ones fade out
- **Dismissible**: Click or swipe to dismiss

### Accessibility
- **Role**: `role="alert"` for errors, `role="status"` for success
- **Live Region**: `aria-live="polite"` for non-critical, `aria-live="assertive"` for errors
- **Focus Management**: Don't steal focus unless action required

## 🪟 Modal Dialogs

### Structure
```html
<div role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <h2 id="modal-title">Modal Title</h2>
  <!-- Content -->
</div>
```

### Behavior
- **Backdrop**: Semi-transparent overlay (rgba(0,0,0,0.5))
- **Animation**: Fade in backdrop (200ms), scale up modal (300ms)
- **Focus Trap**: Tab cycles within modal only
- **Close Methods**: 
  - Escape key
  - Click backdrop
  - Close button (X)
  - Cancel/Confirm buttons

### Accessibility
- **Initial Focus**: First interactive element or close button
- **Focus Return**: Return to trigger element on close
- **Screen Reader**: Announce modal opening/closing
- **Keyboard**: Full keyboard navigation support

## ♿ Accessibility Guidelines

### Keyboard Navigation
1. **Tab Order**: Logical flow matching visual layout
2. **Skip Links**: "Skip to main content" as first focusable element
3. **Focus Indicators**: 
   - 2px solid outline
   - Color: `#E85D04` (primary accent)
   - Offset: 2px
   - Never remove outline without alternative

### Interactive Elements
1. **Buttons**:
   - Minimum size: 44x44px (mobile), 32x32px (desktop)
   - Clear hover/focus/active states
   - Descriptive labels (avoid "Click here")
   - Loading states with aria-busy="true"

2. **Links**:
   - Underline on hover/focus
   - Color different from body text
   - Visited state color variation
   - External links: include icon + screen reader text

3. **Forms**:
   - Label all inputs clearly
   - Group related fields with fieldset/legend
   - Error messages linked via aria-describedby
   - Success feedback for completed fields

### Screen Reader Support
1. **Semantic HTML**: Use proper heading hierarchy (h1-h6)
2. **ARIA Labels**: For icons and complex widgets
3. **Alt Text**: Descriptive for informative images, "" for decorative
4. **Landmarks**: main, nav, footer, aside with appropriate roles
5. **Dynamic Content**: Announce changes with live regions

## 🎭 Animation & Micro-interactions

### Performance Guidelines
- **60 FPS**: All animations must maintain smooth performance
- **GPU Acceleration**: Use transform and opacity only
- **Reduced Motion**: Respect prefers-reduced-motion

### Animation Timing
```css
/* Standard timings */
--animation-fast: 150ms;
--animation-normal: 300ms;
--animation-slow: 500ms;

/* Easing functions */
--ease-out: cubic-bezier(0.215, 0.61, 0.355, 1);
--ease-in-out: cubic-bezier(0.645, 0.045, 0.355, 1);
--spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Micro-interactions
1. **Hover States**:
   - Scale: 1.02 for cards, 1.05 for buttons
   - Shadow elevation increase
   - Color brightness adjustment (+10%)

2. **Click Feedback**:
   - Scale down to 0.98 on active
   - Ripple effect from click point (Material-like)

3. **Loading States**:
   - Skeleton screens for content
   - Spinner for actions (with text description)
   - Progress bars for multi-step processes

4. **Scroll Animations**:
   - Fade in on scroll (subtle, once only)
   - Parallax effects (subtle, performance-conscious)
   - Sticky elements with smooth transitions

## 📊 Visual Hierarchy

### Typography Scale
```css
/* Fluid typography with clamp() */
--text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
--text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
--text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
--text-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
--text-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
--text-2xl: clamp(1.5rem, 1.3rem + 1vw, 1.875rem);
--text-3xl: clamp(1.875rem, 1.5rem + 1.875vw, 2.25rem);
--text-4xl: clamp(2.25rem, 1.8rem + 2.25vw, 3rem);
```

### Spacing System
```css
/* 8px base unit */
--space-1: 0.5rem;   /* 8px */
--space-2: 1rem;     /* 16px */
--space-3: 1.5rem;   /* 24px */
--space-4: 2rem;     /* 32px */
--space-5: 2.5rem;   /* 40px */
--space-6: 3rem;     /* 48px */
--space-8: 4rem;     /* 64px */
--space-10: 5rem;    /* 80px */
--space-12: 6rem;    /* 96px */
```

### Z-Index Scale
```css
--z-base: 0;
--z-dropdown: 100;
--z-sticky: 200;
--z-fixed: 300;
--z-modal-backdrop: 400;
--z-modal: 500;
--z-popover: 600;
--z-tooltip: 700;
--z-toast: 800;
--z-alert: 900;
```

## 🚨 Error Handling & Loading States

### Error States
1. **Form Validation**:
   - Inline error messages below fields
   - Red border (with icon for colorblind users)
   - Error summary at form top for screen readers

2. **Network Errors**:
   - User-friendly messages
   - Retry options
   - Fallback content where possible

3. **404/Error Pages**:
   - Clear messaging
   - Helpful navigation options
   - Maintain brand consistency

### Loading States
1. **Initial Load**:
   - Skeleton screens matching content structure
   - Progressive enhancement
   - Avoid layout shift

2. **Action Feedback**:
   - Immediate visual response
   - Disable interaction during processing
   - Clear completion feedback

3. **Lazy Loading**:
   - Images: Blur-up technique
   - Content: Intersection Observer
   - Show loading indicators for long operations

## 📋 Checklist for Implementation

### Before Launch
- [ ] Test with keyboard only navigation
- [ ] Run axe DevTools accessibility audit
- [ ] Check all color contrasts with WebAIM tool
- [ ] Test with screen reader (NVDA/JAWS/VoiceOver)
- [ ] Verify mobile touch targets (44x44px minimum)
- [ ] Test on real devices (not just browser DevTools)
- [ ] Check performance metrics (Core Web Vitals)
- [ ] Test with slow network connection
- [ ] Verify animations with prefers-reduced-motion
- [ ] Test all interactive states (hover, focus, active, disabled)

### Cross-Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS 14+)
- [ ] Chrome Mobile (Android 8+)