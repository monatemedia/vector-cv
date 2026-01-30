import { marked } from 'marked';

// Configure marked for GitHub Flavored Markdown (includes tables)
marked.setOptions({
  breaks: true,
  gfm: true,
  tables: true
});

export const parseMarkdownToHTML = (markdown) => {
  return marked.parse(markdown);
};

// Extract button links ONLY from standalone lines (not in tables or paragraphs)
export const extractButtonLinks = (markdown) => {
  const lines = markdown.split('\n');
  const links = [];
  
  for (let line of lines) {
    const trimmed = line.trim();
    
    // Skip table rows
    if (trimmed.startsWith('|')) continue;
    
    // Skip lines that are part of paragraphs (contain text before/after link)
    // Only extract links that are on their own line or grouped together
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const matches = [...trimmed.matchAll(linkRegex)];
    
    // Check if the line ONLY contains markdown links (possibly multiple)
    if (matches.length > 0) {
      // Remove all matched links from the line
      let testLine = trimmed;
      matches.forEach(match => {
        testLine = testLine.replace(match[0], '');
      });
      
      // If what's left is just whitespace, these are standalone button links
      if (testLine.trim().length === 0) {
        matches.forEach(match => {
          links.push({
            label: match[1],
            url: match[2]
          });
        });
      }
    }
  }
  
  return links;
};

// Remove button links from markdown (but keep embedded links)
export const removeButtonLinks = (markdown) => {
  const lines = markdown.split('\n');
  const cleanedLines = lines.map(line => {
    const trimmed = line.trim();
    
    // Don't touch table rows
    if (trimmed.startsWith('|')) {
      return line;
    }
    
    // Check if this line only contains markdown links
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const matches = [...trimmed.matchAll(linkRegex)];
    
    if (matches.length > 0) {
      let testLine = trimmed;
      matches.forEach(match => {
        testLine = testLine.replace(match[0], '');
      });
      
      // If the line ONLY contains links, remove it entirely
      if (testLine.trim().length === 0) {
        return ''; // Remove this line completely
      }
    }
    
    // Keep the line as-is (it contains text + links, or just text)
    return line;
  });
  
  // Filter out empty lines that we created
  return cleanedLines.filter((line, index) => {
    // Keep line if it's not empty, or if it's an intentional blank line (surrounded by content)
    return line.trim().length > 0 || 
           (index > 0 && index < cleanedLines.length - 1 && 
            cleanedLines[index - 1].trim().length > 0 && 
            cleanedLines[index + 1].trim().length > 0);
  }).join('\n');
};