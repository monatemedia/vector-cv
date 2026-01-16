import os
import json
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embedding(text: str) -> List[float]:
    """Generate embeddings using OpenAI's text-embedding-3-small model"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=1024
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        import hashlib
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        vector = []
        for i in range(1024):
            vector.append((hash_bytes[i % len(hash_bytes)] / 255.0) * 2 - 1)
        return vector

def analyze_skills_gap(candidate_chunks: List[Dict], job_description: str) -> Dict:
    """Identify skills gaps with technical precision"""
    chunks_text = "\n\n".join([
        f"**{chunk['title']} at {chunk['company']}**\n{chunk['content']}\nSkills: {', '.join(chunk['metadata_tags'])}"  
        for chunk in candidate_chunks
    ])

    prompt = f"""You are a Technical Lead analyzing a candidate for a role.

    CANDIDATE EXPERIENCE:
    {chunks_text}

    JOB DESCRIPTION:
    {job_description}

    Analyze the skills gap. Be specific about versions and ecosystems (e.g., 'Laravel' vs 'PHP').
    Return ONLY valid JSON:
    {{
        "missing_skills": [],
        "matching_skills": [],
        "partial_matches": [],
        "recommendations": []
    }}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "system", "content": "You are a technical recruiter who values data over fluff."},       
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

def generate_tailored_cv(
    personal_info: Dict,
    relevant_chunks: List[Dict],
    job_description: str,
    style_guidelines: List[Dict] = None) -> str:
    """Generate a tailored CV matching Edward's exact style and voice"""

    chunks_text = "\n\n".join([
        f"BLOCK: {chunk['title']} at {chunk['company']}\nCONTENT: {chunk['content']}\nTAGS: {', '.join(chunk['metadata_tags'])}"
        for chunk in relevant_chunks
    ])

    guidelines_text = "\n".join([f"- {g['name']}: {g['description']}" for g in (style_guidelines or [])])

    system_prompt = """You are Edward Baitsewe's CV writer. Your job is to mimic his EXACT writing style and formatting.

CRITICAL ANTI-FABRICATION RULES:
1. SOURCE OF TRUTH: Use ONLY the provided candidate data blocks. If information is not explicitly in the data, DO NOT INCLUDE IT.
2. NO INVENTED CREDENTIALS: Never invent degrees, certifications, company names, dates, or project names.
3. NO PLACEHOLDER DATES: If dates are not provided, omit them entirely. Do not use "2018-Present" or similar unless explicitly given.
4. NO GENERIC CERTIFICATIONS: Do not add "Certified Laravel Developer" or similar unless explicitly listed in the data.

EDWARD'S CV STYLE FINGERPRINT:
- Uses emoji section markers: 🔹 for sections
- Uses contact emojis in header: 📍 📞 📧 🔗 🌐 🐙
- Quantifies with special notation: "~77×", "sub-500ms", "99.9%"
- Bold-highlights technologies: **Laravel**, **PostgreSQL + GIS**, **Typesense**
- Bullet points start with "* " not "- "
- Section headers: "## 🔹 Section Name"
- Uses developer-centric language: "Engineered", "Implemented", "Integrated" (NOT "Spearheaded", "Championed", "Leveraging")
- Includes demo credentials when relevant (see example below)
- CONCISE: One line per bullet when possible, no wordy expansions

FORBIDDEN PHRASES (NEVER USE THESE):
- "leveraging" / "utilizing" (use specific tech names directly)
- "demonstrating proficiency" (just state what was done)
- "showcasing ability" (too meta, just show it)
- "honed skills" / "instilled" / "equipped me with"
- Any passive voice construction

STRUCTURE TEMPLATE (Follow this EXACTLY):
```
# [Name]
**[Title]**
📍 [Location] | 📞 [Phone] | 📧 [Email]
🔗 [LinkedIn] | 🌐 [Portfolio] | 🐙 [GitHub]

## 🔹 Summary
[2-3 sentence punchy summary mentioning years of experience, core tech stack, and key differentiator]

---

## 🔹 Core Technical Strengths
* **Backend:** [List]
* **Frontend:** [List]
* **Infrastructure:** [List]
* **Specialized:** [List]

---

## 🔹 Key Projects
[Project listings with this format]

**[Project Name] – [Type]** | [URL if provided]

* **[Category]:** [Achievement with metrics]
* **[Category]:** [Achievement with metrics]

[If demo credentials exist in source data, include this table:]
| Field | Value |
|-------|-------|
| URL | [url] |
| Email | [email] |
| Password | [password] |
| Test VIN | [vin if applicable] |

---

## 🔹 Professional Experience

**[Title]** | *[Company]* | [Dates if provided]

* [Achievement bullet points using Edward's voice]

---

## 🔹 Education

* **[Degree]** – [Institution]
* **Online Certifications:** [List]
```

VOICE EXAMPLES (Learn the pattern, don't copy):

BAD: "Leveraging Laravel and PostgreSQL, I demonstrated proficiency in building scalable systems"
GOOD: "Engineered a high-performance marketplace using **Laravel** and **PostgreSQL + GIS**"

BAD: "Utilized modern DevOps practices to improve deployment efficiency"
GOOD: "Implemented a zero-downtime **Blue/Green deployment** strategy via GitHub Actions"

BAD: "Optimized image processing to enhance application performance"
GOOD: "Achieved ~77× image compression (1.7MB to 22KB WebP)"

BAD: "Developed a microservice showcasing ability to bridge polyglot environments"
GOOD: "Developed a **Python/Flask** microservice, bridging polyglot environments (PHP/Python)"

SUMMARY TAILORING RULE:
The summary should be MOSTLY fixed but with ONE sentence tailored to the job. Structure:
- Sentence 1: Years of experience + core tech (always the same)
- Sentence 2: Specific expertise relevant to THIS job (tailored)
- Sentence 3: Professional background differentiator (always the same)

Example for a Laravel/Marketplace role:
"Full stack developer with 5 years of experience building and deploying scalable webapps. Expert in the **Laravel** ecosystem with a deep focus on search optimization, geospatial data, and CI/CD automation. Former financial advisor with over a decade track record of high-stakes stakeholder management and client service excellence."
"""

    user_prompt = f"""
CANDIDATE DATA:
Name: {personal_info.get('name')}
Email: {personal_info.get('email')}
Phone: {personal_info.get('phone')}
Location: {personal_info.get('location')}
LinkedIn: {personal_info.get('linkedin')}
GitHub: {personal_info.get('github')}
Portfolio: {personal_info.get('portfolio')}
Summary: {personal_info.get('summary')}

EXPERIENCE BLOCKS (USE ONLY THIS DATA - DO NOT INVENT ANYTHING):
{chunks_text}

TARGET JOB:
{job_description}

STYLE GUIDELINES:
{guidelines_text}

CRITICAL INSTRUCTIONS:
1. Include ALL contact links in the header (LinkedIn, Portfolio, GitHub) - DO NOT OMIT THE PORTFOLIO URL
2. In the Summary, identify the 1-2 most relevant aspects of the job and highlight those specific skills (e.g., "geospatial data" for a location-based role)
3. For each project, use the EXACT formatting from the source blocks - don't expand or reword
4. If a source block includes GitHub links or demo credentials, INCLUDE THEM VERBATIM
5. Keep bullet points CONCISE - one line when possible
6. NO PASSIVE VOICE - use direct action verbs
7. Extract education from the "Education & Certifications" block if present

EXAMPLE OF CORRECT VinScape FORMATTING:
**VinScape – VIN Decoder Microservice** | [GitHub](https://github.com/monatemedia/vinscape)

* Developed a specialized **Python/Flask** microservice for vehicle data enrichment, showcasing the ability to bridge polyglot environments (PHP/Python) to solve specific business logic needs.

(Note: One bullet, concise, includes GitHub link, uses exact wording from source)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2  # Very low for maximum consistency
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def generate_cover_letter(
    personal_info: Dict,
    relevant_chunks: List[Dict],
    job_description: str,
    company_name: str,
    job_title: str) -> str:
    """Generate a cover letter using Edward's 'DNA matching' strategy"""

    chunks_text = "\n\n".join([
        f"PROJECT: {chunk['title']}\nDETAILS: {chunk['content']}"
        for chunk in relevant_chunks[:3]
    ])

    system_prompt = """You are Edward Baitsewe's cover letter writer. Your job is to use his "DNA MATCHING" strategy.

EDWARD'S COVER LETTER VOICE:
- Conversational but professional (peer-to-peer, engineer to engineer)
- Direct and confident (no hedging with "I believe" or "I think")
- Specific technical details (actual tech stacks, not "modern practices")
- Shows domain knowledge (understands their product/challenges)
- Uses active voice exclusively

FORBIDDEN PHRASES (NEVER USE THESE):
- "vibrant tech scene" / "remarkable journey" / "deeply immersed"
- "has equipped me with" / "has instilled in" / "has honed"
- "I've been closely following"
- "look forward to the possibility of discussing"
- "contribute meaningfully"
- Any passive constructions

STRATEGY STRUCTURE:
```
# 🔹 Cover Letter

**To:** [Hiring Manager Name if provided, otherwise "Hiring Team"]
**Subject:** [Job Title] Application - Edward Baitsewe

Dear [Name],

[HOOK - 2-3 sentences showing domain expertise and why you care about their product]

[DNA MATCH - Show how YOUR specific project shares technical DNA with THEIR challenges. Be concrete.]

[BONUS SKILLS - Address "Bonus" requirements from job description with specific examples from your experience]

[PROFESSIONAL MATURITY - One paragraph on the financial background as a differentiator for soft skills]

[FORWARD-LOOKING - Show excitement about specific tech initiatives they mentioned (AI/ML, new products, etc.)]

Thank you for your time and for considering my application. I look forward to discussing how my experience with [specific tech] and [specific domain] can contribute to [Company]'s continued success.

Best regards,

Edward Baitsewe
+27 78 324 5326
edward@monatemedia.com
```

HOOK EXAMPLES (Learn the pattern):

BAD: "As a Full Stack Developer deeply immersed in the vibrant tech scene of Cape Town, I've been closely following your remarkable journey"
GOOD: "As a Cape Town-based developer who has spent the last few years building marketplace logic from the ground up, I have long admired how [Company] handles the complexity of [their domain] at scale"

The good version: (1) Shows actual work experience, (2) Demonstrates understanding of their challenges, (3) Natural language

DNA MATCH EXAMPLES:

BAD: "My project, ActuallyFind, mirrors the technical DNA of LekkeSlaap's challenges and ambitions. At its core, ActuallyFind is built using Laravel for the backend"
GOOD: "My core project, **ActuallyFind**, shares a striking DNA with the LekkeSlaap platform. It is a high-traffic vehicle marketplace built on **Laravel** that utilizes **PostgreSQL + GIS** for location-based searches—the same technical challenges involved in helping a user find the perfect 'lekke' stay nearby."

The good version: (1) Bold confidence ("striking DNA"), (2) Specific technical parallel (GIS for location), (3) Shows product understanding (makes a "lekke" pun), (4) Uses bold for tech

BONUS SKILLS EXAMPLES:

BAD: "In addressing the 'Bonus' requirements mentioned in the job description, I bring hands-on experience with Docker"
GOOD: "Beyond just writing code, I have a deep passion for the 'Bonus' requirements in your listing: I manage my own containerized VPS environments using **Docker** and **Nginx**"

The good version: (1) Direct quote of "Bonus", (2) Shows ownership ("my own"), (3) Specific tech combo

CLOSING EXAMPLES:

BAD: "I look forward to the possibility of discussing how my background, skills, and enthusiasms can contribute to the innovative work being done at [Company]"
GOOD: "Thank you for your time and for considering my application. I look forward to discussing how my experience with Laravel and marketplace architecture can contribute to Tripco's continued success."

The good version: (1) Brief thank you, (2) Specific mention of relevant tech, (3) Direct language
"""

    user_prompt = f"""
CANDIDATE: {personal_info.get('name')}
LOCATION: {personal_info.get('location')}
JOB: {job_title} at {company_name}

CANDIDATE'S RELEVANT PROJECTS:
{chunks_text}

JOB DESCRIPTION (Identify their technical DNA, "Bonus" requirements, and specific initiatives):
{job_description}

INSTRUCTIONS:
1. HOOK: Identify their technical DNA (e.g., "Marketplace + Location + Scale" for LekkeSlaap). Open with domain knowledge.
2. DNA MATCH: Find Edward's project that matches their DNA. For marketplace/search roles, it's usually ActuallyFind. Draw SPECIFIC technical parallels (e.g., "we both use GIS for location filtering").
3. If the company has a unique name or term (like "lekke" in LekkeSlaap), work it naturally into the DNA paragraph as a pun or reference.
4. BONUS SKILLS: Quote "Bonus" if they use that word. Address each bonus requirement with a specific example from the experience blocks.
5. PROFESSIONAL MATURITY: Mention the 10-year financial services background for stakeholder management and ownership mindset.
6. FORWARD-LOOKING: If they mention AI/ML, new products, or specific initiatives, express genuine excitement with specifics.
7. CLOSING: Use the formula "Thank you for your time and for considering my application. I look forward to discussing how my experience with [specific tech/domain] can contribute to [Company]'s continued success."
8. Keep the whole letter under 400 words.
9. Use bold for technologies (**Laravel**, **Docker**)
10. NO PASSIVE VOICE - use direct active constructions
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4  # Lower than before for more consistent voice
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"