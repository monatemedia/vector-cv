import { Sparkles, XCircle, Loader } from "lucide-react";

export default function Generate({
  formData,
  setFormData,
  loading,
  error,
  onGenerate,
}) {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h2 className="text-5xl font-bold text-white mb-4">
          Generate AI-tailored CV
        </h2>
        <p className="text-xl text-purple-200 max-w-2xl mx-auto">
          Paste any job description and get an AI-tailored CV and cover letter
          for Edward in seconds
        </p>
      </div>

      <div className="bg-black/60 backdrop-blur-md rounded-2xl border border-[#549E06]/30 p-8 shadow-2xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-sm font-medium text-[#C6F486] mb-2">
              Company Name *
            </label>
            <input
              type="text"
              value={formData.company_name}
              onChange={(e) =>
                setFormData({ ...formData, company_name: e.target.value })
              }
              className="w-full px-4 py-3 bg-white/5 border border-[#549E06]/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#95E913]"
              placeholder="e.g., LekkeSlaap"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#C6F486] mb-2">
              Job Title *
            </label>
            <input
              type="text"
              value={formData.job_title}
              onChange={(e) =>
                setFormData({ ...formData, job_title: e.target.value })
              }
              className="w-full px-4 py-3 bg-white/5 border border-[#549E06]/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#95E913]"
              placeholder="e.g., Full Stack Developer"
            />
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-[#C6F486] mb-2">
            Job URL (Optional)
          </label>
          <input
            type="url"
            value={formData.job_url}
            onChange={(e) =>
              setFormData({ ...formData, job_url: e.target.value })
            }
            className="w-full px-4 py-3 bg-white/5 border border-[#549E06]/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#95E913]"
            placeholder="https://..."
          />
        </div>

        <div className="mb-8">
          <label className="block text-sm font-medium text-[#C6F486] mb-2">
            Job Description *
          </label>
          <textarea
            value={formData.raw_spec}
            onChange={(e) =>
              setFormData({ ...formData, raw_spec: e.target.value })
            }
            rows={16}
            className="w-full px-4 py-3 bg-white/5 border border-[#549E06]/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#95E913] font-mono text-sm"
            placeholder="Paste the complete job description here..."
          />
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
            <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-400 font-medium">Error</p>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          </div>
        )}

        <button
          onClick={onGenerate}
          disabled={loading}
          className="w-full py-4 bg-[#95E913] text-white rounded-lg font-semibold hover:bg-[#549E06] transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Generating Your Perfect Application...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Generate CV & Cover Letter
            </>
          )}
        </button>

        <p className="text-center text-sm text-gray-400 mt-4">
          This usually takes 30-60 seconds
        </p>
      </div>
    </div>
  );
}
