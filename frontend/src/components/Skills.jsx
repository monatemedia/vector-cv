export default function Skills({ experienceBlocks }) {
  const blockTypeLabels = {
    pillar_project: "⭐ Pillar Projects",
    supporting_project: "🔧 Supporting Projects",
    employment: "💼 Employment History",
    education: "🎓 Education",
    skills_summary: "💡 Skills Summary",
  };

  const blockTypeOrder = [
    "skills_summary",
    "pillar_project",
    "supporting_project",
    "employment",
    "education",
  ];

  const groupedBlocks = experienceBlocks.reduce((acc, block) => {
    const type = block.block_type || "supporting_project";
    if (!acc[type]) acc[type] = [];
    acc[type].push(block);
    return acc;
  }, {});

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8 shadow-2xl">
        <h2 className="text-4xl font-bold text-white mb-4">
          My Experience & Skills
        </h2>
        <p className="text-gray-300 mb-8">
          This is the complete knowledge base that the RAG system uses to
          generate tailored CVs. Each block is converted to a vector embedding
          for semantic search.
        </p>

        {blockTypeOrder.map((type) => {
          const blocks = groupedBlocks[type];
          if (!blocks || blocks.length === 0) return null;

          return (
            <div key={type} className="mb-8">
              <h3 className="text-2xl font-bold text-purple-300 mb-4">
                {blockTypeLabels[type] || type}
              </h3>

              <div className="space-y-4">
                {blocks.map((block) => (
                  <div
                    key={block.id}
                    className="bg-white/5 border border-white/10 rounded-lg p-6 hover:bg-white/10 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="text-xl font-semibold text-white">
                          {block.title}
                        </h4>
                        {block.company && (
                          <p className="text-purple-300 mt-1">
                            {block.company}
                          </p>
                        )}
                      </div>
                      {block.priority && (
                        <span className="text-xs px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full">
                          Priority {block.priority}
                        </span>
                      )}
                    </div>

                    <div className="text-gray-300 mb-4 whitespace-pre-line">
                      {block.content.length > 500
                        ? `${block.content.substring(0, 500)}...`
                        : block.content}
                    </div>

                    {block.metadata_tags && block.metadata_tags.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {block.metadata_tags.map((tag, i) => (
                          <span
                            key={i}
                            className="text-xs px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full border border-blue-500/30"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {experienceBlocks.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">
              No experience blocks found. The database may be empty.
            </p>
          </div>
        )}

        <div className="mt-8 p-6 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <h3 className="text-xl font-bold text-blue-300 mb-2">
            How Selection Works
          </h3>
          <p className="text-gray-300">
            When you generate a CV, the system analyzes the job description and
            selects 8-12 relevant blocks using:
          </p>
          <ul className="list-disc list-inside mt-3 space-y-1 text-gray-300">
            <li>
              <strong>Pillar projects</strong> are always included
            </li>
            <li>
              <strong>Skills summary</strong> is always included
            </li>
            <li>
              <strong>Skill matching</strong> finds blocks with required
              technologies
            </li>
            <li>
              <strong>Vector similarity</strong> finds semantically related
              experience
            </li>
            <li>
              <strong>Priority ranking</strong> ensures the most relevant
              content comes first
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
