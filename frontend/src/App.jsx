import { useState, useEffect } from "react";
import {
  User,
  Sparkles,
  Info,
  Brain,
  Award,
  Target,
  FileText,
  Menu,
  MessageCircle,
  Mail,
  Github,
  Linkedin,
  Briefcase,
} from "lucide-react";
import ParticleBackground from "./components/ParticleBackground";
import About from "./components/About";
import RagAI from "./components/RagAI";
import Skills from "./components/Skills";
import Generate from "./components/Generate";
import Results from "./components/Results";

// If we are in production (Docker/Nginx), use relative paths.
// If in dev mode, use the environment variable or localhost.
const API_URL = import.meta.env.PROD
  ? ""
  : import.meta.env.VITE_API_URL || "http://localhost:8010";

function App() {
  const [activeTab, setActiveTab] = useState("generate");
  const [showMenu, setShowMenu] = useState(false);
  const [usage, setUsage] = useState({ used: 0, remaining: 3, limit: 3 });
  const [personalInfo, setPersonalInfo] = useState(null);
  const [experienceBlocks, setExperienceBlocks] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    company_name: "",
    job_title: "",
    job_url: "",
    raw_spec: "",
  });

  useEffect(() => {
    fetchPersonalInfo();
    fetchExperienceBlocks();
    fetchUsage();
  }, []);

  const fetchPersonalInfo = async () => {
    try {
      const response = await fetch(`${API_URL}/api/personal-info`);
      if (response.ok) {
        const data = await response.json();
        setPersonalInfo(data);
      }
    } catch (err) {
      console.error("Failed to fetch personal info:", err);
    }
  };

  const fetchExperienceBlocks = async () => {
    try {
      const response = await fetch(`${API_URL}/api/experience-blocks`);
      if (response.ok) {
        const data = await response.json();
        setExperienceBlocks(data);
      }
    } catch (err) {
      console.error("Failed to fetch experience blocks:", err);
    }
  };

  const handleGenerate = async () => {
    if (!formData.company_name || !formData.job_title || !formData.raw_spec) {
      setError("Please fill in all required fields");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/applications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        if (response.status === 429) {
          // Friendly message for the 3-per-day limit
          throw new Error(
            "Daily limit reached: You can generate up to 3 CVs per day to help manage AI costs. Please try again tomorrow!",
          );
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate CV");
      }

      const data = await response.json();
      setResult(data);

      // Refresh usage stats AFTER successful generation
      await fetchUsage();

      setActiveTab("results");
    } catch (err) {
      setError(err.message);
      // Refresh usage stats even on error just to be safe/synced
      fetchUsage();
    } finally {
      setLoading(false);
    }
  };

  const fetchUsage = async () => {
    try {
      const response = await fetch(`${API_URL}/api/usage-stats`);
      if (response.ok) {
        const data = await response.json();
        setUsage(data);
      }
    } catch (err) {
      console.error("Failed to fetch usage stats:", err);
    }
  };

  const tabs = [
    { id: "about", label: "About", icon: Info },
    { id: "skills", label: "Skills", icon: Award },
    { id: "generate", label: "Generate", icon: Target },
    { id: "results", label: "Results", icon: FileText, disabled: !result },
    { id: "rag-ai", label: "RAG AI", icon: Brain },
  ];

  return (
    <div className="min-h-screen bg-black overflow-x-hidden">
      {/* Particle Background */}
      <ParticleBackground />

      <div className="relative z-10 pointer-events-none">
        {/* Header */}
        <header className="border-b border-[#549E06]/30 bg-black/40 backdrop-blur-md pointer-events-auto">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              {/* Logo and title - clickable to navigate to Generate tab */}
              <div
                className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
                onClick={() => setActiveTab("generate")}
              >
                <div className="w-12 h-12 bg-[#95E913] rounded-xl flex items-center justify-center shadow-lg shadow-[#95E913]/30">
                  <Sparkles className="w-7 h-7 text-black" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Vector CV</h1>
                  <p className="text-sm text-[#C6F486]">
                    Edward's AI-Powered Resume
                  </p>
                </div>
              </div>

              {/* User name - clickable to go to About page */}
              {personalInfo && (
                <div
                  className="flex items-center gap-3 bg-[#542C3C]/50 px-4 py-2 rounded-lg border border-[#9D6777]/30 backdrop-blur-sm cursor-pointer hover:opacity-80 transition-opacity"
                  onClick={() => setActiveTab("about")}
                >
                  <User className="w-5 h-5 text-[#ADB5D6]" />
                  <span className="text-white font-medium">
                    {personalInfo.name}
                  </span>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-12 pointer-events-auto">
          {/* Tabs */}
          <div className="mb-8">
            {/* Desktop: Full tabs */}
            <div className="hidden lg:flex flex-wrap gap-2 bg-black/50 p-2 rounded-xl w-fit mx-auto border border-[#549E06]/30 backdrop-blur-md">
              {tabs.map(({ id, label, icon: Icon, disabled }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  disabled={disabled}
                  className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                    activeTab === id
                      ? "bg-[#95E913] text-black shadow-lg shadow-[#95E913]/30"
                      : "text-[#C6F486] hover:text-white hover:bg-[#549E06]/20 disabled:opacity-50 disabled:cursor-not-allowed"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {label}
                </button>
              ))}
            </div>

            {/* Mobile: Hamburger menu */}
            <div className="lg:hidden relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="mx-auto flex items-center gap-2 px-6 py-3 rounded-lg font-medium bg-[#95E913] text-black shadow-lg shadow-[#95E913]/30"
              >
                <Menu className="w-5 h-5" />
                Menu
              </button>

              {showMenu && (
                <div className="absolute left-1/2 transform -translate-x-1/2 mt-2 bg-black/95 backdrop-blur-md border border-[#549E06]/30 rounded-xl overflow-hidden shadow-xl z-50 min-w-[200px]">
                  {tabs.map(({ id, label, icon: Icon, disabled }) => (
                    <button
                      key={id}
                      onClick={() => {
                        setActiveTab(id);
                        setShowMenu(false);
                      }}
                      disabled={disabled}
                      className={`w-full px-6 py-3 font-medium transition-all flex items-center gap-2 border-b border-[#549E06]/20 last:border-b-0 ${
                        activeTab === id
                          ? "bg-[#95E913] text-black"
                          : "text-[#C6F486] hover:text-white hover:bg-[#549E06]/20 disabled:opacity-50 disabled:cursor-not-allowed"
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      {label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === "about" && <About personalInfo={personalInfo} />}
          {activeTab === "skills" && (
            <Skills experienceBlocks={experienceBlocks} />
          )}
          {activeTab === "generate" && (
            <Generate
              formData={formData}
              setFormData={setFormData}
              loading={loading}
              error={error}
              onGenerate={handleGenerate}
              usage={usage}
            />
          )}
          {activeTab === "results" && result && (
            <Results result={result} apiUrl={API_URL} />
          )}
          {activeTab === "rag-ai" && <RagAI />}
        </main>

        {/* Footer */}
        <footer className="border-t border-[#549E06]/30 bg-black/40 backdrop-blur-md mt-20 pointer-events-auto">
          <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              {/* Text content - left side on desktop, stacks on mobile */}
              <div className="text-center sm:text-left">
                <p className="text-[#ADB5D6] text-sm">
                  Powered by OpenAI GPT-4{" "}
                  <span className="hidden sm:inline">•</span>
                  <span className="block sm:inline sm:ml-1">
                    Built by Edward Baitsewe
                  </span>
                </p>
              </div>

              {/* Icon links - right side on desktop */}
              <div className="flex gap-4 items-center">
                <a
                  href="https://wa.me/27783245326"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#C6F486] hover:text-[#95E913] transition-colors"
                  aria-label="WhatsApp"
                >
                  <MessageCircle className="w-5 h-5" />
                </a>
                <a
                  href="mailto:edward@monatemedia.com"
                  className="text-[#C6F486] hover:text-[#95E913] transition-colors"
                  aria-label="Email"
                >
                  <Mail className="w-5 h-5" />
                </a>
                <a
                  href="https://github.com/monatemedia"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#C6F486] hover:text-[#95E913] transition-colors"
                  aria-label="GitHub"
                >
                  <Github className="w-5 h-5" />
                </a>
                <a
                  href="https://linkedin.com/in/edwardbaitsewe"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#C6F486] hover:text-[#95E913] transition-colors"
                  aria-label="LinkedIn"
                >
                  <Linkedin className="w-5 h-5" />
                </a>
                <a
                  href="https://www.monatemedia.com/portfolio/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#C6F486] hover:text-[#95E913] transition-colors"
                  aria-label="Portfolio"
                >
                  <Briefcase className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
