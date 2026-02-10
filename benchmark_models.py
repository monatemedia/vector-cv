"""
Automated Performance Benchmark for Vector CV LLM Models
Tests gpt-4-turbo-preview vs gpt-4o vs gpt-4o-mini on real workloads
"""

import os
import json
import time
from datetime import datetime
from openai import OpenAI
from typing import Dict, List, Tuple
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model pricing per 1M tokens (input/output)
MODEL_PRICING = {
    "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60}
}

# Test data - realistic job description
TEST_JOB_DESCRIPTION = """
Senior Full Stack Developer - SaaS Platform
Company: TechCorp Industries

Requirements:
- 5+ years PHP development (Laravel 9+ required)
- Strong PostgreSQL experience with complex queries
- React or Vue.js for frontend development
- Docker & CI/CD pipeline management
- RESTful API design and implementation
- Experience with Redis caching
- AWS deployment experience (EC2, S3, RDS)
- Git version control

Bonus:
- Tailwind CSS
- TypeScript
- GraphQL
- Microservices architecture

The role involves building and maintaining our core SaaS platform serving 10,000+ users.
"""

# Candidate skills (simulating database data)
CANDIDATE_SKILLS = [
    "PHP", "Laravel", "PostgreSQL", "MySQL", "React", "Vue.js", "JavaScript",
    "Docker", "Docker Compose", "CI/CD", "GitHub Actions", "RESTful API",
    "Redis", "Nginx", "Linux", "Ubuntu", "Git", "Tailwind CSS", "Bootstrap",
    "HTML5", "CSS3", "jQuery", "JSON", "OAuth 2.0", "JWT", "Eloquent ORM",
    "Python", "FastAPI", "Flask", "NumPy", "Pandas", "AWS", "AWS EC2",
    "AWS S3", "Memcached", "SEO", "Responsive Design", "Mobile-First",
    "Agile", "Scrum", "OpenAPI", "Swagger", "Markdown"
]


def benchmark_extract_skills(model: str) -> Tuple[Dict, float, int, int]:
    """Test extract_skills_from_job operation"""
    prompt = f"""Extract ONLY the technical skills, technologies, tools, and frameworks from this job description.

Be specific and include:
- Programming languages (PHP, Python, JavaScript, etc.)
- Frameworks (Laravel, React, Vue, Django, etc.)
- Databases (MySQL, PostgreSQL, Redis, etc.)
- Tools (Docker, Git, Nginx, etc.)
- Cloud platforms (AWS, Azure, etc.)
- Methodologies (CI/CD, DevOps, etc.)

Return ONLY a JSON object with a "skills" array of strings.

Job Description:
{TEST_JOB_DESCRIPTION}

Example output format:
{{"skills": ["React", "Docker", "PostgreSQL", "AWS", "Laravel"]}}
"""

    start_time = time.time()
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    duration = time.time() - start_time
    
    result = json.loads(response.choices[0].message.content)
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    
    return result, duration, input_tokens, output_tokens


def benchmark_analyze_skills_gap(model: str) -> Tuple[Dict, float, int, int]:
    """Test analyze_skills_gap operation"""
    
    skills_context = f"\n\n⚠️ CRITICAL - CANDIDATE'S COMPLETE SKILL SET ⚠️\nThe candidate HAS these skills: {', '.join(CANDIDATE_SKILLS)}\n\nDo NOT mark any of the above skills as 'missing_skills'. They must go in 'matching_skills'.\n"
    
    prompt = f"""You are a Technical Lead analyzing a candidate for a role.

CANDIDATE EXPERIENCE:
The candidate has {len(CANDIDATE_SKILLS)} technical skills including Laravel, PostgreSQL, React, Docker, CI/CD, AWS, and more.
{skills_context}

JOB DESCRIPTION:
{TEST_JOB_DESCRIPTION}

CRITICAL RULES FOR matching_skills:
1. ONLY include skills that are EXPLICITLY mentioned in the job description
2. Check if the candidate has each job-required skill
3. DO NOT include candidate skills that aren't mentioned in the job description

Analyze the skills gap. Be specific about versions and ecosystems.
Return ONLY valid JSON:
{{
    "missing_skills": [],
    "matching_skills": [],
    "partial_matches": [],
    "recommendations": []
}}"""

    start_time = time.time()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a technical recruiter who values data over fluff."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    duration = time.time() - start_time
    
    result = json.loads(response.choices[0].message.content)
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    
    return result, duration, input_tokens, output_tokens


def benchmark_cover_letter(model: str) -> Tuple[str, float, int, int]:
    """Test generate_cover_letter operation"""
    
    prompt = f"""You are Edward Baitsewe's cover letter writer.

CANDIDATE: Edward Baitsewe
LOCATION: Cape Town, South Africa
JOB: Senior Full Stack Developer at TechCorp Industries

CANDIDATE'S SKILLS: {', '.join(CANDIDATE_SKILLS[:20])}

JOB DESCRIPTION:
{TEST_JOB_DESCRIPTION}

Write a professional cover letter (under 400 words) that:
1. Shows domain expertise and understanding of their SaaS platform
2. Matches Edward's Laravel/PostgreSQL/React experience to their needs
3. Addresses bonus skills honestly
4. Mentions 10-year financial services background as differentiator
5. Shows enthusiasm for the role

Use active voice, be specific about technical skills, and keep it conversational."""

    start_time = time.time()
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional cover letter writer. Be concise and specific."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    
    duration = time.time() - start_time
    
    result = response.choices[0].message.content
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    
    return result, duration, input_tokens, output_tokens


def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Calculate cost in USD for the operation"""
    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def run_benchmark() -> Dict:
    """Run complete benchmark suite"""
    
    print("🚀 Starting Vector CV Model Benchmark")
    print("=" * 80)
    
    models = ["gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"]
    results = {
        "timestamp": datetime.now().isoformat(),
        "models": {}
    }
    
    for model in models:
        print(f"\n📊 Testing {model}...")
        model_results = {
            "operations": {}
        }
        
        # Test 1: Extract Skills
        print(f"  → extract_skills_from_job...")
        try:
            output, duration, input_tokens, output_tokens = benchmark_extract_skills(model)
            cost = calculate_cost(input_tokens, output_tokens, model)
            model_results["operations"]["extract_skills"] = {
                "duration_seconds": round(duration, 2),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": round(cost, 6),
                "success": True,
                "output_preview": output.get("skills", [])[:5] if isinstance(output, dict) else str(output)[:100]
            }
            print(f"    ✅ {duration:.2f}s | ${cost:.6f} | {len(output.get('skills', []))} skills")
        except Exception as e:
            model_results["operations"]["extract_skills"] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ Failed: {e}")
        
        # Test 2: Analyze Skills Gap
        print(f"  → analyze_skills_gap...")
        try:
            output, duration, input_tokens, output_tokens = benchmark_analyze_skills_gap(model)
            cost = calculate_cost(input_tokens, output_tokens, model)
            model_results["operations"]["analyze_skills_gap"] = {
                "duration_seconds": round(duration, 2),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": round(cost, 6),
                "success": True,
                "matching_skills_count": len(output.get("matching_skills", [])),
                "missing_skills_count": len(output.get("missing_skills", []))
            }
            print(f"    ✅ {duration:.2f}s | ${cost:.6f} | {len(output.get('matching_skills', []))} matching")
        except Exception as e:
            model_results["operations"]["analyze_skills_gap"] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ Failed: {e}")
        
        # Test 3: Generate Cover Letter
        print(f"  → generate_cover_letter...")
        try:
            output, duration, input_tokens, output_tokens = benchmark_cover_letter(model)
            cost = calculate_cost(input_tokens, output_tokens, model)
            model_results["operations"]["generate_cover_letter"] = {
                "duration_seconds": round(duration, 2),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": round(cost, 6),
                "success": True,
                "length_words": len(output.split()),
                "output_preview": output[:200] + "..."
            }
            print(f"    ✅ {duration:.2f}s | ${cost:.6f} | {len(output.split())} words")
        except Exception as e:
            model_results["operations"]["generate_cover_letter"] = {
                "success": False,
                "error": str(e)
            }
            print(f"    ❌ Failed: {e}")
        
        # Calculate totals
        total_cost = sum(
            op.get("cost_usd", 0) 
            for op in model_results["operations"].values()
        )
        total_duration = sum(
            op.get("duration_seconds", 0)
            for op in model_results["operations"].values()
        )
        
        model_results["total_cost_usd"] = round(total_cost, 6)
        model_results["total_duration_seconds"] = round(total_duration, 2)
        model_results["cost_per_10_applications"] = round(total_cost * 10, 4)
        
        results["models"][model] = model_results
        
        print(f"\n  💰 Total: ${total_cost:.6f} | ⏱️  {total_duration:.2f}s")
        print(f"  📊 Cost for 10 applications: ${total_cost * 10:.4f}")
    
    return results


def generate_text_report(results: Dict) -> str:
    """Generate human-readable text report"""
    
    report = []
    report.append("=" * 80)
    report.append("VECTOR CV MODEL BENCHMARK REPORT")
    report.append("=" * 80)
    report.append(f"Timestamp: {results['timestamp']}")
    report.append("")
    
    # Comparison table
    report.append("COST COMPARISON (per single CV generation):")
    report.append("-" * 80)
    report.append(f"{'Model':<25} {'Total Cost':<15} {'10 Apps':<15} {'Duration':<10}")
    report.append("-" * 80)
    
    for model, data in results["models"].items():
        report.append(
            f"{model:<25} "
            f"${data['total_cost_usd']:<14.6f} "
            f"${data['cost_per_10_applications']:<14.4f} "
            f"{data['total_duration_seconds']:<9.2f}s"
        )
    
    report.append("")
    report.append("SAVINGS ANALYSIS:")
    report.append("-" * 80)
    
    base_cost = results["models"]["gpt-4-turbo-preview"]["cost_per_10_applications"]
    for model in ["gpt-4o", "gpt-4o-mini"]:
        model_cost = results["models"][model]["cost_per_10_applications"]
        savings = base_cost - model_cost
        savings_pct = (savings / base_cost) * 100
        report.append(f"{model}: Save ${savings:.4f} ({savings_pct:.1f}%) per 10 applications")
    
    report.append("")
    report.append("OPERATION BREAKDOWN:")
    report.append("-" * 80)
    
    for model, data in results["models"].items():
        report.append(f"\n{model}:")
        for op_name, op_data in data["operations"].items():
            if op_data.get("success"):
                report.append(
                    f"  {op_name}: ${op_data['cost_usd']:.6f} | "
                    f"{op_data['duration_seconds']:.2f}s | "
                    f"{op_data['input_tokens']}→{op_data['output_tokens']} tokens"
                )
    
    report.append("")
    report.append("RECOMMENDATIONS:")
    report.append("-" * 80)
    report.append("1. ✅ SAFE: Switch extract_skills_from_job to gpt-4o-mini (simple extraction)")
    report.append("2. ✅ SAFE: Switch analyze_skills_gap to gpt-4o (needs accuracy)")
    report.append("3. ⚠️  TEST: Try gpt-4o for generate_cover_letter (review quality)")
    report.append("4. ❌ KEEP: Leave generate_tailored_cv on gpt-4-turbo-preview (complex)")
    report.append("")
    
    return "\n".join(report)


def main():
    # Run benchmark
    results = run_benchmark()
    
    # Save JSON results
    json_path = "benchmark_results.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ JSON results saved to {json_path}")
    
    # Generate and save text report
    text_report = generate_text_report(results)
    txt_path = "benchmark_report.txt"
    with open(txt_path, "w") as f:
        f.write(text_report)
    print(f"✅ Text report saved to {txt_path}")
    
    # Print summary
    print("\n" + text_report)
    
    print("\n" + "=" * 80)
    print("✅ Benchmark complete! Next steps:")
    print("   1. Review benchmark_report.txt for cost analysis")
    print("   2. Run quality_comparison.py to test output quality")
    print("   3. See BENCHMARKING_README.md for implementation guide")
    print("=" * 80)


if __name__ == "__main__":
    main()