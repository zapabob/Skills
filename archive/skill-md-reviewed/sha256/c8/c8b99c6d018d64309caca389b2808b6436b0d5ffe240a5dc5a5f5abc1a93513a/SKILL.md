---
name: cursor-web-deepresearch-plan-mode
description: Create comprehensive execution plans using Cursor's MCP browser tools for deep web research. Integrates web search, content analysis, multi-source validation, and intelligent plan generation. Use when tasks require research-backed planning, multi-step coordination, or when explicitly requesting research-based plans.
---

# Cursor Web Deepresearch Plan Mode

## Overview

This skill combines Cursor's MCP browser tools with deep research methodology and intelligent plan generation. It performs comprehensive web research, validates information across multiple sources, and creates execution plans informed by research findings.

## Core Features

### 1. Web Research Integration
- **Browser-based search**: Use `browser_search` for initial queries
- **Content extraction**: Use `browser_snapshot` to analyze page content
- **Multi-tab navigation**: Manage multiple research tabs with `browser_tabs`
- **Deep dive analysis**: Navigate through linked resources

### 2. Research Methodology
- **Multi-source validation**: Cross-reference information from 3+ sources
- **Credibility assessment**: Evaluate source authority and reliability
- **Contradiction detection**: Identify and resolve conflicting information
- **Timeline analysis**: Track information recency and evolution

### 3. Plan Generation
- **Research-informed planning**: Create plans based on research findings
- **Dependency analysis**: Identify step dependencies from research
- **Risk assessment**: Evaluate risks based on research insights
- **Best practice integration**: Incorporate researched best practices

## When to Use

Use this skill when:
- ✅ Task requires research before planning
- ✅ Multiple information sources need validation
- ✅ Best practices or patterns need discovery
- ✅ Complex multi-step tasks with research dependencies
- ✅ User explicitly requests research-based planning

Skip for:
- ❌ Tasks with clear, well-known solutions
- ❌ Single-step operations
- ❌ No research needed

## Research Workflow

### Step 1: Initial Search

```python
# Use browser_search for initial query
search_query = "best practices for [task domain] implementation"
browser_search(query=search_query, max_results=10)

# Get search results
tabs = browser_tabs(action="list")
```

### Step 2: Content Analysis

```python
# Navigate to promising results
for tab in tabs[:5]:  # Top 5 results
    browser_navigate(url=tab["url"])
    browser_lock()  # Lock tab for interaction

    # Get page content
    snapshot = browser_snapshot()

    # Analyze content
    content_analysis = analyze_content(snapshot)

    browser_unlock()
```

### Step 3: Multi-Source Validation

```python
# Search for validation queries
validation_queries = [
    f"{topic} alternative approaches",
    f"{topic} comparison analysis",
    f"{topic} expert opinions"
]

for query in validation_queries:
    browser_search(query=query, max_results=5)
    # Analyze and cross-reference
```

### Step 4: Information Synthesis

```python
# Synthesize research findings
research_summary = {
    "main_approaches": extract_approaches(all_snapshots),
    "best_practices": extract_best_practices(all_snapshots),
    "common_pitfalls": extract_pitfalls(all_snapshots),
    "recommended_tools": extract_tools(all_snapshots),
    "credibility_scores": assess_credibility(all_sources)
}
```

## Plan Creation from Research

### Research-Informed Plan Structure

```python
def create_research_plan(task_description, research_summary):
    plan = {
        "id": generate_plan_id(),
        "title": task_description,
        "research_basis": research_summary,
        "steps": [],
        "sources": research_summary["sources"],
        "confidence_level": calculate_confidence(research_summary)
    }

    # Generate steps based on research
    approaches = research_summary["main_approaches"]
    best_practice = select_best_approach(approaches, research_summary)

    plan["steps"] = decompose_approach_to_steps(
        best_practice,
        research_summary["best_practices"]
    )

    return plan
```

### Step Generation

```python
def decompose_approach_to_steps(approach, best_practices):
    steps = []

    # Research step (if needed)
    if approach.get("requires_research"):
        steps.append({
            "id": "research",
            "name": f"Research {approach['name']} implementation details",
            "status": "pending",
            "research_needed": True,
            "research_queries": approach.get("research_queries", [])
        })

    # Implementation steps from best practices
    for practice in best_practices:
        steps.append({
            "id": f"step-{len(steps)+1}",
            "name": practice["action"],
            "status": "pending",
            "dependencies": practice.get("dependencies", []),
            "best_practice_source": practice["source_url"],
            "estimated_time": practice.get("time_estimate")
        })

    # Validation step
    steps.append({
        "id": "validation",
        "name": "Validate implementation against research findings",
        "status": "pending",
        "dependencies": [s["id"] for s in steps[:-1]]
    })

    return steps
```

## Browser Tool Usage Patterns

### Pattern 1: Sequential Research

```python
# Search → Navigate → Analyze → Next
def sequential_research(query):
    browser_search(query=query)
    tabs = browser_tabs(action="list")

    for tab in tabs[:3]:
        browser_navigate(url=tab["url"])
        browser_lock()
        snapshot = browser_snapshot()
        analyze(snapshot)
        browser_unlock()
```

### Pattern 2: Parallel Research

```python
# Open multiple tabs → Analyze in parallel
def parallel_research(queries):
    tabs = []
    for query in queries:
        browser_search(query=query)
        new_tabs = browser_tabs(action="list")
        tabs.extend(new_tabs[:2])  # Top 2 per query

    # Analyze all tabs
    for tab in tabs:
        browser_navigate(url=tab["url"])
        browser_lock()
        snapshot = browser_snapshot()
        analyze(snapshot)
        browser_unlock()
```

### Pattern 3: Deep Dive

```python
# Follow links for deeper research
def deep_dive_research(initial_url):
    browser_navigate(url=initial_url)
    browser_lock()
    snapshot = browser_snapshot()

    # Extract links
    links = extract_relevant_links(snapshot)

    # Follow promising links
    for link in links[:5]:
        browser_navigate(url=link)
        snapshot = browser_snapshot()
        analyze(snapshot)
        browser_navigate_back()  # Return to initial page

    browser_unlock()
```

## Research Quality Assessment

### Source Credibility Scoring

```python
def assess_source_credibility(url, content):
    score = {
        "domain_authority": check_domain_authority(url),
        "content_quality": analyze_content_quality(content),
        "recency": check_content_recency(content),
        "expertise_indicators": find_expertise_indicators(content),
        "citation_count": count_citations(content)
    }

    overall_score = calculate_weighted_score(score)
    return overall_score, score
```

### Contradiction Detection

```python
def detect_contradictions(research_results):
    claims = extract_claims(research_results)
    contradictions = []

    for claim1 in claims:
        for claim2 in claims:
            if claim1 != claim2 and contradicts(claim1, claim2):
                contradictions.append({
                    "claim1": claim1,
                    "claim2": claim2,
                    "sources": [claim1["source"], claim2["source"]],
                    "resolution": resolve_contradiction(claim1, claim2)
                })

    return contradictions
```

## Plan Execution with Research

### Step-Specific Research

```python
def execute_step_with_research(step):
    if step.get("research_needed"):
        # Conduct step-specific research
        for query in step.get("research_queries", []):
            browser_search(query=query)
            tabs = browser_tabs(action="list")

            # Analyze top results
            for tab in tabs[:3]:
                browser_navigate(url=tab["url"])
                browser_lock()
                snapshot = browser_snapshot()
                research_data = extract_step_specific_info(snapshot)
                browser_unlock()

        # Execute step with research context
        return execute_step(step, research_context=research_data)
    else:
        return execute_step(step)
```

### Research Validation During Execution

```python
def validate_step_with_research(step, result):
    # Search for validation information
    validation_query = f"validate {step['name']} implementation"
    browser_search(query=validation_query)

    tabs = browser_tabs(action="list")
    validation_results = []

    for tab in tabs[:3]:
        browser_navigate(url=tab["url"])
        browser_lock()
        snapshot = browser_snapshot()
        validation = extract_validation_criteria(snapshot)
        validation_results.append(validation)
        browser_unlock()

    # Validate result against research
    return validate_against_research(result, validation_results)
```

## Best Practices

### Research Strategy
1. **Start broad, then narrow**: Begin with general queries, then focus
2. **Multiple sources**: Always validate with 3+ independent sources
3. **Source diversity**: Use different types of sources (docs, blogs, forums)
4. **Check recency**: Prefer recent information for fast-moving domains
5. **Follow citations**: Trace back to original sources when possible

### Browser Tool Usage
1. **Lock tabs**: Always lock tabs before interaction
2. **Clean up**: Close unused tabs to manage resources
3. **Snapshot timing**: Take snapshots after page fully loads
4. **Navigation**: Use browser_navigate_back for efficient browsing
5. **Error handling**: Handle navigation failures gracefully

### Plan Generation
1. **Research first**: Complete research before planning
2. **Synthesize findings**: Combine insights from multiple sources
3. **Document sources**: Include source URLs in plan
4. **Update dynamically**: Revise plan based on new research
5. **Validate assumptions**: Verify plan assumptions with research

## Example Workflow

### Complete Research-to-Plan Flow

```python
# 1. Initial research
task = "Implement JWT authentication in FastAPI"

browser_search(query="JWT authentication FastAPI best practices 2026")
tabs = browser_tabs(action="list")

# 2. Analyze top sources
research_data = []
for tab in tabs[:5]:
    browser_navigate(url=tab["url"])
    browser_lock()
    snapshot = browser_snapshot()
    data = extract_research_data(snapshot)
    research_data.append(data)
    browser_unlock()

# 3. Validate with alternative sources
browser_search(query="JWT FastAPI security considerations")
# ... additional validation

# 4. Synthesize research
research_summary = synthesize_research(research_data)

# 5. Create plan
plan = create_research_plan(task, research_summary)

# 6. Initialize tracking
todo_write(merge=False, todos=plan["steps"])

# 7. Execute with research integration
execute_plan_with_research(plan)
```

## Integration with Cursor Features

### Todo Management
- Use `todo_write` to track plan steps
- Include research status in step descriptions
- Mark research steps as completed when done

### File Management
- Save research findings to files
- Document source URLs in plan files
- Create research summary documents

### Terminal Integration
- Execute commands based on research findings
- Validate implementations with research-backed checks
- Run tests informed by research

## Research Documentation

### Research Log Format

```markdown
# Research Log: [Task Name]

## Research Query
[Initial search query]

## Sources Analyzed
1. [Source 1 URL]
   - Credibility: High
   - Key Findings: [Summary]

2. [Source 2 URL]
   - Credibility: Medium
   - Key Findings: [Summary]

## Synthesis
[Combined insights from all sources]

## Plan Implications
[How research informs the plan]
```

## Error Handling

### Browser Navigation Errors

```python
def safe_browser_navigate(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            browser_navigate(url=url)
            browser_wait_for(timeout=5)  # Wait for page load
            return True
        except NavigationError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            logger.warning(f"Failed to navigate to {url}: {e}")
            return False
```

### Research Failure Handling

```python
def research_with_fallback(query, primary_sources, fallback_sources):
    try:
        # Try primary sources
        results = research_from_sources(query, primary_sources)
        if results and len(results) >= 3:
            return results
    except Exception as e:
        logger.warning(f"Primary research failed: {e}")

    # Fallback to alternative sources
    return research_from_sources(query, fallback_sources)
```

## Performance Optimization

### Caching Research Results

```python
research_cache = {}

def cached_research(query):
    cache_key = hash_query(query)
    if cache_key in research_cache:
        cached_result = research_cache[cache_key]
        if not is_stale(cached_result):
            return cached_result

    # Perform fresh research
    result = perform_research(query)
    research_cache[cache_key] = {
        "result": result,
        "timestamp": datetime.now()
    }
    return result
```

### Parallel Research

```python
async def parallel_research_queries(queries):
    tasks = []
    for query in queries:
        task = asyncio.create_task(research_query(query))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return synthesize_parallel_results(results)
```

---

*This skill integrates Cursor's MCP browser tools with deep research methodology and intelligent plan generation for research-backed task execution.*
