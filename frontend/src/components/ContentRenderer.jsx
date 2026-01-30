import { getButtonStyle } from "../utils/buttonStyles";
import {
  extractButtonLinks,
  removeButtonLinks,
  parseMarkdownToHTML,
} from "../utils/markdownParser";

export default function ContentRenderer({ content }) {
  // Extract buttons and clean content
  const buttons = extractButtonLinks(content);
  const cleanContent = removeButtonLinks(content);

  // Parse to HTML
  const htmlContent = parseMarkdownToHTML(cleanContent);

  return (
    <>
      {/* Rendered HTML content */}
      <div
        className="markdown-content mb-4"
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />

      {/* Button links */}
      {buttons.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-4">
          {buttons.map((button, index) => (
            <a
              key={index}
              href={button.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`px-3 sm:px-4 py-2 text-sm sm:text-base border rounded-lg transition-all ${getButtonStyle(button.label)}`}
            >
              {button.label}
            </a>
          ))}
        </div>
      )}
    </>
  );
}
