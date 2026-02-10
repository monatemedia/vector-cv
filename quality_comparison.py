"""
Quality Comparison Tool for Vector CV Models
Generates side-by-side outputs for human evaluation
"""

import os
import json
from datetime import datetime
from openai import OpenAI
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Same test data as benchmark
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

CANDIDATE_SKILLS = [
    "PHP", "Laravel", "PostgreSQL", "MySQL", "React", "Vue.js", "JavaScript",
    "Docker", "Docker Compose", "CI/CD", "GitHub Actions", "RESTful API",
    "Redis", "Nginx", "Linux", "Ubuntu", "Git", "Tailwind CSS", "Bootstrap",
    "HTML5", "CSS3", "jQuery", "JSON", "OAuth 2.0", "JWT", "Eloquent ORM",
    "Python", "FastAPI", "Flask", "NumPy", "Pandas", "AWS", "AWS EC2",
    "AWS S3", "Memcached", "SEO", "Responsive Design", "Mobile-First",
    "Agile", "Scrum", "OpenAPI", "Swagger", "Markdown"
]


def generate_cover_letter(model: str) -> str:
    """Generate cover letter with specified model"""
    
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

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a professional cover letter writer. Be concise and specific."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    
    return response.choices[0].message.content


def extract_skills(model: str) -> List[str]:
    """Extract skills with specified model"""
    
    prompt = f"""Extract ONLY the technical skills, technologies, tools, and frameworks from this job description.

Return ONLY a JSON object with a "skills" array of strings.

Job Description:
{TEST_JOB_DESCRIPTION}

Example output format:
{{"skills": ["React", "Docker", "PostgreSQL", "AWS", "Laravel"]}}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    return result.get("skills", [])


def generate_html_report(outputs: Dict) -> str:
    """Generate interactive HTML comparison report"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vector CV Model Quality Comparison</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 50px;
        }}
        .section-title {{
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 20px;
            padding: 10px;
            background: #ecf0f1;
            border-left: 4px solid #3498db;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .model-output {{
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            background: #fafafa;
        }}
        .model-name {{
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}
        .model-name.current {{ color: #e74c3c; }}
        .model-name.recommended {{ color: #27ae60; }}
        .model-name.test {{ color: #f39c12; }}
        .output-content {{
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.8;
            background: white;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }}
        .skills-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        .skill-tag {{
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .rating-form {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 4px;
            padding: 15px;
            margin-top: 15px;
        }}
        .rating-form h4 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        .rating-options {{
            display: flex;
            gap: 15px;
            margin: 10px 0;
        }}
        .rating-options label {{
            display: flex;
            align-items: center;
            gap: 5px;
            cursor: pointer;
        }}
        textarea {{
            width: 100%;
            min-height: 80px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
            font-size: 14px;
            margin-top: 10px;
        }}
        .job-description {{
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}
        .recommendation {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
        }}
        .recommendation h3 {{
            margin-bottom: 10px;
        }}
        .recommendation ul {{
            margin-left: 20px;
        }}
        .recommendation li {{
            margin: 5px 0;
        }}
        .legend {{
            display: flex;
            gap: 30px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .legend-dot.current {{ background: #e74c3c; }}
        .legend-dot.recommended {{ background: #27ae60; }}
        .legend-dot.test {{ background: #f39c12; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Vector CV Model Quality Comparison</h1>
        <div class="timestamp">Generated: {outputs['timestamp']}</div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-dot current"></div>
                <span>Current Model (gpt-4-turbo-preview)</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot recommended"></div>
                <span>Recommended Switch (gpt-4o or gpt-4o-mini)</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot test"></div>
                <span>Needs Testing (gpt-4o)</span>
            </div>
        </div>
        
        <div class="job-description">
            <h3>📄 Test Job Description</h3>
            <pre style="white-space: pre-wrap; margin-top: 10px;">{TEST_JOB_DESCRIPTION}</pre>
        </div>
        
        <!-- Skills Extraction Comparison -->
        <div class="section">
            <div class="section-title">🔍 Operation 1: extract_skills_from_job</div>
            <div class="recommendation">
                <h3>Recommendation: Switch to gpt-4o-mini ✅</h3>
                <p>This is simple JSON extraction with clear requirements. The cheapest model should handle it perfectly.</p>
            </div>
            
            <div class="comparison-grid">
"""
    
    # Skills extraction comparison
    for model in ["gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"]:
        skills = outputs["skills_extraction"][model]
        css_class = "current" if model == "gpt-4-turbo-preview" else "recommended"
        
        html += f"""
                <div class="model-output">
                    <div class="model-name {css_class}">{model}</div>
                    <div class="skills-list">
"""
        for skill in skills:
            html += f'                        <span class="skill-tag">{skill}</span>\n'
        
        html += f"""                    </div>
                    <div style="margin-top: 15px; color: #666; font-size: 13px;">
                        Count: {len(skills)} skills
                    </div>
                    <div class="rating-form">
                        <h4>Rate this output:</h4>
                        <div class="rating-options">
                            <label><input type="radio" name="skills_{model}" value="excellent"> Excellent</label>
                            <label><input type="radio" name="skills_{model}" value="good"> Good</label>
                            <label><input type="radio" name="skills_{model}" value="poor"> Poor</label>
                        </div>
                        <textarea placeholder="Notes: Missing skills? Incorrect extractions? Too verbose?"></textarea>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <!-- Cover Letter Comparison -->
        <div class="section">
            <div class="section-title">✉️ Operation 3: generate_cover_letter</div>
            <div class="recommendation">
                <h3>Recommendation: Test gpt-4o carefully ⚠️</h3>
                <p>This requires creativity and tone matching. Compare quality carefully before switching. Look for:</p>
                <ul>
                    <li>Natural, conversational tone (not corporate fluff)</li>
                    <li>Specific technical details from candidate's experience</li>
                    <li>Honest acknowledgment of skill gaps</li>
                    <li>Enthusiasm without being fake</li>
                </ul>
            </div>
            
            <div class="comparison-grid">
"""
    
    # Cover letter comparison
    for model in ["gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"]:
        letter = outputs["cover_letters"][model]
        css_class = "current" if model == "gpt-4-turbo-preview" else ("test" if model == "gpt-4o" else "recommended")
        
        html += f"""
                <div class="model-output">
                    <div class="model-name {css_class}">{model}</div>
                    <div class="output-content">{letter}</div>
                    <div style="color: #666; font-size: 13px; margin-bottom: 10px;">
                        Length: {len(letter.split())} words
                    </div>
                    <div class="rating-form">
                        <h4>Rate this cover letter:</h4>
                        <div class="rating-options">
                            <label><input type="radio" name="letter_{model}" value="excellent"> Excellent</label>
                            <label><input type="radio" name="letter_{model}" value="good"> Good</label>
                            <label><input type="radio" name="letter_{model}" value="poor"> Poor</label>
                        </div>
                        <textarea placeholder="Notes: Tone? Specificity? Authenticity? Technical accuracy?"></textarea>
                    </div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="recommendation">
            <h3>📊 Decision Framework</h3>
            <ul>
                <li><strong>Extract Skills:</strong> If all 3 models extract similar skills → switch to gpt-4o-mini</li>
                <li><strong>Cover Letter:</strong> If gpt-4o matches quality of gpt-4-turbo-preview → switch to save costs</li>
                <li><strong>If in doubt:</strong> Keep current model (quality > cost for customer-facing content)</li>
            </ul>
        </div>
        
        <div style="margin-top: 50px; padding: 20px; background: #e3f2fd; border-radius: 4px;">
            <h3 style="color: #1976d2; margin-bottom: 10px;">📝 Next Steps</h3>
            <ol style="margin-left: 20px; line-height: 2;">
                <li>Review outputs above and rate each model's quality</li>
                <li>Check benchmark_report.txt for cost analysis</li>
                <li>If quality is acceptable, update llm_service.py (see BENCHMARKING_README.md)</li>
                <li>Deploy and monitor first 10 applications for quality issues</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    print("🔬 Starting Quality Comparison Test")
    print("=" * 80)
    
    models = ["gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"]
    outputs = {
        "timestamp": datetime.now().isoformat(),
        "skills_extraction": {},
        "cover_letters": {}
    }
    
    # Generate outputs for each model
    for model in models:
        print(f"\n📊 Testing {model}...")
        
        # Extract skills
        print(f"  → Extracting skills...")
        try:
            skills = extract_skills(model)
            outputs["skills_extraction"][model] = skills
            print(f"    ✅ Extracted {len(skills)} skills")
        except Exception as e:
            outputs["skills_extraction"][model] = []
            print(f"    ❌ Failed: {e}")
        
        # Generate cover letter
        print(f"  → Generating cover letter...")
        try:
            letter = generate_cover_letter(model)
            outputs["cover_letters"][model] = letter
            print(f"    ✅ Generated {len(letter.split())} word letter")
        except Exception as e:
            outputs["cover_letters"][model] = f"Error: {e}"
            print(f"    ❌ Failed: {e}")
    
    # Save raw outputs
    json_path = "quality_comparison_outputs.json"
    with open(json_path, "w") as f:
        json.dump(outputs, f, indent=2)
    print(f"\n✅ Raw outputs saved to {json_path}")
    
    # Generate HTML report
    html_report = generate_html_report(outputs)
    html_path = "quality_comparison.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_report)
    print(f"✅ HTML report saved to {html_path}")
    
    print("\n" + "=" * 80)
    print("✅ Quality comparison complete!")
    print(f"   Open {html_path} in your browser to review and rate outputs")
    print("=" * 80)
    
    return html_path


if __name__ == "__main__":
    main()