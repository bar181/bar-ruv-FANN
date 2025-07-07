# 1-Agent Swarm Best Practices & Orchestration Guide

## Overview
A 1-agent swarm provides swarm infrastructure benefits (memory, hooks, metrics) without multi-agent coordination overhead. It's ideal for measuring pure swarm overhead and leveraging automation features.

## Optimal 1-Agent Setup with BatchTool

### 🚀 The Golden Pattern (Always Use This)

```javascript
// EVERYTHING in ONE BatchTool message - this is MANDATORY
[BatchTool - Single Message]:
  mcp__ruv-swarm__swarm_init { 
    topology: "star",           // Minimal overhead topology
    maxAgents: 1,              // Single agent limit
    strategy: "specialized"     // Focused execution
  }
  mcp__ruv-swarm__agent_spawn { 
    type: "coder",             // Or "coordinator" or "researcher"
    name: "solo-developer",
    capabilities: ["coding", "testing", "documentation", "review"]
  }
  mcp__ruv-swarm__memory_usage {
    action: "store",
    key: "swarm/config",
    value: { "mode": "single-agent", "purpose": "baseline-testing" }
  }
  mcp__ruv-swarm__task_orchestrate { 
    task: "[Your task description]",
    strategy: "adaptive",
    maxAgents: 1
  }
```

## Agent Type Selection

### Config A1.1: Single Coder
```javascript
mcp__ruv-swarm__agent_spawn { 
  type: "coder",
  name: "full-stack-developer",
  capabilities: ["implementation", "testing", "debugging", "optimization"]
}
```
**Use for**: Code generation, debugging, implementation tasks

### Config A1.2: Single Coordinator
```javascript
mcp__ruv-swarm__agent_spawn { 
  type: "coordinator",
  name: "technical-lead",
  capabilities: ["architecture", "planning", "review", "integration"]
}
```
**Use for**: Architecture design, planning, code review tasks

### Config A1.3: Single Researcher
```javascript
mcp__ruv-swarm__agent_spawn { 
  type: "researcher",
  name: "technical-analyst",
  capabilities: ["analysis", "research", "documentation", "evaluation"]
}
```
**Use for**: Research, analysis, documentation tasks

## Key Benefits of 1-Agent Swarm

### 1. Memory Persistence
```javascript
// Store context at start
mcp__ruv-swarm__memory_usage {
  action: "store",
  key: "project/context",
  value: { 
    "task": "implement feature",
    "decisions": ["use async", "add caching"],
    "timestamp": Date.now()
  }
}

// Retrieve in future sessions
mcp__ruv-swarm__memory_usage {
  action: "retrieve",
  key: "project/context"
}
```

### 2. Automated Hooks
Configured in `.claude/settings.json`:
- **Pre-task**: Loads previous context
- **Post-edit**: Auto-formats code
- **Neural training**: Learns from patterns
- **Session persistence**: Saves state

### 3. Performance Metrics
```javascript
// Check single agent metrics
mcp__ruv-swarm__agent_metrics { 
  metric: "all" 
}

// Monitor overhead
mcp__ruv-swarm__swarm_monitor { 
  duration: 10, 
  interval: 2 
}
```

## Orchestration Pattern for 1-Agent

### The Orchestrator Role
Even with 1 agent, the orchestrator (Claude Code) provides:
1. **Task Management**: Structures the approach
2. **Memory Coordination**: Manages persistent state
3. **Hook Triggering**: Ensures automation runs
4. **Metric Collection**: Tracks performance

### Example Workflow

```javascript
// Step 1: Initialize (ALWAYS in BatchTool)
[BatchTool]:
  mcp__ruv-swarm__swarm_init { topology: "star", maxAgents: 1, strategy: "specialized" }
  mcp__ruv-swarm__agent_spawn { type: "coder", name: "developer" }
  
// Step 2: The agent MUST use coordination hooks
Task {
  prompt: `
    You are the developer agent in a 1-agent swarm.
    
    MANDATORY: Use these coordination commands:
    1. START: npx ruv-swarm hook pre-task --description "[task]"
    2. AFTER EACH FILE: npx ruv-swarm hook post-edit --file "[file]"
    3. END: npx ruv-swarm hook post-task --task-id "[task]"
    
    Your task: [Implement the specific feature]
  `
}

// Step 3: Claude Code monitors and coordinates
mcp__ruv-swarm__swarm_status { verbose: true }
mcp__ruv-swarm__task_results { taskId: "[task-id]" }
```

## Overhead Measurement

### Expected Overhead for 1-Agent
- **Initialization**: ~2-3 seconds
- **Memory operations**: <1 second each
- **Hook execution**: ~1-2 seconds per hook
- **Total overhead**: 5-10% over baseline

### Measuring Pure Swarm Cost
```javascript
// Baseline: Direct Claude Code execution
Time: X seconds

// 1-Agent Swarm: Same task with infrastructure
Time: X + overhead seconds

// Overhead percentage: ((X + overhead) - X) / X * 100
```

## Best Practices Summary

### ✅ DO:
1. **Always use BatchTool** for all operations in one message
2. **Choose appropriate agent type** for the task
3. **Leverage memory** for context persistence
4. **Use hooks** for automation benefits
5. **Monitor metrics** to track overhead

### ❌ DON'T:
1. **Don't spawn multiple messages** - breaks parallel execution
2. **Don't skip orchestration** - loses swarm benefits
3. **Don't ignore memory** - main benefit of 1-agent swarm
4. **Don't disable hooks** - free automation value

## When to Use 1-Agent Swarm

### Ideal Scenarios:
- **Baseline testing**: Measure pure swarm overhead
- **Simple tasks with memory needs**: Context persistence
- **Automation benefits**: Code formatting, neural training
- **Learning tasks**: Neural pattern development

### Not Recommended For:
- **One-off tasks**: Use baseline if no persistence needed
- **When speed critical**: 5-10% overhead may matter
- **No automation needed**: Baseline is simpler

## Example Test Configuration

```javascript
// Complete 1-agent test setup
[BatchTool]:
  // Initialize swarm
  mcp__ruv-swarm__swarm_init { 
    topology: "star", 
    maxAgents: 1, 
    strategy: "specialized" 
  }
  
  // Spawn agent based on task type
  mcp__ruv-swarm__agent_spawn { 
    type: "coder",  // Change based on task
    name: "solo-agent",
    capabilities: ["full-spectrum"]
  }
  
  // Store test context
  mcp__ruv-swarm__memory_usage {
    action: "store",
    key: "test/1-agent/start",
    value: { 
      "test_type": "simple",
      "start_time": Date.now()
    }
  }
  
  // Start monitoring
  mcp__ruv-swarm__swarm_monitor { 
    duration: 300,  // 5 minutes
    interval: 5 
  }
  
  // Orchestrate task
  mcp__ruv-swarm__task_orchestrate { 
    task: "Complete test 1a: merge sorted lists",
    strategy: "adaptive",
    priority: "high"
  }
```

## Conclusion

1-agent swarms provide a sweet spot between baseline simplicity and multi-agent power. They offer persistence, automation, and metrics with minimal coordination overhead, making them ideal for:
- Measuring swarm infrastructure cost
- Simple tasks that benefit from memory
- Leveraging automation without complexity
- Building neural patterns over time

The key is proper setup using BatchTool and understanding that the orchestrator (Claude Code) still plays a vital coordination role, even with just one agent.