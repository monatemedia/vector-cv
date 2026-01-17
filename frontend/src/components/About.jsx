export default function About({ personalInfo }) {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8 shadow-2xl">
        <h2 className="text-4xl font-bold text-white mb-6">
          About Edward Baitsewe
        </h2>

        <div className="space-y-6 text-gray-300">
          <p className="text-lg">
            I am a full stack developer with 5 years of experience building and
            deploying scalable web applications. My expertise lies in the
            Laravel ecosystem, with deep knowledge of search optimization,
            geospatial data, and CI/CD automation.
          </p>

          <div>
            <h3 className="text-2xl font-bold text-purple-300 mb-3">
              Background
            </h3>
            <p>
              Before transitioning to software development, I spent over a
              decade in financial services as a financial advisor, where I honed
              my skills in stakeholder management, client relationships, and
              high-stakes decision-making. This unique background gives me a
              strong understanding of business needs and user experience.
            </p>
          </div>

          <div>
            <h3 className="text-2xl font-bold text-purple-300 mb-3">
              Technical Expertise
            </h3>
            <ul className="list-disc list-inside space-y-2">
              <li>
                <strong className="text-blue-400">Backend:</strong> PHP
                (Laravel), Python (Django, Flask, FastAPI)
              </li>
              <li>
                <strong className="text-blue-400">Frontend:</strong> JavaScript
                (Alpine.js, Vue.js, React), Inertia.js, Tailwind CSS
              </li>
              <li>
                <strong className="text-blue-400">Infrastructure:</strong>{" "}
                Docker, Nginx, GitHub Actions, VPS Management
              </li>
              <li>
                <strong className="text-blue-400">Specialized:</strong> Vector
                Search, RAG Architecture, Geospatial Data, AI Integration
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-2xl font-bold text-purple-300 mb-3">
              Notable Projects
            </h3>
            <div className="space-y-4">
              <div className="bg-white/5 p-4 rounded-lg border border-white/10">
                <h4 className="text-xl font-semibold text-white mb-2">
                  ActuallyFind.com
                </h4>
                <p>
                  A production vehicle marketplace featuring PostgreSQL +
                  PostGIS for geospatial queries, Typesense for sub-500ms
                  search, and Blue/Green deployment for zero-downtime updates.
                </p>
              </div>

              <div className="bg-white/5 p-4 rounded-lg border border-white/10">
                <h4 className="text-xl font-semibold text-white mb-2">
                  Vector CV
                </h4>
                <p>
                  This AI-powered resume synthesizer you're using right now,
                  showcasing my ability to build production RAG systems with
                  hybrid selection strategies and OpenAI integration.
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-4 mt-6">
            <a
              href="https://github.com/monatemedia"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/30 text-purple-300 rounded-lg transition-all"
            >
              GitHub
            </a>
            <a
              href="https://linkedin.com/in/edwardbaitsewe"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/30 text-blue-300 rounded-lg transition-all"
            >
              LinkedIn
            </a>
            <a
              href="https://monatemedia.com/portfolio"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-green-500/20 hover:bg-green-500/30 border border-green-500/30 text-green-300 rounded-lg transition-all"
            >
              Portfolio
            </a>
          </div>

          {personalInfo && (
            <div className="mt-8 p-6 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <h3 className="text-xl font-bold text-purple-300 mb-3">
                Contact Information
              </h3>
              <div className="space-y-2">
                {personalInfo.email && <p>📧 {personalInfo.email}</p>}
                {personalInfo.phone && <p>📞 {personalInfo.phone}</p>}
                {personalInfo.location && <p>📍 {personalInfo.location}</p>}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
