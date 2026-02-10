# Vector CV Model Benchmarking Guide

## Overview

This benchmarking suite helps you test switching from expensive `gpt-4-turbo-preview` to cheaper models (`gpt-4o`, `gpt-4o-mini`) for cost savings while maintaining quality.

**Current Setup:**
- All 4 LLM operations use `gpt-4-turbo-preview` ($10/$30 per 1M tokens)
- Estimated cost per CV generation: ~$0.05-0.08
- Cost for 100 applications/month: ~$5-8

**Potential Savings:**
- Switching to `gpt-4o`: 75% cost reduction → ~$1.25-2/month
- Switching to `gpt-4o-mini`: 95% cost reduction → ~$0.25-0.40/month

---

## The 4 LLM Operations

### Operation 1: `extract_skills_from_job()` (Line ~66)
**What it does:** Extracts technical skills from job descriptions into JSON array  
**Complexity:** Low - simple extraction task  
**Current model:** `gpt-4-turbo-preview`  
**Recommendation:** ✅ **Switch to `gpt-4o-mini`** - safe, 95% cost reduction  

### Operation 2: `analyze_skills_gap()` (Line ~90)
**What it does:** Compares candidate skills to job requirements, generates gap analysis  
**Complexity:** Medium - requires accuracy but structured output  
**Current model:** `gpt-4-turbo-preview`  
**Recommendation:** ✅ **Switch to `gpt-4o`** - safe, 75% cost reduction  

### Operation 3: `generate_cover_letter()` (Line ~150)
**What it does:** Writes personalized cover letter matching Edward's voice  
**Complexity:** High - creative writing, tone matching, requires personality  
**Current model:** `gpt-4-turbo-preview`  
**Recommendation:** ⚠️ **Test `gpt-4o` carefully** - review quality first  

### Operation 4: `generate_tailored_cv()` (Line ~200)
**What it does:** Generates complex structured CV with anti-hallucination validation  
**Complexity:** Very High - critical output, complex JSON structure  
**Current model:** `gpt-4-turbo-preview`  
**Recommendation:** ❌ **Keep current model** - too risky to change  

---

## Testing Methodology

### Phase 1: Automated Benchmarking
Run `benchmark_models.py` to measure:
- **Cost:** Exact USD cost per operation
- **Speed:** Response time in seconds
- **Token usage:** Input/output tokens
- **Projections:** Cost for 10/100 applications

**Output:** 
- `benchmark_results.json` - Raw data
- `benchmark_report.txt` - Human-readable analysis

### Phase 2: Quality Comparison
Run `quality_comparison.py` to generate:
- Side-by-side outputs from all 3 models
- Interactive HTML report with rating forms
- Space for human evaluation notes

**Output:**
- `quality_comparison_outputs.json` - Raw model outputs
- `quality_comparison.html` - Interactive comparison

### Phase 3: Human Evaluation
Open `quality_comparison.html` and evaluate:

**For Skills Extraction:**
- Are all required skills captured?
- Any false positives (skills not in job)?
- Is the list comprehensive?

**For Cover Letters:**
- Does it match Edward's voice (conversational, technical)?
- Are specific projects/skills mentioned?
- Does it feel authentic (not corporate fluff)?
- Are skill gaps acknowledged honestly?

---

## Decision Framework

### Operation 1 (extract_skills_from_job)
**Switch to gpt-4o-mini if:**
- ✅ All 3 models extract similar skills (~90% overlap)
- ✅ No critical skills are missed
- ✅ No hallucinated skills are added

**Risk Level:** 🟢 Low - This is simple JSON extraction

### Operation 2 (analyze_skills_gap)
**Switch to gpt-4o if:**
- ✅ Matching skills list is focused (job-specific only)
- ✅ Missing skills are accurate
- ✅ Recommendations are sensible

**Risk Level:** 🟢 Low - Structured output with clear requirements

### Operation 3 (generate_cover_letter)
**Switch to gpt-4o if:**
- ✅ Tone matches Edward's voice (conversational, not corporate)
- ✅ Technical details are specific and accurate
- ✅ Skill gaps are acknowledged honestly
- ✅ Letter feels authentic and enthusiastic
- ⚠️ Test with 5-10 real applications first

**Risk Level:** 🟡 Medium - Customer-facing content requires quality

### Operation 4 (generate_tailored_cv)
**Do NOT switch - Keep gpt-4-turbo-preview**
- ❌ Most complex operation
- ❌ Critical customer-facing output
- ❌ Has anti-hallucination validation that expects high quality
- ❌ Cost savings not worth the risk

**Risk Level:** 🔴 High - Core product output

---

## Implementation Guide

### Safe Implementation (Recommended)

#### Step 1: Switch Operation 1 (extract_skills_from_job)
**File:** `llm_service.py`, Line ~66

**Change:**
```python
# OLD
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    temperature=0.1,
    response_format={"type": "json_object"}
)

# NEW
response = client.chat.completions.create(
    model="gpt-4o-mini",  # ← Changed
    messages=messages,
    temperature=0.1,
    response_format={"type": "json_object"}
)
```

**Test:** Generate 3-5 applications, verify skills are extracted correctly

#### Step 2: Switch Operation 2 (analyze_skills_gap)
**File:** `llm_service.py`, Line ~120

**Change:**
```python
# OLD
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    temperature=0.2,
    response_format={"type": "json_object"}
)

# NEW
response = client.chat.completions.create(
    model="gpt-4o",  # ← Changed
    messages=messages,
    temperature=0.2,
    response_format={"type": "json_object"}
)
```

**Test:** Generate 3-5 applications, verify skills gap analysis is accurate

#### Step 3: Test Operation 3 (generate_cover_letter) - OPTIONAL
**File:** `llm_service.py`, Line ~270

**Change:**
```python
# OLD
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=messages,
    temperature=0.4
)

# NEW
response = client.chat.completions.create(
    model="gpt-4o",  # ← Changed
    messages=messages,
    temperature=0.4
)
```

**Test:** Generate 10+ applications, manually review each cover letter for:
- Tone and authenticity
- Technical accuracy
- Specific project mentions
- Honest acknowledgment of gaps

**Rollback if:** Cover letters feel generic, lack specificity, or lose Edward's voice

#### Step 4: NEVER Change Operation 4
**Do not modify `generate_tailored_cv()` at line ~200**

---

## Monitoring Plan

### Week 1: Initial Rollout
- Deploy changes to operations 1 & 2
- Generate 10 applications
- Manually review all outputs
- Check for:
  - Missing skills
  - Incorrect gap analysis
  - Quality degradation

### Week 2-4: Extended Testing
- Continue monitoring for anomalies
- Compare user engagement (if metrics available)
- Document any issues

### Rollback Criteria
Immediately rollback if:
- ❌ Skills are consistently missed
- ❌ Hallucinated skills appear
- ❌ Gap analysis is inaccurate
- ❌ Users report quality issues

---

## Expected Cost Savings

### Current Costs (gpt-4-turbo-preview for all)
- Per CV generation: ~$0.05-0.08
- 10 applications: ~$0.50-0.80
- 100 applications: ~$5-8

### After Switching Operations 1-2 (Conservative)
- Per CV generation: ~$0.02-0.04 (60% reduction)
- 10 applications: ~$0.20-0.40
- 100 applications: ~$2-4
- **Monthly savings: ~$3-4 @ 100 apps/month**

### After Switching Operations 1-3 (Aggressive)
- Per CV generation: ~$0.01-0.02 (80% reduction)
- 10 applications: ~$0.10-0.20
- 100 applications: ~$1-2
- **Monthly savings: ~$4-6 @ 100 apps/month**

---

## Troubleshooting

### Benchmark fails with API errors
- Check `.env` file has valid `OPENAI_API_KEY`
- Verify API key has sufficient credits
- Check rate limits on OpenAI dashboard

### Quality is inconsistent
- Try adjusting temperature (±0.1)
- Add more specific examples in prompts
- Consider using `gpt-4o` instead of `gpt-4o-mini`

### Outputs are too generic
- Keep current model for that operation
- Cost savings aren't worth quality loss

---

## Files Reference

| File | Purpose |
|------|---------|
| `benchmark_models.py` | Automated performance testing |
| `quality_comparison.py` | Generate side-by-side quality comparison |
| `run_benchmarks.py` | Simple runner for both tests |
| `benchmark_results.json` | Raw performance data |
| `benchmark_report.txt` | Human-readable cost analysis |
| `quality_comparison.html` | Interactive quality review |
| `quality_comparison_outputs.json` | Raw model outputs |
| `BENCHMARKING_README.md` | This file |
| `QUICK_START.md` | Fast-track guide |

---

## Support

If you encounter issues:
1. Review `benchmark_report.txt` for cost analysis
2. Check `quality_comparison.html` for quality comparison
3. Test with smaller sample (3-5 applications) first
4. Rollback immediately if quality degrades

Remember: **Quality > Cost Savings** for customer-facing outputs