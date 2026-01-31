import { parseMarkdownToHTML } from "../utils/markdownParser";
import { getButtonStyle } from "../utils/buttonStyles";

// Extract markdown links from content string
function extractLinksFromMarkdown(markdown) {
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  const links = [];
  let match;

  while ((match = linkRegex.exec(markdown)) !== null) {
    links.push({ label: match[1], url: match[2] });
  }

  return links;
}

export default function StructuredCVRenderer({ cvData }) {
  if (!cvData || cvData.error) {
    return (
      <div className="text-red-400">
        Error loading CV: {cvData?.error || "Unknown error"}
      </div>
    );
  }

  const {
    header,
    summary,
    technical_strengths,
    key_projects,
    professional_experience,
    education,
    _source_chunks,
  } = cvData;

  // Get buttons for a project from its source chunk
  const getProjectButtons = (projectTitle) => {
    const sourceChunk = _source_chunks?.[projectTitle];
    if (!sourceChunk) return [];

    // Extract links from the source chunk's content
    const links = extractLinksFromMarkdown(sourceChunk.content);
    return links;
  };

  return (
    <div className="markdown-content">
      {/* Header */}
      <h1>{header.name}</h1>
      <p>
        <strong>{header.title}</strong>
        <br />
        📍 {header.location} | 📞 {header.phone} | 📧{" "}
        <a href={`mailto:${header.email}`}>{header.email}</a>
        <br />
        🔗{" "}
        <a href={header.linkedin} target="_blank" rel="noopener noreferrer">
          {header.linkedin}
        </a>{" "}
        | 🌐{" "}
        <a href={header.portfolio} target="_blank" rel="noopener noreferrer">
          {header.portfolio}
        </a>{" "}
        | 🐙{" "}
        <a href={header.github} target="_blank" rel="noopener noreferrer">
          {header.github}
        </a>
      </p>

      {/* Summary — parsed as markdown so **Laravel** renders bold */}
      <h2>🔹 Summary</h2>
      <div dangerouslySetInnerHTML={{ __html: parseMarkdownToHTML(summary) }} />

      <hr />

      {/* Technical Strengths */}
      <h2>🔹 Core Technical Strengths</h2>
      <ul>
        {Object.entries(technical_strengths).map(([category, skills]) => {
          // skills may contain markdown like **Laravel 9-12** — parse it.
          // marked wraps inline text in <p>...</p>\n so strip that wrapper
          // to keep the content inline inside the <li>.
          const skillsHtml = parseMarkdownToHTML(skills)
            .replace(/^<p>/, "")
            .replace(/<\/p>\s*$/, "");
          return (
            <li key={category}>
              <strong>{category}:</strong>{" "}
              <span dangerouslySetInnerHTML={{ __html: skillsHtml }} />
            </li>
          );
        })}
      </ul>

      <hr />

      {/* Key Projects */}
      <h2>🔹 Key Projects</h2>
      {key_projects.map((project, index) => {
        const buttons = getProjectButtons(project.title);

        return (
          <div key={index} className="mb-6">
            <p>
              <strong>{project.title}</strong>
            </p>

            {/* Project content */}
            <div
              dangerouslySetInnerHTML={{
                __html: parseMarkdownToHTML(project.content),
              }}
            />

            {/* Demo table if present */}
            {project.demo_table && (
              <table className="my-4">
                <thead>
                  <tr>
                    <th>Field</th>
                    <th>Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(project.demo_table).map(([field, value]) => (
                    <tr key={field}>
                      <td>{field}</td>
                      <td>
                        <code>{value}</code>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* Project buttons — getButtonStyle returns a single className string */}
            {buttons.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {buttons.map((link, i) => {
                  const styleClass = getButtonStyle(link.label);
                  return (
                    <a
                      key={i}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`px-3 sm:px-4 py-2 text-sm sm:text-base border rounded-lg transition-all ${styleClass}`}
                    >
                      {link.label}
                    </a>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}

      <hr />

      {/* Professional Experience */}
      <h2>🔹 Professional Experience</h2>
      <div
        dangerouslySetInnerHTML={{
          __html: parseMarkdownToHTML(professional_experience),
        }}
      />

      <hr />

      {/* Education */}
      <h2>🔹 Education</h2>
      <div
        dangerouslySetInnerHTML={{ __html: parseMarkdownToHTML(education) }}
      />
    </div>
  );
}
