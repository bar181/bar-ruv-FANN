# Component-Specific UX Specifications

## 🎯 Hero Section Requirements

### Visual Design
- **Height**: 100vh on desktop, min-height: 600px on mobile
- **Background**: Gradient overlay on image for text readability
- **Text Shadow**: Subtle shadow for contrast insurance

### Interactions
- **CTA Buttons**: 
  - Primary: Filled background with hover scale
  - Secondary: Outlined with fill on hover
  - Minimum 48px height on mobile
- **Scroll Indicator**: Animated arrow bouncing (2s interval)

### Accessibility
- **Hero Image**: Decorative, use aria-hidden="true"
- **Heading**: Single H1, maximum 60 characters
- **Subheading**: H2 or p with larger font size

## 🏗️ Feature Cards Requirements

### Layout
- **Grid**: 3 columns desktop, 1 column mobile
- **Gap**: 32px between cards
- **Card Padding**: 24px mobile, 32px desktop

### Interactions
- **Hover Effect**: 
  - Lift: translateY(-4px)
  - Shadow: 0 8px 16px rgba(0,0,0,0.1)
  - Duration: 300ms ease-out
- **Focus**: Same as hover + outline
- **Click**: Entire card clickable if has link

### Content
- **Icon**: 48x48px, descriptive aria-label
- **Title**: H3, max 2 lines
- **Description**: Max 3 lines with ellipsis

## 🍔 Navigation Menu Requirements

### Desktop Behavior
- **Sticky**: After scroll past hero
- **Background**: Blur effect (backdrop-filter)
- **Height**: 64px normal, 56px when sticky
- **Transition**: All changes over 300ms

### Mobile Behavior
- **Toggle**: Hamburger to X animation
- **Drawer**: Slide from right, full height
- **Backdrop**: Click to close
- **Body**: Prevent scroll when open

### Accessibility
- **Toggle Button**: aria-expanded, aria-controls
- **Menu**: nav with aria-label
- **Current Page**: aria-current="page"
- **Focus Trap**: When mobile menu open

## 📝 Form Components Requirements

### Input Fields
- **Height**: 48px mobile, 44px desktop
- **Border**: 2px, darker on focus
- **Label**: Always visible (no placeholder-only)
- **Error Icon**: Red exclamation inside field
- **Success Icon**: Green checkmark

### Validation
- **Timing**: On blur, not on type
- **Messages**: Below field, 12px gap
- **Summary**: At form top for multi-field errors
- **Success**: Green border + checkmark

### Select Dropdowns
- **Custom Style**: Match input design
- **Arrow**: Rotates on open
- **Options**: Max-height with scroll
- **Keyboard**: Arrow keys navigation

## 🏃 Performance Requirements

### Core Web Vitals Targets
- **LCP**: < 2.5s (Largest Contentful Paint)
- **FID**: < 100ms (First Input Delay)
- **CLS**: < 0.1 (Cumulative Layout Shift)

### Image Optimization
- **Format**: WebP with JPEG fallback
- **Sizes**: Multiple for responsive
- **Loading**: Lazy load below fold
- **Placeholder**: Blurred thumbnail

### Font Loading
- **Strategy**: font-display: swap
- **Preload**: Critical fonts only
- **Fallback**: System font stack
- **Subset**: Only used characters

## 🎨 Interaction Feedback Patterns

### Button States
```css
/* Default */
background: var(--primary);
transform: scale(1);
box-shadow: 0 2px 4px rgba(0,0,0,0.1);

/* Hover */
background: var(--primary-dark);
transform: scale(1.02);
box-shadow: 0 4px 8px rgba(0,0,0,0.15);

/* Active */
transform: scale(0.98);
box-shadow: 0 1px 2px rgba(0,0,0,0.1);

/* Focus */
outline: 2px solid var(--primary);
outline-offset: 2px;

/* Disabled */
opacity: 0.5;
cursor: not-allowed;
```

### Loading Animations
```css
/* Spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Pulse */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Skeleton */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

## 📱 Touch Gestures

### Swipe Support
- **Carousels**: Swipe left/right
- **Modals**: Swipe down to close
- **Tabs**: Swipe between tabs
- **Sensitivity**: 50px minimum

### Touch Feedback
- **Tap**: Immediate visual response
- **Long Press**: Show context menu
- **Pinch**: Image zoom if applicable
- **Double Tap**: Zoom to element

## 🔍 Search Experience

### Input Behavior
- **Autocomplete**: After 2 characters
- **Debounce**: 300ms delay
- **Results**: Dropdown with categories
- **Empty State**: Helpful suggestions

### Results Display
- **Highlighting**: Match text bold
- **Categories**: Grouped results
- **Count**: Show result numbers
- **Navigation**: Arrow keys + Enter

## 💬 Notification Patterns

### Toast Types
1. **Success**: Green, checkmark icon
2. **Error**: Red, X icon
3. **Warning**: Yellow, ! icon
4. **Info**: Blue, i icon

### Behavior Rules
- **Stack**: Maximum 3 visible
- **Order**: Newest on top
- **Persist**: Errors until dismissed
- **Queue**: Show one at a time if many

## 🎯 Call-to-Action Guidelines

### Primary CTA
- **Size**: Large, prominent
- **Color**: High contrast
- **Position**: Above fold
- **Text**: Action-oriented (Start, Get, Try)

### Secondary CTA
- **Style**: Outlined or text
- **Size**: Smaller than primary
- **Position**: Near primary
- **Purpose**: Alternative action

### Micro CTAs
- **Learn More**: With arrow →
- **Expand**: With chevron ⌄
- **External**: With icon 🔗
- **Download**: With icon ⬇

## 📊 Data Visualization

### Charts/Graphs
- **Colors**: Accessible palette
- **Labels**: Always visible
- **Interaction**: Hover for details
- **Alternative**: Table view option

### Progress Indicators
- **Bar**: With percentage text
- **Steps**: Numbered with labels
- **Circular**: For loading/completion
- **Accessibility**: Text equivalent

## 🌐 Internationalization Ready

### Text Expansion
- **Allow**: 30% expansion room
- **Truncate**: With ellipsis if needed
- **Tooltips**: For truncated text

### RTL Support
- **Margins**: Use logical properties
- **Icons**: Mirror if directional
- **Layout**: Flexible for reversal

### Date/Time
- **Format**: Locale-appropriate
- **Timezone**: User's local time
- **Relative**: "2 hours ago" option