# Test 4a: Research & Analysis - Technology Comparison

## 🟢 Difficulty: SIMPLE
**Expected Duration**: 2-3 minutes per configuration

## Test Overview
This test evaluates basic research and comparison skills with a focused scope.

## Test Prompt
```
Compare Python async frameworks for building a simple REST API:

Compare these 3 frameworks:
1. FastAPI
2. Aiohttp
3. Sanic

For each framework, briefly analyze:
- Ease of use for beginners
- Performance characteristics
- Built-in features (validation, docs, etc.)
- Community support

Provide:
1. A comparison table
2. Simple "Hello World" API example for each
3. Recommendation based on these criteria:
   - Team has moderate Python experience
   - Need automatic API documentation
   - Expecting <1000 requests/second
   - Want minimal dependencies

Keep response concise - focus on practical differences.
```

## Expected Deliverables
- Comparison table
- Code examples (minimal)
- Clear recommendation with reasoning
- 1-2 paragraph summary

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct prompt
- **Expected Time**: 60-90 seconds

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "researcher", name: "framework-analyst" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "example-creator" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "recommendation-maker" }
  ```
- **Expected Time**: 90-120 seconds

### 3. Swarm Config B: Hierarchical (3 agents)
- **Expected Time**: 2-3 minutes

## Evaluation Metrics

### Quick Assessment (2 minutes)
- [ ] All frameworks covered
- [ ] Accurate information
- [ ] Working code examples
- [ ] Clear recommendation
- [ ] Addresses all criteria

### Quality Indicators
- Information accuracy
- Practical focus
- Clear reasoning
- Concise presentation

## Notes
- Limited scope keeps time manageable
- Clear criteria for evaluation
- Tests synthesis and recommendation skills