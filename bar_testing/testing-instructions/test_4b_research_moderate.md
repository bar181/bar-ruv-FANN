# Test 4b: Research & Analysis - Architecture Decision

## 🟡 Difficulty: MODERATE
**Expected Duration**: 5-8 minutes per configuration

## Test Overview
This test evaluates research and architectural decision-making for a realistic scenario.

## Test Prompt
```
Analyze and recommend a caching strategy for an e-commerce platform:

Context:
- 50,000 daily active users
- Product catalog: 100,000 items
- User sessions with shopping carts
- Personalized recommendations
- Real-time inventory updates
- Global presence (3 regions)

Compare these caching solutions:
1. Redis
2. Memcached
3. Hazelcast
4. Application-level caching (in-memory)

Analyze each for:
- Performance at scale
- Data persistence options
- Clustering/replication capabilities
- Cost implications
- Implementation complexity
- Specific e-commerce features support

Deliverables:
1. Feature comparison matrix
2. Architecture diagram for recommended solution
3. Caching strategy for different data types:
   - Product catalog
   - User sessions
   - Shopping carts
   - Recommendations
4. Implementation code snippet for cart caching
5. Migration plan from current no-cache setup

Consider: Some data needs persistence, some is ephemeral, 
and inventory must be real-time accurate.
```

## Expected Deliverables
- Detailed comparison matrix
- Architecture diagram (ASCII or description)
- Caching strategy per data type
- Code example
- Phased migration approach
- Cost-benefit analysis

## Test Configurations

### 1. Claude Native (Baseline)
- **Setup**: Direct prompt
- **Expected Time**: 3-4 minutes

### 2. Swarm Config A: Simple Parallel (3 agents, flat)
- **Setup**: 
  ```javascript
  mcp__ruv-swarm__swarm_init { topology: "mesh", maxAgents: 3, strategy: "balanced" }
  mcp__ruv-swarm__agent_spawn { type: "researcher", name: "cache-expert" }
  mcp__ruv-swarm__agent_spawn { type: "analyst", name: "architecture-designer" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "implementation-specialist" }
  ```
- **Expected Time**: 4-6 minutes

### 3. Swarm Config B: Hierarchical (3 agents)
- **Expected Time**: 5-7 minutes

### 4. Swarm Config C: Specialized Team (5 agents)
- **Setup**: Add cost analyst and migration planner
- **Expected Time**: 6-8 minutes

## Evaluation Metrics

### Assessment Checklist (5 minutes)
- [ ] Comprehensive comparison
- [ ] Appropriate recommendations
- [ ] Considers all requirements
- [ ] Practical implementation approach
- [ ] Cost awareness
- [ ] Clear architecture

### Quality Indicators
- Depth of analysis
- Practical considerations
- Technical accuracy
- Business alignment
- Implementation feasibility

## Notes
- Real-world scenario with trade-offs
- Multiple valid approaches
- Tests system design thinking