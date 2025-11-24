# Tree Quality Feedback Log

This file captures user feedback on tree generation quality to improve prompts over time.

## Feedback Entry Format

```
Date: YYYY-MM-DD
Issue: Description of the problem
Example Bad Output: What was generated incorrectly
Example Good Output: What should have been generated
Fix Applied: Changes made to prompts or code
Status: Fixed / In Progress / Planned
```

---

## Feedback Entries

### 2025-11-23: L3 Labels Too Verbose with Vendor Names

**Issue**: L3 labels included vendor names and were overly verbose, making them hard to present

**Example Bad Output**:
```json
{
  "label": "Resident-Reported Fear of Falling Reduction via Teton.ai",
  "question": "Does the implementation of Teton.ai computer vision fall detection reduce resident-reported fear of falling by at least 20% among surveyed residents within 6 months?"
}
```

**Example Good Output** (from mece_tree_fall_detection.json):
```json
{
  "label": "Fall Incident Reduction",
  "question": "What is the measured reduction in fall incidents?",
  "target": ">25% reduction vs baseline"
}
```

**Root Cause**:
- Prompt lines 66, 96 instructed LLM to "mention specific vendors/competitors" in content
- No explicit rules against vendor names in labels
- No length limits on labels/questions

**Fix Applied**:
1. Removed instructions to mention vendors in labels/questions (lines 66, 96)
2. Added explicit **CRITICAL Label/Question Rules** section with:
   - Labels: 2-4 words max, NO vendor names, NO numbers
   - Questions: 1 sentence max, NO vendor names
   - Targets: Benchmarks and numbers go HERE
   - Data sources: Vendor names go HERE
3. Updated examples to show clean, concise format
4. Added ✓/✗ examples for clarity

**Status**: Fixed (2025-11-23)

**Prompt Changes**:
- File: `strategic_consultant_agent/tools/llm_tree_generators.py`
- Lines 61-108: L3 prompt completely restructured
- Lines 193-240: L2 prompt updated with same rules

---

### 2025-11-23: API Quota Exceeded (429 Error)

**Issue**: Free tier quota exhausted (15 req/min) during tree generation

**Error Message**:
```
429 RESOURCE_EXHAUSTED
Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests,
limit: 15, model: gemini-2.5-flash-lite
```

**Root Cause**:
- Using `gemini-2.5-flash-lite` (15 req/min limit)
- Making ~14 calls per tree: 2 research + 3 L2 + 9 L3

**Fix Applied**:
- Switched to `gemini-1.5-flash` (360 req/min limit)
- Changed default model in both functions

**Status**: Fixed (2025-11-23)

**Code Changes**:
- File: `strategic_consultant_agent/tools/llm_tree_generators.py`
- Line 24: `model_name: str = "gemini-1.5-flash"` (was gemini-2.5-flash-lite)
- Line 150: `model_name: str = "gemini-1.5-flash"` (was gemini-2.5-flash-lite)

---

## Guidelines for Future Prompt Updates

Based on feedback, follow these principles:

1. **Conciseness**: Labels should be 2-5 words, questions 1 sentence max
2. **Separation of Concerns**:
   - Labels/Questions: Generic, presentable
   - Targets: Specific benchmarks and numbers
   - Data Sources: Vendor names and studies
3. **MECE Compliance**: Always emphasize mutually exclusive, collectively exhaustive
4. **Examples**: Provide both good (✓) and bad (✗) examples
5. **Clarity**: Use explicit rules, not implicit expectations

---

## Next Steps for Quality Improvement

1. **Monitor Output Quality**: Review next 5-10 generated trees for compliance
2. **Add Validation**: Consider post-generation check for:
   - Label length (2-5 words)
   - Vendor name detection in labels
   - Question length (<20 words)
3. **Iterative Refinement**: Update this log with new patterns discovered

---

*This file serves as both documentation and training data for improving tree generation quality over time.*
