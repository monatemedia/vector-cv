import {
  CheckCircle,
  AlertCircle,
  Target,
  FileText,
  Briefcase,
} from "lucide-react";
import ContentRenderer from "./ContentRenderer";
import StructuredCVRenderer from "./StructuredCVRenderer";
import DownloadDropdown from "./DownloadDropdown";

// Safely extract text from a recommendation item.
// GPT returns these in inconsistent shapes across runs. Observed keys:
//   plain string
//   { skill: "Symfony", action: "Consider a short course..." }  ← current shape
//   { details: "..." }
//   { recommendation: "..." }
//   { description: "..." }
// When skill + action are both present, render as a React node with the
// skill name highlighted so it reads naturally. Otherwise fall back.
function getRecommendationText(rec) {
  if (typeof rec === "string") return rec;
  if (typeof rec === "object" && rec !== null) {
    // Best case: skill label + action sentence — format as readable line
    if (rec.skill && rec.action) {
      return (
        <>
          <strong className="text-[#C6F486]">{rec.skill}:</strong> {rec.action}
        </>
      );
    }
    // Single-value fallbacks in priority order
    return (
      rec.action ||
      rec.details ||
      rec.recommendation ||
      rec.description ||
      rec.text ||
      JSON.stringify(rec)
    );
  }
  return String(rec);
}

export default function Results({ result, apiUrl }) {
  // Check if CV is structured JSON or markdown
  const isStructuredCV =
    typeof result.generated_cv === "object" &&
    result.generated_cv !== null &&
    !result.generated_cv.error;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Success Message */}
      <div className="bg-[#549E06]/20 border border-[#95E913]/50 rounded-xl p-4 sm:p-6 flex items-start gap-4">
        <CheckCircle className="w-6 h-6 text-[#95E913] shrink-0 mt-1" />
        <div>
          <h3 className="text-lg sm:text-xl font-bold text-white mb-1">
            Application Generated Successfully!
          </h3>
          <p className="text-sm sm:text-base text-[#C6F486]">
            Your tailored CV and cover letter for{" "}
            <span className="font-semibold">{result.job_title}</span> at{" "}
            <span className="font-semibold">{result.company_name}</span> are
            ready.
          </p>
        </div>
      </div>

      {/* Skills Gap Analysis */}
      {result.skills_gap_report && (
        <div className="bg-black/60 backdrop-blur-md rounded-2xl border border-[#549E06]/30 p-4 sm:p-8">
          <h3 className="text-xl sm:text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <Target className="w-6 h-6 text-[#95E913]" />
            Skills Gap Analysis
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h4 className="text-base sm:text-lg font-semibold text-[#95E913] mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Matching Skills
              </h4>
              <div className="space-y-2">
                {result.skills_gap_report.matching_skills?.map((skill, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-sm sm:text-base text-[#C6F486]"
                  >
                    <div className="w-1.5 h-1.5 bg-[#95E913] rounded-full shrink-0"></div>
                    <span className="break-words">{skill}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-base sm:text-lg font-semibold text-amber-400 mb-3 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                Skills to Develop
              </h4>
              <div className="space-y-2">
                {result.skills_gap_report.missing_skills?.map((skill, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-2 text-sm sm:text-base text-amber-300"
                  >
                    <div className="w-1.5 h-1.5 bg-amber-400 rounded-full shrink-0"></div>
                    <span className="break-words">{skill}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {result.skills_gap_report.recommendations && (
            <div>
              <h4 className="text-base sm:text-lg font-semibold text-[#ADB5D6] mb-3">
                Recommendations
              </h4>
              <div className="space-y-2">
                {result.skills_gap_report.recommendations.map((rec, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 text-sm sm:text-base text-[#ADB5D6]"
                  >
                    <div className="w-1.5 h-1.5 bg-[#ADB5D6] rounded-full mt-2 shrink-0"></div>
                    <span className="break-words">
                      {getRecommendationText(rec)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* CV */}
      <div className="bg-black/60 backdrop-blur-md rounded-2xl border border-[#549E06]/30 p-4 sm:p-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <h3 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-3">
            <FileText className="w-6 h-6 text-[#95E913]" />
            Tailored CV
          </h3>
          <DownloadDropdown
            type="cv"
            result={result}
            apiUrl={apiUrl}
            buttonColor="purple"
          />
        </div>
        <div className="bg-white/5 border border-[#549E06]/30 rounded-lg p-4 sm:p-6">
          <div className="text-sm sm:text-base text-gray-300">
            {isStructuredCV ? (
              <StructuredCVRenderer cvData={result.generated_cv} />
            ) : (
              <ContentRenderer content={result.generated_cv} />
            )}
          </div>
        </div>
      </div>

      {/* Cover Letter */}
      <div className="bg-black/60 backdrop-blur-md rounded-2xl border border-[#549E06]/30 p-4 sm:p-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <h3 className="text-xl sm:text-2xl font-bold text-white flex items-center gap-3">
            <Briefcase className="w-6 h-6 text-[#ADB5D6]" />
            Cover Letter
          </h3>
          <DownloadDropdown
            type="cover-letter"
            result={result}
            apiUrl={apiUrl}
            buttonColor="blue"
          />
        </div>
        <div className="bg-white/5 border border-[#549E06]/30 rounded-lg p-4 sm:p-6">
          <div className="text-sm sm:text-base text-gray-300">
            <ContentRenderer content={result.generated_cover_letter} />
          </div>
        </div>
      </div>
    </div>
  );
}
