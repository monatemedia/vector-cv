"""
Generate Word documents from CV markdown
Converts markdown-formatted CVs to professional Word documents
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re

def parse_markdown_to_docx(markdown_text: str, output_path: str):
    """Convert markdown CV to Word document with formatting"""
    
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    lines = markdown_text.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # H1 - Name (first line starting with #)
        if line.startswith('# '):
            name = line[2:].strip()
            p = doc.add_paragraph()
            run = p.add_run(name)
            run.font.size = Pt(24)
            run.font.bold = True
            run.font.color.rgb = RGBColor(31, 78, 121)  # Dark blue
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        # Job title (bold text after name)
        elif line.startswith('**') and line.endswith('**'):
            title = line[2:-2]
            p = doc.add_paragraph()
            run = p.add_run(title)
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = RGBColor(68, 68, 68)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        # Contact info (lines with emoji or |)
        elif any(emoji in line for emoji in ['📍', '📞', '📧', '🔗', '🌐', '🐙']) or '|' in line:
            # Remove emojis and clean up
            clean_line = re.sub(r'[📍📞📧🔗🌐🐙]', '', line)
            clean_line = clean_line.replace('|', ' • ')
            p = doc.add_paragraph()
            run = p.add_run(clean_line.strip())
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(102, 102, 102)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        # H2 - Section headers (## 🔹 Section)
        elif line.startswith('## '):
            section = line[2:].strip()
            section = section.replace('🔹', '').strip()
            doc.add_paragraph()  # Add space before section
            p = doc.add_heading(section, level=2)
            p.runs[0].font.color.rgb = RGBColor(31, 78, 121)
            
        # Horizontal rule
        elif line == '---':
            doc.add_paragraph()  # Just add space, skip the line
            
        # Bullet points
        elif line.startswith('* '):
            content = line[2:].strip()
            # Parse bold text (**text**)
            content = parse_inline_formatting(content)
            p = doc.add_paragraph(style='List Bullet')
            add_formatted_text(p, content)
            
        # Project/Job headers (bold with optional link)
        elif line.startswith('**') and ('–' in line or '|' in line):
            # Parse project title
            content = parse_inline_formatting(line)
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            add_formatted_text(p, content)
            
        # Table (for demo credentials)
        elif line.startswith('|') and '---' not in line:
            # Simple table handling - just format as regular text
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and cells[0] and cells[0] != 'Field':  # Skip header row
                p = doc.add_paragraph()
                run = p.add_run(f"{cells[0]}: {cells[1]}")
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(102, 102, 102)
            
        # Regular paragraphs
        else:
            content = parse_inline_formatting(line)
            p = doc.add_paragraph()
            add_formatted_text(p, content)
        
        i += 1
    
    # Save document
    doc.save(output_path)
    return output_path

def parse_inline_formatting(text: str) -> list:
    """Parse markdown inline formatting into segments"""
    segments = []
    current = ""
    i = 0
    
    while i < len(text):
        # Bold text **text**
        if i < len(text) - 1 and text[i:i+2] == '**':
            if current:
                segments.append({'text': current, 'bold': False})
                current = ""
            # Find closing **
            end = text.find('**', i + 2)
            if end != -1:
                segments.append({'text': text[i+2:end], 'bold': True})
                i = end + 2
                continue
        
        current += text[i]
        i += 1
    
    if current:
        segments.append({'text': current, 'bold': False})
    
    return segments

def add_formatted_text(paragraph, segments):
    """Add formatted text segments to paragraph"""
    if isinstance(segments, str):
        paragraph.add_run(segments)
        return
    
    for segment in segments:
        run = paragraph.add_run(segment['text'])
        if segment.get('bold'):
            run.font.bold = True

def generate_cv_docx(cv_markdown: str, company_name: str, job_title: str, output_dir: str = "./") -> str:
    """Generate Word document from CV markdown"""
    
    # Clean filename
    filename = f"CV_{company_name}_{job_title}.docx".replace(' ', '_').replace('/', '_')
    output_path = f"{output_dir}/{filename}"
    
    parse_markdown_to_docx(cv_markdown, output_path)
    
    return output_path

def generate_cover_letter_docx(cover_letter_markdown: str, company_name: str, job_title: str, output_dir: str = "./") -> str:
    """Generate Word document from cover letter markdown"""
    
    # Clean filename
    filename = f"CoverLetter_{company_name}_{job_title}.docx".replace(' ', '_').replace('/', '_')
    output_path = f"{output_dir}/{filename}"
    
    # Cover letters are simpler, just format paragraphs
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    
    lines = cover_letter_markdown.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Skip the "# 🔹 Cover Letter" header
        if line.startswith('# '):
            continue
        
        # To/Subject lines
        if line.startswith('**To:**') or line.startswith('**Subject:**'):
            p = doc.add_paragraph()
            segments = parse_inline_formatting(line)
            add_formatted_text(p, segments)
            
        # Greeting
        elif line.startswith('Dear '):
            doc.add_paragraph()  # Add space before greeting
            doc.add_paragraph(line)
            
        # Closing
        elif line in ['Best regards,', 'Sincerely,', 'Kind regards,']:
            doc.add_paragraph()  # Add space before closing
            p = doc.add_paragraph(line)
            
        # Contact info at end
        elif any(char in line for char in ['+27', '@']):
            doc.add_paragraph(line)
            
        # Regular paragraphs
        else:
            segments = parse_inline_formatting(line)
            p = doc.add_paragraph()
            add_formatted_text(p, segments)
    
    doc.save(output_path)
    
    return output_path

# Example usage for testing
if __name__ == "__main__":
    sample_cv = """# Edward Baitsewe
**Full Stack Developer**
📍 Parow, Cape Town | 📞 +27 78 324 5326 | 📧 edward@monatemedia.com

## 🔹 Summary
Full stack developer with 5 years of experience building and deploying scalable webapps.

---

## 🔹 Core Technical Strengths
* **Backend:** Laravel, PHP, Python
* **Frontend:** React, Vue.js, Tailwind CSS
* **Infrastructure:** Docker, Nginx, GitHub Actions

---

## 🔹 Key Projects

**ActuallyFind – Vehicle Marketplace SaaS** | https://actuallyfind.com

* **Marketplace Architecture:** Engineered a high-performance marketplace using **Laravel** and **PostgreSQL + GIS**.
* **Search Optimization:** Integrated **Typesense** for instant full-text search.
"""
    
    generate_cv_docx(sample_cv, "TestCompany", "Developer", "./")
    print("✅ Test CV generated: CV_TestCompany_Developer.docx")