import { useState } from "react";

export default function Skills({ experienceBlocks }) {
  const [expandedBlocks, setExpandedBlocks] = useState({});

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

  const toggleExpand = (blockId) => {
    setExpandedBlocks((prev) => ({
      ...prev,
      [blockId]: !prev[blockId],
    }));
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="bg-black/60 backdrop-blur-md rounded-2xl border border-[#549E06]/30 p-4 sm:p-8 shadow-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
          My Experience & Skills
        </h2>
        <p className="text-sm sm:text-base text-gray-300 mb-8">
          This is the complete knowledge base that the RAG system uses to
          generate tailored CVs. Each block is converted to a vector embedding
          for semantic search.
        </p>

        {blockTypeOrder.map((type) => {
          const blocks = groupedBlocks[type];
          if (!blocks || blocks.length === 0) return null;

          return (
            <div key={type} className="mb-8">
              <h3 className="text-xl sm:text-2xl font-bold text-[#C6F486] mb-4">
                {blockTypeLabels[type] || type}
              </h3>

              <div className="space-y-4">
                {blocks.map((block) => {
                  const isExpanded = expandedBlocks[block.id];
                  const shouldTruncate = block.content.length > 500;
                  const displayContent =
                    isExpanded || !shouldTruncate
                      ? block.content
                      : `${block.content.substring(0, 500)}...`;

                  return (
                    <div
                      key={block.id}
                      className="bg-white/5 border border-[#549E06]/30 rounded-lg p-4 sm:p-6 hover:bg-white/10 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3 gap-2">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-lg sm:text-xl font-semibold text-white break-words">
                            {block.title}
                          </h4>
                          {block.company && (
                            <p className="text-sm sm:text-base text-[#C6F486] mt-1">
                              {block.company}
                            </p>
                          )}
                        </div>
                        {block.priority && (
                          <span className="text-xs px-2 sm:px-3 py-1 bg-[#549E06]/20 text-[#C6F486] rounded-full whitespace-nowrap">
                            Priority {block.priority}
                          </span>
                        )}
                      </div>

                      <div className="text-sm sm:text-base text-gray-300 mb-4 whitespace-pre-line">
                        {displayContent}
                        {shouldTruncate && (
                          <button
                            onClick={() => toggleExpand(block.id)}
                            className="ml-2 text-[#95E913] hover:text-[#C6F486] font-medium transition-colors underline"
                          >
                            {isExpanded ? "read less" : "read more"}
                          </button>
                        )}
                      </div>

                      {block.metadata_tags &&
                        block.metadata_tags.length > 0 && (
                          <div className="flex flex-wrap gap-2">
                            {block.metadata_tags.map((tag, i) => (
                              <span
                                key={i}
                                className="text-xs px-2 sm:px-3 py-1 bg-[#9D6777]/20 text-blue-300 rounded-full border border-[#9D6777]/30"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                    </div>
                  );
                })}
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

        <div className="mt-8 p-4 sm:p-6 bg-blue-500/10 border border-[#9D6777]/30 rounded-lg">
          <h3 className="text-lg sm:text-xl font-bold text-blue-300 mb-2">
            How Selection Works
          </h3>
          <p className="text-sm sm:text-base text-gray-300">
            When you generate a CV, the system analyzes the job description and
            selects 8-12 relevant blocks using:
          </p>
          <ul className="list-disc list-inside mt-3 space-y-1 text-sm sm:text-base text-gray-300">
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
