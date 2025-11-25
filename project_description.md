# HypothesisTree Pro  

**Don’t get blindsided. Spot decision gaps before you scale or invest. Build in 5 minutes what consultants build in 5 weeks.**  

In one run, HypothesisTree Pro turns vague "should we?" debates into a clear set of bets, tradeoffs, and experiments your team can act on **today**.  

# Problem Statement  

Strategic decisions about where to scale, what to launch, or where to fix performance usually take days of meetings, weeks of slide-building, and a handful of scarce strategy experts. Leaders wrestle with questions like *“Should we launch this product?”, “Which risks matter most?”, “Where is performance really breaking down?”* — but turning those questions into a crisp, testable decision framework is slow, expensive, and inconsistent.  

Most teams instead rely on:  

- **Fragmented analysis**  
  Siloed spreadsheets, scattered docs, and one-off slide decks that don’t connect into a coherent decision tree.  

- **One-shot AI answers**  
  Generic LLM outputs that sound confident but don’t expose decision gaps, don’t iterate on validation feedback, and rarely capture real tradeoffs.  

- **Unstructured prioritization**  
  Gut-feel 2x2s that are not directly grounded in hypotheses, evidence, or testable metrics—making it hard to defend decisions to executives or boards.  

This leads to slow decisions, missed risks, over-investment in the wrong paths, and a huge dependency on a small number of seasoned strategists. There’s no systematized way to turn complex strategic questions into reusable, high-quality decision frameworks.  

---

# Solution Statement  

**HypothesisTree Pro** is an AI-powered strategic consultant that operationalizes top-tier consulting practice. It doesn’t just “answer your question” — it **builds the kind of decision framework a strategy firm would create, then shows you exactly what to test first.**  

Given a strategic question (e.g., “Should we launch a fall detection product for eldercare facilities?”), the agent system will:  

- **Research the landscape automatically**  
  Parallel agents perform market and competitor research using live search, surfacing trends, vendors, benchmarks, and case studies.  

- **Construct MECE hypothesis trees**  
  Using domain-tailored frameworks (scale decisions, product launch, market entry, investment, operations, risk, hypothesis issue trees), the system generates a 3-level hypothesis tree that is:  
  - Mutually Exclusive and Collectively Exhaustive at each level  
  - Grounded in research, not generic templates  
  - Explicitly structured for metrics, data sources, and validation.  

- **Validate and refine via loops**  
  A MECE validator inspects the tree for overlaps, gaps, and level inconsistencies, driving iterative refinement until the tree passes quality checks.  

- **Turn hypotheses into a 2x2 prioritization matrix**  
  The validated hypotheses are converted into an impact vs. effort matrix, with a clear testing roadmap and recommended critical path.  

The result is an **end-to-end strategic reasoning pipeline**: from raw question → research → MECE hypothesis tree → validation → prioritized action plan.  

---

# Architecture  

Core to HypothesisTree Pro is the **`strategic_analyzer`** — a SequentialAgent built with Google’s Agent Development Kit (ADK). It orchestrates a multi-agent system tailored for strategic consulting work.  

## High-Level Flow  

```text
strategic_analyzer (SequentialAgent) ← Main Orchestrator
│
├─ PHASE 1: research_phase (ParallelAgent) ← PERFORMANCE
│   ├─ market_researcher (LlmAgent + google_search)
│   └─ competitor_researcher (LlmAgent + google_search)
│
├─ PHASE 2: analysis_phase (LoopAgent) ← QUALITY
│   ├─ hypothesis_generator (LlmAgent + generate_hypothesis_tree)
│   └─ mece_validator_agent (LlmAgent + validate_mece_structure + exit_loop)
│   └─ [loops until MECE compliant or max_iterations]
│
└─ PHASE 3: prioritizer (LlmAgent) ← OUTPUT
    └─ prioritizer (LlmAgent + generate_2x2_matrix)
```

## Phase 1: Research (ParallelAgent)  

- **market_researcher**  
  - LlmAgent (Gemini) using `MARKET_RESEARCHER_PROMPT`  
  - Equipped with `google_search` to pull current data on market size, growth, trends, and benchmarks.  
  - Outputs structured `market_research` context.  

- **competitor_researcher**  
  - LlmAgent (Gemini) using `COMPETITOR_RESEARCHER_PROMPT`  
  - Uses `google_search` to analyze vendors, capabilities, pricing models, reviews, and case studies.  
  - Outputs `competitor_research` context.  

Both run **in parallel** under `research_phase`, maximizing performance and ensuring independent research streams for market and competition.  

## Phase 2: Analysis (LoopAgent with MECE validation)  

- **hypothesis_generator**  
  - LlmAgent (Gemini) with `HYPOTHESIS_GENERATOR_PROMPT`.  
  - Selects the appropriate framework based on trigger phrases in the problem statement (e.g., scale decision, product launch, market entry, investment decision, operations improvement, hypothesis issue tree, risk assessment).  
  - Calls `generate_hypothesis_tree` (FunctionTool) which:  
    - Loads a strategic framework template via `FrameworkLoader` / `load_framework`.  
    - Builds a 3-level tree (L1, L2, L3) with:  
      - Static L1 categories from the framework for consistency.  
      - LLM-generated L2 branches and L3 leaves, optionally batched for efficiency.  
      - Benchmark-rich metadata, data sources, and MECE validation metadata.  

- **mece_validator_agent**  
  - LlmAgent (Gemini) using `MECE_VALIDATOR_PROMPT`.  
  - Equipped with:  
    - `validate_mece_structure` (FunctionTool) — checks tree for overlaps, gaps, and level inconsistencies, distinguishing hard failures from soft warnings.  
    - `exit_loop` (FunctionTool) — signals that MECE validation passed, instructing the LoopAgent to proceed.  

- **LoopAgent behavior** (`analysis_phase`)  
  - Iteratively calls `hypothesis_generator` → `mece_validator_agent`.  
  - Uses validation feedback to refine the tree until:  
    - MECE criteria are satisfied, or  
    - `max_iterations` is reached.  

This loop enforces **quality-by-design**, not just quality-by-prompt.  

## Phase 3: Prioritization (LlmAgent + tools)  

- **prioritizer**  
  - LlmAgent (Gemini) using `PRIORITIZER_PROMPT`.  
  - Consumes the validated hypothesis tree.  
  - Calls `generate_2x2_matrix` (FunctionTool) to:  
    - Score hypotheses by impact and effort.  
    - Produce a 2x2 matrix (e.g., quick wins, big bets, maintenance, de-prioritize).  
    - Recommend a testing sequence / critical path aligned with constraints.  

This phase turns structured thinking into **operational decision guidance**.  

## Custom Tools and Framework Engine  

- **FrameworkLoader / framework_loader.py**  
  - Robust JSON-driven framework catalog (`framework_templates.json`).  
  - Validates template structure, supports trigger-based framework selection, and surfaces available frameworks with descriptions.  

- **LLM-powered tree generators (`llm_tree_generators.py`)**  
  - Batched generation of L2 and L3 elements with integrated validation.  
  - Detailed prompts that enforce:  
    - MECE-adaptive leaf counts (3–7 per branch).  
    - Clean labels and questions with strict rules on vendors, numbers, and targets.  
    - Benchmark-aware targets and explicit data sources.  

- **MECE validator (`mece_validator.py`)**  
  - Deep structural checks for overlaps, gaps (as soft warnings), and level inconsistencies.  
  - Outputs actionable suggestions, not just a pass/fail flag.  

Together, these tools make HypothesisTree Pro feel like working with a **real strategy team**: structured, rigorous, and iterative.  

---

# Conclusion  

HypothesisTree Pro transforms strategic analysis from a one-off, slide-building exercise into a **repeatable, inspectable decision engine**.  

- The **SequentialAgent** orchestrator acts like a lead engagement manager, sequencing research, analysis, and prioritization.  
- **Parallel research** gives you breadth and freshness of insight without extra time cost.  
- The **LoopAgent** with MECE validation enforces rigor and structure that most one-shot LLM tools simply cannot match.  
- The **prioritizer** converts beautifully structured trees into clear, defensible action plans.  

This multi-agent architecture, powered by Google’s Agent Development Kit, demonstrates how real-world strategic workflows can be decomposed into specialized agents and tools—yielding a system that is modular, extensible, and ready for production-grade evaluation and observability.  

---

# Value Statement  

HypothesisTree Pro aims to compress **days of MBB-style strategic structuring** into **minutes**, while preserving quality and transparency. In a typical use case, it can:  

- **Save 6–10 hours per strategic question**  
  by automating research synthesis, tree building, and prioritization—freeing human strategists to focus on judgment, stakeholder management, and storytelling.  

- **Level-up teams without adding headcount**  
  Product managers, founders, and ops leaders gain access to decision frameworks that previously required dedicated strategy support or expensive consultants.  

- **Increase decision confidence and alignment**  
  By making hypotheses, assumptions, metrics, and tradeoffs explicit in a tree and 2x2, cross-functional teams can challenge, refine, and align on decisions faster.  

If extended further, the next frontier would be:  

- **Continuous strategic sensing**  
  Adding agents that scan industry news, regulatory changes, and competitor moves to proactively suggest new hypothesis trees or update existing ones.  

- **Scenario-aware evaluation**  
  Integrating evaluation agents that compare alternative hypotheses and trees across scenarios (e.g., optimistic, base, downside) and propose portfolio-level tradeoffs.  

These enhancements would turn HypothesisTree Pro from a powerful strategic consultant into an **always-on strategic operating system** for your business.
