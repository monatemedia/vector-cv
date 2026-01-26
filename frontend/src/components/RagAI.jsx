import { Github } from "lucide-react";

export default function RagAI() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-black/60 backdrop-blur-md rounded-2xl border border-[#549E06]/30 p-8 shadow-2xl">
        <h2 className="text-4xl font-bold text-white mb-6">What is RAG AI?</h2>

        <div className="space-y-6 text-gray-300">
          <p className="text-lg">
            RAG stands for{" "}
            <strong className="text-[#C6F486]">
              Retrieval-Augmented Generation
            </strong>{" "}
            - a powerful AI architecture that combines information retrieval
            with large language model generation to create highly accurate,
            contextual responses.
          </p>

          <div>
            <h3 className="text-2xl font-bold text-[#C6F486] mb-3">
              How Vector CV Works
            </h3>
            <ol className="list-decimal list-inside space-y-4">
              <li>
                <strong className="text-[#ADB5D6]">Embeddings:</strong> All my
                experience blocks are converted into 1024-dimensional vectors
                using OpenAI's text-embedding-3-small model. These vectors
                capture the semantic meaning of the text.
              </li>
              <li>
                <strong className="text-[#ADB5D6]">Vector Database:</strong>{" "}
                Vectors are stored in PostgreSQL with the pgvector extension,
                enabling lightning-fast similarity searches through cosine
                distance calculations.
              </li>
              <li>
                <strong className="text-[#ADB5D6]">Hybrid Selection:</strong>{" "}
                When you paste a job description, the system uses three
                strategies:
                <ul className="list-disc list-inside ml-6 mt-2 space-y-1">
                  <li>Vector similarity search (cosine distance)</li>
                  <li>Skill matching (keyword extraction)</li>
                  <li>
                    Priority-based selection (pillar projects always included)
                  </li>
                </ul>
              </li>
              <li>
                <strong className="text-[#ADB5D6]">AI Generation:</strong>{" "}
                Selected blocks are sent to GPT-4 along with sophisticated
                prompts that include few-shot examples and anti-hallucination
                guards to generate a tailored CV and cover letter in my exact
                writing style.
              </li>
            </ol>
          </div>

          <div>
            <h3 className="text-2xl font-bold text-[#C6F486] mb-3">
              Why This Matters
            </h3>
            <p>
              Traditional CV generation tools use templates. Vector CV
              understands the <em>semantic relationship</em> between your
              experience and job requirements, ensuring every CV highlights the
              most relevant skills and projects. The result? CVs that pass ATS
              systems and resonate with hiring managers.
            </p>
          </div>

          <div>
            <h3 className="text-2xl font-bold text-[#C6F486] mb-3">
              Technical Implementation
            </h3>
            <div className="bg-black/30 p-4 rounded-lg border border-[#549E06]/30 space-y-3">
              <p>
                <strong className="text-green-400">Architecture:</strong>{" "}
                Microservices with Nginx Reverse Proxy
              </p>
              <p>
                <strong className="text-green-400">Backend:</strong> FastAPI
                (Python 3.12), SQLAlchemy, Uvicorn
              </p>
              <p>
                <strong className="text-green-400">Database:</strong> PostgreSQL
                17 + <code className="text-[#C6F486]">pgvector</code> extension
              </p>
              <p>
                <strong className="text-green-400">AI/LLM:</strong> GPT-4o &
                text-embedding-3-small (1536d)
              </p>
              <p>
                <strong className="text-green-400">DevOps:</strong> Multi-stage
                Docker Builds, GitHub Actions CI/CD, Streamlit Admin
              </p>
            </div>
          </div>

          <div>
            <h3 className="text-2xl font-bold text-[#C6F486] mb-3">
              The Problem It Solves
            </h3>
            <p>
              Job hunting is tedious. Tailoring a CV for each application takes
              30-60 minutes. Vector CV automates this while maintaining quality
              by:
            </p>
            <ul className="list-disc list-inside space-y-2 mt-3">
              <li>Automatically selecting the most relevant experience</li>
              <li>Highlighting skills that match the job requirements</li>
              <li>Maintaining consistent voice and formatting</li>
              <li>Generating cover letters that reference specific projects</li>
              <li>Providing skills gap analysis for self-improvement</li>
            </ul>
          </div>

          <div className="mt-8 p-6 bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-[#549E06]/30 rounded-lg">
            <div className="flex items-start gap-4">
              <Github className="w-8 h-8 text-[#C6F486] shrink-0 mt-1" />
              <div>
                <h3 className="text-xl font-bold text-white mb-2">
                  Open Source
                </h3>
                <p className="mb-3">
                  The complete source code for Vector CV is available on GitHub.
                  Feel free to explore the implementation, learn from it, or
                  adapt it for your own use.
                </p>
                <a
                  href="https://github.com/monatemedia/vector-cv"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block px-6 py-2 bg-[#549E06]/20 hover:bg-purple-500/30 border border-[#549E06]/30 text-[#C6F486] rounded-lg transition-all"
                >
                  View on GitHub
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
