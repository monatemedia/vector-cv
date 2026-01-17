import {
  CheckCircle,
  AlertCircle,
  Target,
  FileText,
  Briefcase,
} from "lucide-react";
import { marked } from "marked";
import DownloadDropdown from "./DownloadDropdown";

export default function Results({ result, apiUrl }) {
  const renderMarkdownAsHTML = (markdown) => {
    return { __html: marked.parse(markdown) };
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Success Message */}
      <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 flex items-start gap-4">
        <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
        <div>
          <h3 className="text-xl font-bold text-white mb-1">
            Application Generated Successfully!
          </h3>
          <p className="text-green-300">
            Your tailored CV and cover letter for{" "}
            <span className="font-semibold">{result.job_title}</span> at{" "}
            <span className="font-semibold">{result.company_name}</span> are
            ready.
          </p>
        </div>
      </div>

      {/* Skills Gap Analysis */}
      {result.skills_gap_report && (
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <Target className="w-6 h-6 text-purple-400" />
            Skills Gap Analysis
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="text-lg font-semibold text-green-400 mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Matching Skills
              </h4>
              <div className="space-y-2">
                {result.skills_gap_report.matching_skills?.map((skill, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-green-300"
                  >
                    <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                    {skill}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-amber-400 mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Skills to Develop
              </h4>
              <div className="space-y-2">
                {result.skills_gap_report.missing_skills?.map((skill, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-amber-300"
                  >
                    <div className="w-1.5 h-1.5 bg-amber-400 rounded-full"></div>
                    {skill}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {result.skills_gap_report.recommendations && (
            <div>
              <h4 className="text-lg font-semibold text-blue-400 mb-3">
                Recommendations
              </h4>
              <div className="space-y-2">
                {result.skills_gap_report.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-start gap-3 text-blue-300">
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span>{typeof rec === "string" ? rec : rec.details}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* CV */}
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white flex items-center gap-3">
            <FileText className="w-6 h-6 text-purple-400" />
            Tailored CV
          </h3>
          <DownloadDropdown
            type="cv"
            result={result}
            apiUrl={apiUrl}
            buttonColor="purple"
          />
        </div>
        <div className="bg-black/30 rounded-lg p-6 border border-white/5 prose prose-invert max-w-none">
          <div
            className="markdown-content"
            dangerouslySetInnerHTML={renderMarkdownAsHTML(result.generated_cv)}
          />
        </div>
      </div>

      {/* Cover Letter */}
      <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-8">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white flex items-center gap-3">
            <Briefcase className="w-6 h-6 text-blue-400" />
            Cover Letter
          </h3>
          <DownloadDropdown
            type="cover-letter"
            result={result}
            apiUrl={apiUrl}
            buttonColor="blue"
          />
        </div>
        <div className="bg-black/30 rounded-lg p-6 border border-white/5 prose prose-invert max-w-none">
          <div
            className="markdown-content"
            dangerouslySetInnerHTML={renderMarkdownAsHTML(
              result.generated_cover_letter
            )}
          />
        </div>
      </div>
    </div>
  );
}
