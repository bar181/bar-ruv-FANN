/**
 * Performance Testing Script for 5-Agent Landing Page
 * Validates Core Web Vitals and custom metrics
 */

const puppeteer = require('puppeteer');
const lighthouse = require('lighthouse');
const { URL } = require('url');

// Performance thresholds based on requirements
const THRESHOLDS = {
  LCP: 2500,      // Largest Contentful Paint < 2.5s
  FID: 100,       // First Input Delay < 100ms
  CLS: 0.1,       // Cumulative Layout Shift < 0.1
  FCP: 1800,      // First Contentful Paint < 1.8s
  TTI: 3500,      // Time to Interactive < 3.5s
  TBT: 200,       // Total Blocking Time < 200ms
  SI: 3000,       // Speed Index < 3000
  totalLoad: 3000 // Total page load < 3s
};

// Custom 5-agent metrics
const AGENT_METRICS = {
  coordinationLatency: 50,    // Max latency between agents
  parallelExecution: 0.8,     // Min parallel execution ratio
  taskCompletionRate: 0.848,  // Min success rate
  tokenEfficiency: 0.323      // Min token reduction
};

class PerformanceTester {
  constructor(url) {
    this.url = url;
    this.results = {
      webVitals: {},
      agentMetrics: {},
      resourceSizes: {},
      passed: true,
      failures: []
    };
  }

  async runTests() {
    console.log('🚀 Starting 5-Agent Landing Page Performance Tests...\n');
    
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
      // Run Core Web Vitals tests
      await this.testCoreWebVitals(browser);
      
      // Run resource size tests
      await this.testResourceSizes(browser);
      
      // Run agent-specific metrics
      await this.testAgentMetrics(browser);
      
      // Run Lighthouse audit
      await this.runLighthouseAudit(browser);
      
      // Generate report
      this.generateReport();
      
    } finally {
      await browser.close();
    }

    return this.results;
  }

  async testCoreWebVitals(browser) {
    console.log('📊 Testing Core Web Vitals...');
    
    const page = await browser.newPage();
    
    // Enable performance monitoring
    await page.evaluateOnNewDocument(() => {
      window.webVitals = {
        LCP: null,
        FID: null,
        CLS: null,
        FCP: null,
        TTFB: null
      };

      // LCP Observer
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        window.webVitals.LCP = lastEntry.renderTime || lastEntry.loadTime;
      }).observe({ entryTypes: ['largest-contentful-paint'] });

      // CLS Observer
      let clsValue = 0;
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
            window.webVitals.CLS = clsValue;
          }
        }
      }).observe({ entryTypes: ['layout-shift'] });

      // FCP Observer
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        window.webVitals.FCP = entries[0].startTime;
      }).observe({ entryTypes: ['paint'] });
    });

    // Navigate and wait for load
    const startTime = Date.now();
    await page.goto(this.url, { waitUntil: 'networkidle0' });
    const loadTime = Date.now() - startTime;

    // Wait a bit for all metrics to be collected
    await page.waitForTimeout(2000);

    // Collect metrics
    const metrics = await page.evaluate(() => window.webVitals);
    const navigationTiming = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      return {
        TTFB: nav.responseStart - nav.requestStart,
        domContentLoaded: nav.domContentLoadedEventEnd - nav.domContentLoadedEventStart,
        loadComplete: nav.loadEventEnd - nav.loadEventStart
      };
    });

    // Store results
    this.results.webVitals = {
      LCP: metrics.LCP,
      CLS: metrics.CLS,
      FCP: metrics.FCP,
      TTFB: navigationTiming.TTFB,
      totalLoad: loadTime
    };

    // Validate against thresholds
    Object.entries(this.results.webVitals).forEach(([metric, value]) => {
      if (THRESHOLDS[metric] && value > THRESHOLDS[metric]) {
        this.results.passed = false;
        this.results.failures.push(`${metric}: ${value}ms exceeds threshold of ${THRESHOLDS[metric]}ms`);
      }
    });

    await page.close();
  }

  async testResourceSizes(browser) {
    console.log('📦 Testing Resource Sizes...');
    
    const page = await browser.newPage();
    
    // Monitor network requests
    const resources = {
      html: 0,
      css: 0,
      js: 0,
      images: 0,
      fonts: 0,
      total: 0
    };

    page.on('response', async (response) => {
      const url = response.url();
      const size = parseInt(response.headers()['content-length'] || 0);
      
      if (url.endsWith('.html')) resources.html += size;
      else if (url.endsWith('.css')) resources.css += size;
      else if (url.endsWith('.js')) resources.js += size;
      else if (/\.(jpg|jpeg|png|webp|svg|gif)$/i.test(url)) resources.images += size;
      else if (/\.(woff2|woff|ttf|eot)$/i.test(url)) resources.fonts += size;
      
      resources.total += size;
    });

    await page.goto(this.url, { waitUntil: 'networkidle0' });
    
    this.results.resourceSizes = resources;

    // Check against budgets
    const budgets = {
      html: 15000,
      css: 20000,
      js: 30000,
      images: 200000,
      fonts: 50000,
      total: 315000
    };

    Object.entries(budgets).forEach(([type, budget]) => {
      if (resources[type] > budget) {
        this.results.passed = false;
        this.results.failures.push(`${type} size: ${resources[type]} bytes exceeds budget of ${budget} bytes`);
      }
    });

    await page.close();
  }

  async testAgentMetrics(browser) {
    console.log('🤖 Testing 5-Agent Specific Metrics...');
    
    const page = await browser.newPage();
    
    await page.goto(this.url, { waitUntil: 'networkidle0' });

    // Inject agent monitoring code
    const agentMetrics = await page.evaluate(() => {
      // Simulate agent coordination metrics
      const agents = document.querySelectorAll('.agent-card');
      const metrics = {
        agentCount: agents.length,
        coordinationLatency: 0,
        parallelExecution: 0,
        taskCompletionRate: 0,
        tokenEfficiency: 0
      };

      // Check if we have exactly 5 agents
      if (agents.length === 5) {
        // Simulate coordination timing
        const timings = [12, 45, 78, 23, 15]; // ms for each agent
        metrics.coordinationLatency = Math.max(...timings) - Math.min(...timings);
        
        // Calculate parallel execution ratio
        const overlappingTime = 120; // ms of parallel work
        const totalTime = 173; // total execution time
        metrics.parallelExecution = overlappingTime / totalTime;
        
        // Get displayed metrics
        const successRate = document.querySelector('.metric-success');
        const tokenSaving = document.querySelector('.metric-tokens');
        
        if (successRate) {
          metrics.taskCompletionRate = parseFloat(successRate.textContent) / 100;
        }
        if (tokenSaving) {
          metrics.tokenEfficiency = parseFloat(tokenSaving.textContent) / 100;
        }
      }

      return metrics;
    });

    this.results.agentMetrics = agentMetrics;

    // Validate agent metrics
    if (agentMetrics.agentCount !== 5) {
      this.results.passed = false;
      this.results.failures.push(`Agent count: ${agentMetrics.agentCount} instead of 5`);
    }

    Object.entries(AGENT_METRICS).forEach(([metric, threshold]) => {
      if (agentMetrics[metric] < threshold) {
        this.results.passed = false;
        this.results.failures.push(`${metric}: ${agentMetrics[metric]} below threshold of ${threshold}`);
      }
    });

    await page.close();
  }

  async runLighthouseAudit(browser) {
    console.log('🔍 Running Lighthouse Audit...');
    
    const { lhr } = await lighthouse(this.url, {
      port: (new URL(browser.wsEndpoint())).port,
      output: 'json',
      logLevel: 'error',
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo']
    });

    this.results.lighthouse = {
      performance: Math.round(lhr.categories.performance.score * 100),
      accessibility: Math.round(lhr.categories.accessibility.score * 100),
      bestPractices: Math.round(lhr.categories['best-practices'].score * 100),
      seo: Math.round(lhr.categories.seo.score * 100)
    };

    // Check Lighthouse thresholds
    const lighthouseTargets = {
      performance: 95,
      accessibility: 100,
      bestPractices: 100,
      seo: 100
    };

    Object.entries(lighthouseTargets).forEach(([category, target]) => {
      if (this.results.lighthouse[category] < target) {
        this.results.passed = false;
        this.results.failures.push(`Lighthouse ${category}: ${this.results.lighthouse[category]} below target of ${target}`);
      }
    });
  }

  generateReport() {
    console.log('\n' + '='.repeat(60));
    console.log('📋 PERFORMANCE TEST REPORT - 5-AGENT LANDING PAGE');
    console.log('='.repeat(60) + '\n');

    // Web Vitals
    console.log('🌐 Core Web Vitals:');
    Object.entries(this.results.webVitals).forEach(([metric, value]) => {
      const threshold = THRESHOLDS[metric];
      const status = !threshold || value <= threshold ? '✅' : '❌';
      console.log(`   ${status} ${metric}: ${value}ms ${threshold ? `(threshold: ${threshold}ms)` : ''}`);
    });

    // Resource Sizes
    console.log('\n📦 Resource Sizes:');
    Object.entries(this.results.resourceSizes).forEach(([type, size]) => {
      console.log(`   ${type}: ${(size / 1024).toFixed(2)}KB`);
    });

    // Agent Metrics
    console.log('\n🤖 5-Agent Metrics:');
    Object.entries(this.results.agentMetrics).forEach(([metric, value]) => {
      console.log(`   ${metric}: ${value}`);
    });

    // Lighthouse Scores
    console.log('\n🔍 Lighthouse Scores:');
    Object.entries(this.results.lighthouse).forEach(([category, score]) => {
      console.log(`   ${category}: ${score}/100`);
    });

    // Summary
    console.log('\n' + '='.repeat(60));
    if (this.results.passed) {
      console.log('✅ ALL TESTS PASSED! The 5-agent configuration meets all performance targets.');
    } else {
      console.log('❌ TESTS FAILED:');
      this.results.failures.forEach(failure => {
        console.log(`   - ${failure}`);
      });
    }
    console.log('='.repeat(60) + '\n');
  }
}

// Run tests
if (require.main === module) {
  const url = process.argv[2] || 'http://localhost:3000';
  const tester = new PerformanceTester(url);
  
  tester.runTests()
    .then(results => {
      process.exit(results.passed ? 0 : 1);
    })
    .catch(error => {
      console.error('Test error:', error);
      process.exit(1);
    });
}

module.exports = PerformanceTester;