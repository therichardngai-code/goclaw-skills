---
name: deep-research
description: Multi-source deep research with sub-agent delegation, source verification, and consolidated reporting. Use when user needs thorough research on any topic with verified data, statistics, and citations from trusted sources.
version: 1.0.0
author: Richard Ng
tags:
  - research
  - analysis
  - verification
  - multi-source
  - sub-agent
triggers:
  - "research"
  - "deep research"
  - "investigate"
  - "find data on"
  - "gather information"
  - "nghien cuu"
  - "tim hieu"
  - "market research"
  - "competitive analysis"
  - "industry report"
---

# Deep Research

Multi-source research pipeline with parallel sub-agent gathering, cross-verification, and consolidated reporting. Produces a structured research report with verified data, statistics, and citations.

## When to Use

- User asks to "research", "investigate", or "find data on" a topic
- Content creation requires verified stats and citations (pairs with `source-verify` skill)
- Competitive analysis, market sizing, technology evaluation
- Any task requiring data from 3+ independent sources

---

## Process Overview

```
Topic Input
  |
  v
[Step 1] Decompose into research questions (3-7 questions)
  |
  v
[Step 2] Parallel multi-source gathering (sub-agents)
  |  |  |
  v  v  v
  Report A  Report B  Report C  (each with sources + data)
  |
  v
[Step 3] Cross-verify & score sources (CRAAP + triangulation)
  |
  v
[Step 4] Distill & consolidate (single merged report)
  |
  v
[Step 5] Output: research report + (optional) HTML presentation
```

---

## Step 1 -- Decompose Topic

Break the user's topic into 3-7 focused research questions using the **Issue Tree** method (McKinsey):

| Input | Decomposed Questions |
|-------|---------------------|
| "AI Agent security" | 1. What attack vectors target AI agents? 2. What frameworks exist for AI agent security? 3. What incidents have occurred? 4. What are enterprise adoption stats? 5. What mitigation best practices exist? |
| "Go vs Rust for microservices" | 1. Performance benchmarks? 2. Ecosystem maturity? 3. Developer productivity? 4. Production adoption at scale? 5. Memory safety guarantees? |

For each question, identify:
- **Search angle**: what to search for
- **Source type needed**: academic, industry report, news, benchmark, case study
- **Recency requirement**: last 6 months, 1 year, 3 years, or evergreen

---

## Step 2 -- Multi-Source Gathering

### Source Hierarchy (by trust tier)

| Tier | Source Type | Trust Score | Examples |
|------|-----------|-------------|---------|
| T1 | Peer-reviewed / Official | 9-10 | IEEE, ACM, NIST, RFC, official docs |
| T2 | Industry research firm | 8-9 | Gartner, Forrester, McKinsey, Deloitte, IDC |
| T3 | Reputable tech publication | 7-8 | InfoQ, The Verge, Ars Technica, Dark Reading |
| T4 | Company blog / whitepaper | 6-7 | Anthropic blog, OpenAI blog, Google AI blog |
| T5 | Community / individual | 4-6 | HackerNews, Reddit, Medium, personal blogs |
| T6 | AI-generated / unverified | 1-3 | ChatGPT answers, wiki without citations |

### Gathering Strategy

**Parallel sub-agents** (spawn 2-4 depending on topic breadth):

```
Sub-agent 1: "Academic & Standards"
  Tools: web_search, web_fetch
  Focus: Papers, NIST/OWASP/ISO standards, official specifications
  Output: research report with citations

Sub-agent 2: "Industry & Market"
  Tools: web_search, web_fetch
  Focus: Gartner, Forrester, McKinsey, Deloitte reports, market sizing
  Output: research report with statistics

Sub-agent 3: "News & Case Studies"
  Tools: web_search, web_fetch, camoufox-crawler (if X/Twitter needed)
  Focus: Recent news, incidents, real-world deployments, expert opinions
  Output: research report with timeline

Sub-agent 4: "Benchmarks & Technical" (if technical topic)
  Tools: web_search, web_fetch
  Focus: Benchmark data, performance comparisons, GitHub repos
  Output: research report with data tables
```

### Sub-Agent Prompt Template

```
You are a research analyst. Your task:

TOPIC: {research_question}
FOCUS: {source_type}
RECENCY: {recency_requirement}

Instructions:
1. Search for 5-10 relevant sources using web_search
2. Read the top 3-5 most relevant results using web_fetch
3. Extract: key claims, statistics, quotes, dates, author credentials
4. For each claim, record:
   - The exact data point or quote
   - Source URL
   - Publication date
   - Author/organization
   - Source tier (T1-T6)

Output format:
## Research Report: {question}
### Key Findings
1. [Finding with source]
2. [Finding with source]
### Statistics
| Metric | Value | Source | Date | Tier |
### Notable Quotes
### Unverified Claims (needs cross-check)
### Sources Used (with URLs)
```

### Search Query Formulation

For each research question, construct 2-3 search queries:

| Strategy | Example |
|----------|---------|
| **Direct** | `AI agent security vulnerabilities 2025 2026` |
| **Authority** | `site:gartner.com AI agent security` |
| **Academic** | `"agentic AI" security framework NIST OWASP` |
| **Recency** | `AI agent attack vector after:2025-01-01` |
| **Data-seeking** | `AI agent market size billion 2026 statistics` |

---

## Step 3 -- Cross-Verification (CRAAP + Triangulation)

### CRAAP Test (California State University)

Score each source 1-10 on five criteria:

| Criteria | Question | Weight |
|----------|----------|--------|
| **C**urrency | When was it published/updated? | 15% |
| **R**elevance | Does it directly answer the research question? | 25% |
| **A**uthority | Who is the author/publisher? Credentials? | 25% |
| **A**ccuracy | Is the data supported by evidence? Referenced? | 25% |
| **P**urpose | Is it objective? Educational or promotional? | 10% |

**Composite score** = weighted average. Drop sources below 5.0.

### Triangulation Rule

A claim is **verified** when:
- 2+ independent T1-T3 sources agree, OR
- 1 T1 source confirms with no contradictions

A claim is **likely true** when:
- 2+ T3-T4 sources agree

A claim is **unverified** when:
- Only 1 source, OR
- Sources contradict each other

**When sources contradict:** Record all versions with sources. Note the disagreement. Present the strongest-sourced version as primary, others as alternatives.

### Verification Matrix

Build this for every key data point:

```
| Claim | Source 1 | Source 2 | Source 3 | Status |
|-------|----------|----------|----------|--------|
| AI agent market = $7.6B | Gartner (T2) | IDC (T2) | -- | VERIFIED |
| 80% enterprises adopt by 2026 | IDC (T2) | -- | -- | LIKELY |
| 48% cite agents as #1 vector | Dark Reading (T3) | OWASP (T1) | -- | VERIFIED |
```

---

## Step 4 -- Distill & Consolidate

Merge all sub-agent reports into a single consolidated report:

### Report Structure

```markdown
# Research Report: {Topic}
Generated: {date} | Sources: {count} | Verified claims: {count}

## Executive Summary
3-5 sentences. Key takeaway. Most important number.

## Key Findings
### Finding 1: {title}
{2-3 paragraphs with inline citations [Source, Date]}
**Key stat:** {number} — Source: {name} ({tier})

### Finding 2: {title}
...

## Data Dashboard
| Metric | Value | Source | Verified |
|--------|-------|--------|----------|
...

## Comparison (if applicable)
| Criteria | Option A | Option B |
...

## Timeline (if applicable)
- {date}: {event} [source]
...

## Risk / Gaps
- What data is missing?
- What couldn't be verified?
- What requires primary research?

## Sources
### Tier 1 (Highest Trust)
1. {Title} — {URL} — {Date} — CRAAP: {score}
### Tier 2
...

## Methodology
Research conducted using {N} parallel research agents.
{M} sources evaluated, {K} passed CRAAP threshold.
Triangulation applied to {X} key claims.
```

### Save Location

- Report: `./reports/research-{date}-{slug}.md`
- Raw sub-agent reports: `./reports/research-{date}-{slug}/`

---

## Step 5 -- Output Options

After consolidation, ask user:

1. **Markdown report only** (default) -- saved to ./reports/
2. **Interactive HTML presentation** -- activate `research-presenter` skill
3. **Both** -- report + presentation

---

## Integration with Other Skills

| Skill | When to Chain |
|-------|--------------|
| `source-verify` | Lightweight verification for content writing (subset of this skill) |
| `research-presenter` | Generate interactive HTML from the consolidated report |
| `interactive-explainer` | If research reveals a system/architecture worth diagramming |
| `camoufox-crawler` | When research requires scraping X/Twitter for expert opinions |

---

## Quality Gates

Before delivering the final report:

- [ ] Every key statistic has a source with URL
- [ ] Every source has a CRAAP score >= 5.0
- [ ] Key claims are triangulated (2+ sources)
- [ ] Unverified claims are explicitly marked
- [ ] Executive summary is under 5 sentences
- [ ] All dates are absolute (no "recently" or "last year")
- [ ] Source tier is labeled for every citation

---

## Agentic Protocol

### Activation Log
```
[SKILL ACTIVATED] deep-research v1.0.0
  Topic: {topic}
  Questions: {N} research questions decomposed
  Agents: {M} sub-agents spawned
  Target sources: T1-T{max_tier}
```

### Progress Updates
After each sub-agent completes, report:
```
[deep-research] Agent {N}/{total} complete: {question} — {sources_found} sources, {claims} claims
```

### Completion Log
```
[deep-research] Research complete
  Sources evaluated: {total}
  Sources passed CRAAP: {passed}
  Verified claims: {verified}/{total_claims}
  Report: {path}
```
