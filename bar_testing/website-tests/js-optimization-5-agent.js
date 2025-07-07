/**
 * Performance-Optimized JavaScript for 5-Agent Landing Page
 * Implements lazy loading, efficient animations, and metric tracking
 */

// Performance monitoring setup
const performanceMetrics = {
  startTime: performance.now(),
  interactions: 0,
  agentActivations: 0
};

// Lazy Loading with Intersection Observer
const lazyLoadElements = () => {
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        
        // Load image
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute('data-src');
        }
        
        // Load srcset
        if (img.dataset.srcset) {
          img.srcset = img.dataset.srcset;
          img.removeAttribute('data-srcset');
        }
        
        img.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  }, {
    rootMargin: '50px 0px',
    threshold: 0.01
  });

  // Observe all lazy images
  document.querySelectorAll('img[data-src]').forEach(img => {
    imageObserver.observe(img);
  });
};

// Efficient scroll handling with RAF throttling
let scrollRAF = null;
const handleScroll = () => {
  if (scrollRAF) return;
  
  scrollRAF = requestAnimationFrame(() => {
    const scrollY = window.scrollY;
    const windowHeight = window.innerHeight;
    
    // Parallax effect for hero (GPU accelerated)
    const hero = document.querySelector('.hero-content');
    if (hero && scrollY < windowHeight) {
      hero.style.transform = `translateY(${scrollY * 0.5}px) translateZ(0)`;
      hero.style.opacity = 1 - (scrollY / windowHeight);
    }
    
    // Update progress indicators
    updateProgressBars(scrollY, windowHeight);
    
    scrollRAF = null;
  });
};

// Debounced resize handler
let resizeTimeout;
const handleResize = () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(() => {
    updateAgentGrid();
  }, 300);
};

// 5-Agent Performance Metrics Animation
const animateMetrics = () => {
  const metrics = [
    { selector: '.metric-time', value: -34.52, suffix: '%', duration: 1500 },
    { selector: '.metric-speed', value: 2.8, suffix: 'x', duration: 1200 },
    { selector: '.metric-success', value: 84.8, suffix: '%', duration: 1800 },
    { selector: '.metric-tokens', value: 32.3, suffix: '%', duration: 1600 }
  ];

  metrics.forEach(({ selector, value, suffix, duration }) => {
    const element = document.querySelector(selector);
    if (!element) return;

    const startTime = performance.now();
    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const current = value * easeOutQuart;
      
      element.textContent = current.toFixed(1) + suffix;
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  });
};

// Agent status updates with efficient DOM manipulation
const updateAgentStatus = (agentId, status) => {
  const agent = document.querySelector(`[data-agent-id="${agentId}"]`);
  if (!agent) return;
  
  const statusEl = agent.querySelector('.agent-status');
  statusEl.dataset.status = status;
  
  // Track activation metrics
  if (status === 'active') {
    performanceMetrics.agentActivations++;
  }
};

// Batch DOM updates for agent grid
const updateAgentGrid = () => {
  const fragment = document.createDocumentFragment();
  const grid = document.querySelector('.agent-grid');
  
  // Example: Update multiple agents efficiently
  const updates = getAgentUpdates(); // Assume this returns update data
  
  updates.forEach(update => {
    const agentEl = createAgentElement(update);
    fragment.appendChild(agentEl);
  });
  
  // Single DOM update
  grid.appendChild(fragment);
};

// Progress bars with CSS custom properties
const updateProgressBars = (scrollY, windowHeight) => {
  const progressBars = document.querySelectorAll('.performance-fill');
  
  progressBars.forEach(bar => {
    const targetValue = parseFloat(bar.dataset.value) / 100;
    const elementTop = bar.offsetTop;
    const isVisible = scrollY + windowHeight > elementTop;
    
    if (isVisible && !bar.classList.contains('animated')) {
      bar.style.setProperty('--fill-percent', targetValue);
      bar.classList.add('animated');
    }
  });
};

// Web Workers for heavy computations
const initWorker = () => {
  if (typeof Worker === 'undefined') return;
  
  // Inline worker for metric calculations
  const workerCode = `
    self.addEventListener('message', (e) => {
      const { type, data } = e.data;
      
      if (type === 'calculate-metrics') {
        // Simulate complex calculation
        const result = {
          efficiency: data.agents * 0.168,
          throughput: data.tasks / data.time,
          optimization: Math.min(data.parallelism * 0.285, 1)
        };
        
        self.postMessage({ type: 'metrics-result', data: result });
      }
    });
  `;
  
  const blob = new Blob([workerCode], { type: 'application/javascript' });
  const worker = new Worker(URL.createObjectURL(blob));
  
  worker.addEventListener('message', (e) => {
    if (e.data.type === 'metrics-result') {
      displayCalculatedMetrics(e.data.data);
    }
  });
  
  return worker;
};

// Performance monitoring
const measurePerformance = () => {
  if ('PerformanceObserver' in window) {
    // LCP monitoring
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
    });
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    
    // FID monitoring
    const fidObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        console.log('FID:', entry.processingStart - entry.startTime);
      }
    });
    fidObserver.observe({ entryTypes: ['first-input'] });
  }
};

// Resource hints management
const preloadCriticalResources = () => {
  const resources = [
    { href: '/fonts/inter-subset.woff2', as: 'font', type: 'font/woff2' },
    { href: '/img/hero-1200w.webp', as: 'image' }
  ];
  
  resources.forEach(({ href, as, type }) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = href;
    link.as = as;
    if (type) link.type = type;
    if (as === 'font') link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  });
};

// Initialize on DOM ready
const init = () => {
  // Start performance measurement
  measurePerformance();
  
  // Preload critical resources
  preloadCriticalResources();
  
  // Initialize lazy loading
  lazyLoadElements();
  
  // Attach event listeners with passive flag
  window.addEventListener('scroll', handleScroll, { passive: true });
  window.addEventListener('resize', handleResize, { passive: true });
  
  // Initialize worker for heavy computations
  const metricsWorker = initWorker();
  
  // Animate metrics when visible
  const metricsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateMetrics();
        metricsObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });
  
  const metricsSection = document.querySelector('.performance-metrics');
  if (metricsSection) {
    metricsObserver.observe(metricsSection);
  }
  
  // Log initialization metrics
  console.log('Page initialized in:', performance.now() - performanceMetrics.startTime, 'ms');
};

// Use DOMContentLoaded for faster initialization
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Export for module usage
export { 
  updateAgentStatus, 
  animateMetrics, 
  measurePerformance 
};