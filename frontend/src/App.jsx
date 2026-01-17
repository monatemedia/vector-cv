import { useState, useEffect } from "react";
import {
  User,
  Sparkles,
  Info,
  Brain,
  Award,
  Target,
  FileText,
} from "lucide-react";
import About from "./components/About";
import RagAI from "./components/RagAI";
import Skills from "./components/Skills";
import Generate from "./components/Generate";
import Results from "./components/Results";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8010";

function App() {
  const [activeTab, setActiveTab] = useState("about");
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
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/applications`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate CV");
      }

      const data = await response.json();
      setResult(data);
      setActiveTab("results");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "about", label: "About", icon: Info },
    { id: "rag-ai", label: "RAG AI", icon: Brain },
    { id: "skills", label: "Skills", icon: Award },
    { id: "generate", label: "Generate", icon: Target },
    { id: "results", label: "Results", icon: FileText, disabled: !result },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-96 h-96 bg-purple-500/20 rounded-full blur-3xl -top-48 -left-48 animate-pulse" />
        <div
          className="absolute w-96 h-96 bg-blue-500/20 rounded-full blur-3xl -bottom-48 -right-48 animate-pulse"
          style={{ animationDelay: "1s" }}
        />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                  <Sparkles className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Vector CV</h1>
                  <p className="text-sm text-purple-300">
                    AI-Powered Resume Synthesizer
                  </p>
                </div>
              </div>
              {personalInfo && (
                <div className="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-lg border border-white/10">
                  <User className="w-5 h-5 text-purple-400" />
                  <span className="text-white font-medium">
                    {personalInfo.name}
                  </span>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-6 py-12">
          {/* Tabs */}
          <div className="flex flex-wrap gap-2 mb-8 bg-white/5 p-2 rounded-xl w-fit mx-auto border border-white/10">
            {tabs.map(({ id, label, icon: Icon, disabled }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                disabled={disabled}
                className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
                  activeTab === id
                    ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg"
                    : "text-gray-400 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === "about" && <About personalInfo={personalInfo} />}
          {activeTab === "rag-ai" && <RagAI />}
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
            />
          )}
          {activeTab === "results" && result && (
            <Results result={result} apiUrl={API_URL} />
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-black/20 backdrop-blur-xl mt-20">
          <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <p className="text-gray-400 text-sm">
                Powered by OpenAI GPT-4 • Built by Edward Baitsewe
              </p>
              <div className="flex gap-4">
                <a
                  href="https://github.com/monatemedia"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  GitHub
                </a>
                <a
                  href="https://linkedin.com/in/edwardbaitsewe"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  LinkedIn
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
