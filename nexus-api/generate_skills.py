import json
import random

adjectives = ["Autonomous", "Intelligent", "Dynamic", "Semantic", "Cognitive", "Adaptive", "Predictive", "Neural", "Contextual", "Generative"]
verbs = ["Analyzer", "Synthesizer", "Orchestrator", "Planner", "Reasoner", "Optimizer", "Extractor", "Generator", "Executor", "Delegator", "Evaluator"]
domains = ["Web", "API", "Database", "Code", "Memory", "Knowledge", "DOM", "Terminal", "System", "Cloud", "Graph", "Vector"]
focuses = ["Operations", "Pipelines", "Workflows", "Automation", "Integration", "Processing", "Retrieval", "Synthesis", "Execution"]

tags_pool = ["agent", "llm", "ai", "automation", "reasoning", "planning", "memory", "tool-use", "context", "orchestration", "cognitive", "autonomous", "integration", "execution", "synthesis"]

authors = ["nexus-core", "agent-labs", "auto-dev", "cognitive-systems", "ai-tools-org"]

def generate_skill(index):
    adj = random.choice(adjectives)
    verb = random.choice(verbs)
    domain = random.choice(domains)
    focus = random.choice(focuses)
    
    name = f"{adj} {domain} {verb}"
    skill_id = f"agent-skill-{domain.lower()}-{verb.lower().replace(' ', '-')}-{index}"
    
    description = f"Provides agents with {adj.lower()} capabilities for {domain.lower()} {focus.lower()}. Enables seamless task execution."
    
    tags = random.sample(tags_pool, k=random.randint(3, 6))
    if "agent" not in tags:
        tags.insert(0, "agent")
        
    skill_md = f"""# {name}

## Description
Agent-centric skill that provides {description.lower()}

## Capabilities
- Autonomous {domain.lower()} interaction
- Cognitive {focus.lower()} processing
- Seamless integration with LLM context windows
- Self-healing execution paths

## Usage
```
Input: {{ "task": "goal description", "context": "current state" }}
Output: {{ "result": "...", "confidence": 0.95, "next_steps": [] }}
```
"""
    
    perms = {"network": random.choice(["none", "external", "internal-only"]), 
             "filesystem": random.choice(["none", "read-only", "read-write"]),
             "execution": random.choice(["none", "sandboxed", "containerized"])}
    
    skill = {
        "skill_id": skill_id,
        "name": name,
        "version": f"{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}",
        "description": description,
        "author": random.choice(authors),
        "tags": tags,
        "skill_md_content": skill_md,
        "permissions": perms,
        "price_per_use": round(random.uniform(0.001, 0.05), 3),
        "risk_score": random.randint(5, 45)
    }
    return skill

def generate_100_skills():
    return [generate_skill(i) for i in range(1, 101)]

if __name__ == "__main__":
    skills = generate_100_skills()
    print(f"Generated {len(skills)} skills.")
