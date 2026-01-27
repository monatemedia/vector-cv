export default function About({ personalInfo }) {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-black/60 backdrop-blur-md rounded-2xl border border-[#549E06]/30 p-4 sm:p-8 shadow-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
          About Edward
        </h2>

        <div className="space-y-6 text-gray-300">
          <p className="text-base sm:text-lg">
            I am a full stack developer with 5 years of experience building and
            deploying scalable web applications. My expertise lies in the
            Laravel ecosystem, with deep knowledge of search optimization,
            geospatial data, and CI/CD automation.
          </p>

          <div>
            <h3 className="text-xl sm:text-2xl font-bold text-[#C6F486] mb-3">
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
            <h3 className="text-xl sm:text-2xl font-bold text-[#C6F486] mb-3">
              Technical Expertise
            </h3>
            <ul className="list-disc list-inside space-y-2 text-sm sm:text-base">
              <li>
                <strong className="text-[#ADB5D6]">Backend:</strong> PHP
                (Laravel), Python (Django, Flask, FastAPI)
              </li>
              <li>
                <strong className="text-[#ADB5D6]">Frontend:</strong> JavaScript
                (Alpine.js, Vue.js, React), Inertia.js, Tailwind CSS
              </li>
              <li>
                <strong className="text-[#ADB5D6]">Infrastructure:</strong>{" "}
                Docker, Nginx, GitHub Actions, VPS Management
              </li>
              <li>
                <strong className="text-[#ADB5D6]">Specialized:</strong> Vector
                Search, RAG Architecture, Geospatial Data, AI Integration
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-xl sm:text-2xl font-bold text-[#C6F486] mb-3">
              Notable Projects
            </h3>
            <div className="space-y-4">
              <div className="bg-white/5 p-4 rounded-lg border border-[#549E06]/30">
                <h4 className="text-lg sm:text-xl font-semibold text-white mb-2">
                  ActuallyFind.com
                </h4>
                <p className="text-sm sm:text-base mb-4">
                  A production vehicle marketplace featuring PostgreSQL +
                  PostGIS for geospatial queries, Typesense for sub-500ms
                  search, and Blue/Green deployment for zero-downtime updates.
                </p>
                <div className="flex flex-wrap gap-2">
                  <a
                    href="https://actuallyfind.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 sm:px-4 py-2 text-sm sm:text-base bg-[#95E913]/20 hover:bg-[#95E913]/30 border border-[#95E913]/50 text-[#C6F486] rounded-lg transition-all"
                  >
                    Website
                  </a>
                  <a
                    href="https://dealership.monatemedia.com/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 sm:px-4 py-2 text-sm sm:text-base bg-blue-500/20 hover:bg-blue-500/30 border border-blue-500/50 text-blue-300 rounded-lg transition-all"
                  >
                    Demo
                  </a>
                  <a
                    href="https://github.com/monatemedia/dealership"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 sm:px-4 py-2 text-sm sm:text-base bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 text-purple-300 rounded-lg transition-all"
                  >
                    GitHub
                  </a>
                </div>
              </div>

              <div className="bg-white/5 p-4 rounded-lg border border-[#549E06]/30">
                <h4 className="text-lg sm:text-xl font-semibold text-white mb-2">
                  Vector CV
                </h4>
                <p className="text-sm sm:text-base mb-4">
                  This AI-powered resume synthesizer you're using right now,
                  showcasing my ability to build production RAG systems with
                  hybrid selection strategies and OpenAI integration.
                </p>
                <div className="flex flex-wrap gap-2">
                  <a
                    href="https://github.com/monatemedia/vector-cv"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 sm:px-4 py-2 text-sm sm:text-base bg-purple-500/20 hover:bg-purple-500/30 border border-purple-500/50 text-purple-300 rounded-lg transition-all"
                  >
                    GitHub
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 sm:gap-4 mt-6">
            <a
              href="https://wa.me/27783245326"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-green-500/20 hover:bg-green-500/30 border border-green-500/30 text-green-300 rounded-lg transition-all"
            >
              WhatsApp
            </a>
            <a
              href="mailto:edward@monatemedia.com"
              className="px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-[#9D6777]/20 hover:bg-red-500/30 border border-[#9D6777]/30 text-red-300 rounded-lg transition-all"
            >
              Email
            </a>
            <a
              href="https://github.com/monatemedia"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-[#549E06]/20 hover:bg-purple-500/30 border border-[#549E06]/30 text-[#C6F486] rounded-lg transition-all"
            >
              GitHub
            </a>
            <a
              href="https://linkedin.com/in/edwardbaitsewe"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-[#9D6777]/20 hover:bg-blue-500/30 border border-[#9D6777]/30 text-blue-300 rounded-lg transition-all"
            >
              LinkedIn
            </a>
            <a
              href="https://monatemedia.com/portfolio"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 sm:px-6 py-2 sm:py-3 text-sm sm:text-base bg-[#542C3C]/20 hover:bg-orange-500/30 border border-[#542C3C]/30 text-orange-300 rounded-lg transition-all"
            >
              Portfolio
            </a>
          </div>

          {personalInfo && (
            <div className="mt-8 p-4 sm:p-6 bg-[#542C3C]/20 border border-[#549E06]/30 rounded-lg">
              <h3 className="text-lg sm:text-xl font-bold text-[#C6F486] mb-3">
                Contact Information
              </h3>
              <div className="space-y-2 text-sm sm:text-base">
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
