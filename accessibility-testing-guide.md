# Accessibility Testing & Quality Assurance Guide

## 🔍 Automated Testing Tools

### 1. axe DevTools
```javascript
// Integration example
describe('Accessibility Tests', () => {
  it('should have no accessibility violations', async () => {
    const results = await axe(document.body);
    expect(results.violations).toHaveLength(0);
  });
});

// Common issues to check:
- Color contrast failures
- Missing alt text
- Empty buttons/links
- Missing form labels
- Incorrect heading hierarchy
```

### 2. Lighthouse CI
```yaml
# .github/workflows/lighthouse.yml
lighthouse:
  ci:
    collect:
      settings:
        preset: 'desktop'
        onlyCategories: ['accessibility', 'best-practices']
    assert:
      assertions:
        'categories:accessibility': ['error', {minScore: 0.95}]
        'color-contrast': 'error'
        'heading-order': 'error'
        'image-alt': 'error'
```

### 3. Pa11y Configuration
```json
{
  "defaults": {
    "standard": "WCAG2AA",
    "timeout": 10000,
    "wait": 1000,
    "actions": [
      "wait for element .content to be visible"
    ]
  },
  "urls": [
    {
      "url": "http://localhost:3000",
      "actions": [
        "click element .menu-toggle",
        "wait for element .menu to be visible"
      ]
    }
  ]
}
```

## 🖐️ Manual Testing Checklist

### Keyboard Navigation Testing
```markdown
## Keyboard Navigation Checklist

### Basic Navigation
- [ ] Tab through all interactive elements
- [ ] Shift+Tab navigates backwards
- [ ] Enter activates buttons and links
- [ ] Space activates buttons and checkboxes
- [ ] Arrow keys work in menus and tabs
- [ ] Escape closes modals and dropdowns

### Focus Management
- [ ] Focus indicators visible on all elements
- [ ] Focus order matches visual layout
- [ ] No keyboard traps
- [ ] Skip links work correctly
- [ ] Focus returns to trigger after modal close
- [ ] Focus doesn't move to hidden elements

### Custom Components
- [ ] Dropdowns: Arrow keys navigate options
- [ ] Tabs: Arrow keys switch tabs
- [ ] Accordions: Enter/Space toggle
- [ ] Carousels: Arrow keys navigate slides
- [ ] Date pickers: Full keyboard support
- [ ] Autocomplete: Arrow keys + Enter
```

### Screen Reader Testing

#### NVDA (Windows) Test Script
```markdown
1. **Page Structure**
   - Press H to navigate headings
   - Verify heading hierarchy (h1 → h2 → h3)
   - Press D to navigate landmarks
   - Verify main, nav, footer are announced

2. **Navigation**
   - Press Tab to navigate links
   - Verify link text is descriptive
   - Press B for buttons
   - Verify button purpose is clear

3. **Forms**
   - Press F to navigate form fields
   - Verify labels are announced
   - Check error messages are associated
   - Verify required fields are announced

4. **Dynamic Content**
   - Verify live regions announce updates
   - Check loading states are announced
   - Verify error/success messages are heard
```

#### VoiceOver (macOS/iOS) Commands
```bash
# Desktop Commands
VO+A             # Read all
VO+Right/Left    # Navigate elements
VO+Command+H     # Navigate headings
VO+Command+L     # Navigate links
VO+Space         # Activate element

# Mobile Gestures
Swipe Right      # Next element
Swipe Left       # Previous element
Double Tap       # Activate
Two-finger swipe # Scroll
Rotor gesture    # Change navigation mode
```

## 🎨 Color & Contrast Testing

### Manual Contrast Checking
```javascript
// Color contrast checking function
function checkContrast(foreground, background) {
  const ratio = getContrastRatio(foreground, background);
  
  return {
    ratio: ratio,
    AA: {
      normal: ratio >= 4.5,
      large: ratio >= 3
    },
    AAA: {
      normal: ratio >= 7,
      large: ratio >= 4.5
    }
  };
}

// Test cases
const contrastTests = [
  { fg: '#2D1810', bg: '#FFF8F3', expected: 'AA' },
  { fg: '#E85D04', bg: '#FFFFFF', expected: 'AA' },
  { fg: '#FFFFFF', bg: '#370617', expected: 'AAA' }
];
```

### Color Blindness Simulation
```css
/* CSS filters for testing */
.protanopia {
  filter: url('#protanopia-filter');
}

.deuteranopia {
  filter: url('#deuteranopia-filter');
}

.tritanopia {
  filter: url('#tritanopia-filter');
}

.achromatopsia {
  filter: grayscale(100%);
}
```

## 📱 Mobile Accessibility Testing

### iOS VoiceOver Testing
```markdown
## VoiceOver Gesture Reference

### Navigation
- Swipe right: Next item
- Swipe left: Previous item
- Swipe up/down: Adjust rotor setting
- Double tap: Activate
- Triple tap: Long press
- Two-finger swipe: Scroll

### Rotor Settings
1. Headings
2. Links
3. Form Controls
4. Containers
5. Buttons
6. Text Fields

### Testing Checklist
- [ ] All content readable
- [ ] Images have descriptions
- [ ] Buttons labeled clearly
- [ ] Form fields associated with labels
- [ ] Custom gestures documented
- [ ] Modal focus trapped correctly
```

### Android TalkBack Testing
```markdown
## TalkBack Commands

### Basic Navigation
- Swipe right/left: Navigate items
- Double tap: Activate
- Swipe up then right: Open local menu
- Swipe down then right: Open global menu

### Reading Controls
- Swipe up/down: Change reading control
- Three-finger swipe: Scroll

### Testing Points
- [ ] Explore by touch works
- [ ] All controls reachable
- [ ] Custom views properly labeled
- [ ] LiveRegions announce changes
- [ ] Navigation drawer accessible
```

## 🧪 Automated Test Examples

### Jest + Testing Library
```javascript
// Accessibility-focused component tests
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Button Component', () => {
  it('should be accessible', async () => {
    const { container } = render(
      <Button onClick={() => {}}>Click me</Button>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should have proper ARIA attributes when loading', () => {
    render(<Button loading>Loading...</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(button).toHaveAttribute('aria-disabled', 'true');
  });
  
  it('should be keyboard navigable', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Press me</Button>);
    
    const button = screen.getByRole('button');
    button.focus();
    expect(document.activeElement).toBe(button);
    
    fireEvent.keyDown(button, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalled();
  });
});
```

### Cypress Accessibility Tests
```javascript
// cypress/support/commands.js
import 'cypress-axe';

// cypress/integration/a11y.spec.js
describe('Accessibility Tests', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.injectAxe();
  });
  
  it('Has no detectable a11y violations on load', () => {
    cy.checkA11y();
  });
  
  it('Has no a11y violations after interaction', () => {
    cy.get('.menu-toggle').click();
    cy.checkA11y('.navigation');
    
    cy.get('.modal-trigger').click();
    cy.checkA11y('.modal', {
      rules: {
        'color-contrast': { enabled: true }
      }
    });
  });
  
  it('Maintains focus correctly', () => {
    cy.get('.modal-trigger').focus().click();
    cy.focused().should('have.class', 'modal-close');
    
    cy.get('.modal-close').click();
    cy.focused().should('have.class', 'modal-trigger');
  });
});
```

## 📊 Performance Impact Testing

### Accessibility Feature Performance
```javascript
// Test performance impact of a11y features
const a11yPerformanceTests = {
  'Focus indicators': {
    css: '.5kb',
    runtime: '0ms',
    impact: 'negligible'
  },
  'Skip links': {
    css: '.2kb',
    runtime: '0ms',
    impact: 'negligible'
  },
  'ARIA live regions': {
    css: '0kb',
    runtime: '<5ms per update',
    impact: 'minimal'
  },
  'Reduced motion': {
    css: '.3kb',
    runtime: '0ms',
    impact: 'improves performance'
  }
};
```

## 🏁 Pre-Launch Checklist

### Comprehensive Testing Protocol
```markdown
## Final Accessibility Audit

### Automated Tests ✓
- [ ] axe DevTools: 0 violations
- [ ] Lighthouse: 95+ accessibility score
- [ ] Pa11y: All pages pass WCAG AA
- [ ] Jest a11y tests: 100% passing

### Manual Tests ✓
- [ ] Keyboard navigation: Complete journey
- [ ] Screen reader: NVDA full test
- [ ] Screen reader: JAWS spot check
- [ ] Screen reader: VoiceOver iOS
- [ ] Color contrast: Manual verification
- [ ] Zoom to 200%: No horizontal scroll

### Browser/Device Matrix ✓
- [ ] Chrome + NVDA (Windows)
- [ ] Firefox + NVDA (Windows)
- [ ] Safari + VoiceOver (macOS)
- [ ] Safari + VoiceOver (iOS)
- [ ] Chrome + TalkBack (Android)

### Documentation ✓
- [ ] Accessibility statement published
- [ ] Known issues documented
- [ ] Keyboard shortcuts listed
- [ ] Contact for a11y feedback

### Performance ✓
- [ ] A11y features don't impact speed
- [ ] Animations respect prefers-reduced-motion
- [ ] Focus indicators don't cause reflow
```

## 🚨 Common Issues & Fixes

### Issue Resolution Guide
```javascript
const accessibilityFixes = {
  'color-contrast': {
    issue: 'Insufficient color contrast ratio',
    fix: 'Adjust colors to meet 4.5:1 (normal) or 3:1 (large text)',
    tool: 'WebAIM Contrast Checker'
  },
  'empty-heading': {
    issue: 'Empty heading elements',
    fix: 'Remove empty headings or add content',
    code: '<h2>Section Title</h2> <!-- Never empty -->'
  },
  'button-name': {
    issue: 'Button without accessible name',
    fix: 'Add text content or aria-label',
    code: '<button aria-label="Close dialog">×</button>'
  },
  'image-alt': {
    issue: 'Images without alt text',
    fix: 'Add descriptive alt or empty alt for decorative',
    code: '<img src="..." alt="Description of image">'
  }
};
```