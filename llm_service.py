import os
import json
import re
import time
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv
from api_logger import get_logger

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = get_logger()

def generate_embedding(text: str) -> List[float]:
    """Generate embeddings using OpenAI's text-embedding-3-small model"""
    start_time = time.time()
    request_id = None
    
    try:
        # Log request
        request_id = logger.log_request(
            operation="generate_embedding",
            model="text-embedding-3-small",
            input_text=text,
            dimensions=1024
        )
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=1024
        )
        
        # Log response
        logger.log_response(request_id, response)
        
        # Log timing
        duration_ms = (time.time() - start_time) * 1000
        logger.log_summary("generate_embedding", duration_ms)
        
        return response.data[0].embedding
        
    except Exception as e:
        print(f"Error generating embedding: {e}")
        
        # Log error
        if request_id:
            logger.log_response(request_id, None, error=e)
        
        # Fallback to hash-based vector
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        vector = []
        for i in range(1024):
            vector.append((hash_bytes[i % len(hash_bytes)] / 255.0) * 2 - 1)
        return vector

def extract_skills_from_job(job_description: str) -> List[str]:
    """Extract technical skills and technologies from job description"""
    start_time = time.time()
    request_id = None
    
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
    {job_description}

    Example output format:
    {{"skills": ["React", "Docker", "PostgreSQL", "AWS", "Laravel"]}}
    """

    try:
        messages = [{"role": "user", "content": prompt}]
        
        # Log request
        request_id = logger.log_request(
            operation="extract_skills_from_job",
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Log response
        logger.log_response(request_id, response)
        
        # Log timing
        duration_ms = (time.time() - start_time) * 1000
        logger.log_summary("extract_skills_from_job", duration_ms)
        
        result = json.loads(response.choices[0].message.content)
        return result.get("skills", [])
        
    except Exception as e:
        print(f"Error extracting skills: {e}")
        
        # Log error
        if request_id:
            logger.log_response(request_id, None, error=e)
        
        return []

def analyze_skills_gap(candidate_chunks: List[Dict], job_description: str, all_candidate_skills: List[str] = None) -> Dict:
    """Identify skills gaps with technical precision"""
    start_time = time.time()
    request_id = None

    chunks_text = "\n\n".join([
        f"**{chunk['title']} at {chunk['company']}**\n{chunk['content']}\nSkills: {', '.join(chunk['metadata_tags'])}"
        for chunk in candidate_chunks
    ])
    
    # Add comprehensive skills context if provided
    skills_context = ""
    if all_candidate_skills:
        skills_context = f"\n\nIMPORTANT - CANDIDATE'S COMPLETE SKILL SET:\nThe candidate also has experience with these skills (may not all be shown in the experience blocks above): {', '.join(all_candidate_skills)}\n"

    prompt = f"""You are a Technical Lead analyzing a candidate for a role.

CANDIDATE EXPERIENCE (MOST RELEVANT BLOCKS):
{chunks_text}
{skills_context}

JOB DESCRIPTION:
{job_description}

Analyze the skills gap. Be specific about versions and ecosystems (e.g., 'Laravel' vs 'PHP').

IMPORTANT: When checking for matching skills, consider BOTH:
1. Skills explicitly mentioned in the experience blocks above
2. Skills listed in the candidate's complete skill set

Return ONLY valid JSON:
{{
    "missing_skills": [],
    "matching_skills": [],
    "partial_matches": [],
    "recommendations": []
}}"""

    try:
        messages = [
            {"role": "system", "content": "You are a technical recruiter who values data over fluff."},
            {"role": "user", "content": prompt}
        ]
        
        # Log request
        request_id = logger.log_request(
            operation="analyze_skills_gap",
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Log response
        logger.log_response(request_id, response)
        
        # Log timing
        duration_ms = (time.time() - start_time) * 1000
        logger.log_summary("analyze_skills_gap", duration_ms)
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error analyzing skills gap: {e}")
        
        # Log error
        if request_id:
            logger.log_response(request_id, None, error=e)
        
        return {"error": str(e)}

def generate_tailored_cv(
    personal_info: Dict,
    relevant_chunks: List[Dict],
    job_description: str,
    style_guidelines: List[Dict] = None) -> Dict:
    """Generate a tailored CV as structured JSON"""
    start_time = time.time()
    request_id = None

    # Create a mapping of project titles to their original chunks (for button matching later)
    chunks_map = {chunk['title']: chunk for chunk in relevant_chunks}

    chunks_text = "\n\n".join([
        f"BLOCK: {chunk['title']} at {chunk['company']}\nCONTENT: {chunk['content']}\nTAGS: {', '.join(chunk['metadata_tags'])}"
        for chunk in relevant_chunks
    ])

    system_prompt = """You are Edward Baitsewe's expert CV writer. Return a structured JSON CV.

CRITICAL RULES:
1. Use ONLY the provided candidate data blocks
2. NO invented credentials, dates, certifications, or company names
3. NO placeholder dates unless explicitly given

EDWARD'S VOICE:
- Developer-centric: "Engineered", "Implemented", "Integrated" (NOT "Spearheaded", "Leveraging")
- Quantifies with notation: "~77×", "sub-500ms", "99.9%"
- Bold-highlights tech: **Laravel**, **PostgreSQL + GIS**
- Concise bullets, no fluff
- Bullet points start with "* " not "- "

FORBIDDEN PHRASES:
- "leveraging" / "utilizing"
- "demonstrating proficiency"
- "honed skills" / "equipped me with"
- Any passive voice

JSON STRUCTURE (return this exactly):
{
  "header": {
    "name": "Edward Baitsewe",
    "title": "Full Stack Developer",
    "location": "Parow, Cape Town",
    "phone": "+27 78 324 5326",
    "email": "edward@monatemedia.com",
    "linkedin": "url",
    "portfolio": "url",
    "github": "url"
  },
  "summary": "2-3 sentence summary with job-specific middle sentence",
  "technical_strengths": {
    "Backend": "PHP (Laravel 9-12), Python, etc",
    "Frontend": "JavaScript, React, etc",
    "Infrastructure": "Docker, Nginx, etc",
    "Specialized": "PostgreSQL + PostGIS, etc"
  },
  "key_projects": [
    {
      "title": "ActuallyFind – Core Platform",
      "content": "**Production Marketplace:** description\\n**Tech Stack:** **Laravel 11**, **PostgreSQL**\\n**Search:** details",
      "demo_table": {
        "URL": "https://dealership.monatemedia.com/",
        "Email": "user@example.com",
        "Password": "password",
        "Test VIN": "AFAVXDL44VR135790"
      }
    },
    {
      "title": "ActuallyFind – DevOps & Infrastructure",
      "content": "**Zero-Downtime:** description\\n**Infrastructure:** details"
    }
  ],
  "professional_experience": "**Title** | *Company* | Dates\\n\\n* Achievement 1\\n* Achievement 2",
  "education": "* **Degree** – Institution\\n* **Certifications:** List"
}

IMPORTANT:
- Each key_projects entry has "title" matching EXACTLY the block title from source data
- "content" is markdown WITHOUT project title (title is separate)
- Use \\n for line breaks in content
- Bold tech with **technology**
- demo_table is optional, only if demo credentials exist in source
- Keep content concise - one line per bullet when possible
"""

    user_prompt = f"""
CANDIDATE DATA:
{json.dumps(personal_info, indent=2)}

EXPERIENCE BLOCKS:
{chunks_text}

TARGET JOB:
{job_description}

INSTRUCTIONS:
1. Extract exact contact info from personal data (don't omit portfolio!)
2. Tailor summary middle sentence to job (keep first and last sentences consistent)
3. For each experience block, create a key_projects entry with:
   - title: EXACT block title (e.g., "ActuallyFind – Core Platform")
   - content: markdown description (no title, just bullet points)
   - demo_table: only if demo credentials exist in source
4. Keep technical_strengths consistent but prioritize job-relevant tech
5. Extract professional_experience and education from blocks
6. Be concise - match Edward's punchy style

Return ONLY valid JSON.
"""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Log request
        request_id = logger.log_request(
            operation="generate_tailored_cv",
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        # Log response
        logger.log_response(request_id, response)
        
        # Log timing
        duration_ms = (time.time() - start_time) * 1000
        logger.log_summary("generate_tailored_cv", duration_ms)
        
        cv_data = json.loads(response.choices[0].message.content)

        # Add source_chunks mapping for frontend button matching
        cv_data["_source_chunks"] = chunks_map

        return cv_data
        
    except Exception as e:
        print(f"Error generating CV: {e}")
        
        # Log error
        if request_id:
            logger.log_response(request_id, None, error=e)
        
        return {"error": str(e)}

def generate_cover_letter(
    personal_info: Dict,
    relevant_chunks: List[Dict],
    job_description: str,
    company_name: str,
    job_title: str,
    all_candidate_skills: List[str] = None) -> str:  # ADD THIS PARAMETER
    """Generate a cover letter using Edward's 'DNA matching' strategy"""
    start_time = time.time()
    request_id = None

    chunks_text = "\n\n".join([
        f"PROJECT: {chunk['title']}\nDETAILS: {chunk['content']}"
        for chunk in relevant_chunks[:3]
    ])

    # Extract candidate's actual skills from chunks (keep this for backward compatibility)
    candidate_tags = []
    for chunk in relevant_chunks:
        candidate_tags.extend(chunk.get('metadata_tags', []))
    candidate_skills = list(set(candidate_tags))  # Remove duplicates
    
    # Use all_candidate_skills if provided, otherwise fall back to chunk-based skills
    skills_to_use = all_candidate_skills if all_candidate_skills else candidate_skills

    system_prompt = """You are Edward Baitsewe's cover letter writer. Your job is to use his "DNA MATCHING" strategy.

CRITICAL SKILLS GAP AWARENESS:
You must be HONEST about the candidate's skills. Use ONLY skills that appear in the candidate's project tags.    
NEVER claim proficiency in skills the candidate doesn't have.
If the job requires skills the candidate lacks, focus on TRANSFERABLE skills and genuine enthusiasm to learn.    
Be confident about what the candidate CAN do, honest about what they're still developing.

EDWARD'S COVER LETTER VOICE:
- Conversational but professional (peer-to-peer, engineer to engineer)
- Direct and confident (no hedging with "I believe" or "I think")
- Specific technical details (actual tech stacks, not "modern practices")
- Shows domain knowledge (understands their product/challenges)
- Uses active voice exclusively
- HONEST about skill gaps while emphasizing transferable experience

FORBIDDEN PHRASES (NEVER USE THESE):
- "vibrant tech scene" / "remarkable journey" / "deeply immersed"
- "has equipped me with" / "has instilled in" / "has honed"
- "I've been closely following"
- "look forward to the possibility of discussing"
- "contribute meaningfully"
- Any passive constructions
- Claims of expertise in skills not in the candidate's tags

STRATEGY STRUCTURE:
```
# 🔹 Cover Letter

**To:** [Hiring Manager Name if provided, otherwise "Hiring Team"]
**Subject:** [Job Title] Application - Edward Baitsewe

Dear [Name],

[HOOK - 2-3 sentences showing domain expertise and why you care about their product]

[DNA MATCH - Show how YOUR specific project shares technical DNA with THEIR challenges. Be concrete. Use ONLY skills the candidate actually has.]

[BONUS SKILLS - Address "Bonus" requirements from job description with HONEST assessment - if you have the skill, show it; if not, acknowledge transferable skills]

[PROFESSIONAL MATURITY - One paragraph on the financial background as a differentiator]

[FORWARD-LOOKING - Show genuine excitement about learning new technologies if needed, or contributing existing expertise]

Thank you for your time and for considering my application. I look forward to discussing how my experience with [specific tech the candidate ACTUALLY knows] can contribute to [Company]'s continued success.

Best regards,

Edward Baitsewe
+27 78 324 5326
edward@monatemedia.com
```
"""

    user_prompt = f"""
CANDIDATE: {personal_info.get('name')}
LOCATION: {personal_info.get('location')}
JOB: {job_title} at {company_name}

CANDIDATE'S COMPLETE SKILL SET (from all experience):
{', '.join(skills_to_use)}

CANDIDATE'S MOST RELEVANT PROJECTS (detailed):
{chunks_text}

JOB DESCRIPTION:
{job_description}

INSTRUCTIONS:
1. HOOK: Identify their technical DNA. Open with domain knowledge.
2. DNA MATCH: Find Edward's project that matches their DNA. Draw SPECIFIC technical parallels using ONLY skills from the candidate's complete skill set.
3. BONUS SKILLS: Quote "Bonus" if they use that word. Be HONEST - if the candidate has the skill (check complete skill set), show concrete examples. If not, acknowledge transferable skills.
4. NEVER claim expertise in technologies not in the candidate's complete skill set.
5. PROFESSIONAL MATURITY: Mention the 10-year financial services background.
6. FORWARD-LOOKING: If there are skill gaps, show enthusiasm to learn. If skills match well, express excitement about contributing.
7. CLOSING: "Thank you for your time and for considering my application. I look forward to discussing how my experience with [specific tech FROM candidate's skill set] can contribute to [Company]'s continued success."
8. Keep under 400 words.
9. Use bold for technologies (**Laravel**, **Docker**) but ONLY for technologies in the candidate's complete skill set.
10. NO PASSIVE VOICE
11. BE HONEST - integrity matters more than claiming false expertise
"""

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # Log request
        request_id = logger.log_request(
            operation="generate_cover_letter",
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.4
        )
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.4
        )
        
        # Log response
        logger.log_response(request_id, response)
        
        # Log timing
        duration_ms = (time.time() - start_time) * 1000
        logger.log_summary("generate_cover_letter", duration_ms)
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        
        # Log error
        if request_id:
            logger.log_response(request_id, None, error=e)
        
        return f"Error: {str(e)}"