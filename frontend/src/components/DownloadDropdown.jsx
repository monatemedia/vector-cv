import { useState } from "react";
import { Download, ChevronDown, FileText, FileCode } from "lucide-react";

export default function DownloadDropdown({
  type,
  result,
  apiUrl,
  buttonColor = "purple",
}) {
  const [isOpen, setIsOpen] = useState(false);

  const getFilename = (format) => {
    const docType = type === "cv" ? "CV" : "Cover Letter";
    return `${docType} - ${result.company_name} - ${result.job_title} - Baitsewe, Edward.${format}`;
  };

  const downloadMarkdown = () => {
    const content =
      type === "cv" ? result.generated_cv : result.generated_cover_letter;
    const blob = new Blob([content], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = getFilename("md");
    a.click();
    URL.revokeObjectURL(url);
    setIsOpen(false);
  };

  const downloadWord = async () => {
    try {
      const endpoint = type === "cv" ? "cv" : "cover-letter";
      const response = await fetch(
        `${apiUrl}/api/download/${endpoint}/${result.id}`,
      );

      if (!response.ok) throw new Error("Failed to download");

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = getFilename("docx");
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download error:", error);
      alert("Failed to download Word document. Please try again.");
    }
    setIsOpen(false);
  };

  const colorClasses = {
    purple: {
      button:
        "bg-[#549E06]/20 hover:bg-purple-500/30 border-[#549E06]/30 text-[#C6F486]",
      dropdown: "bg-[#542C3C]/20 border-[#549E06]/30",
    },
    blue: {
      button:
        "bg-[#9D6777]/20 hover:bg-blue-500/30 border-[#9D6777]/30 text-blue-300",
      dropdown: "bg-blue-500/10 border-[#9D6777]/30",
    },
  };

  const colors = colorClasses[buttonColor];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`px-4 py-2 ${colors.button} border rounded-lg transition-all flex items-center gap-2`}
      >
        <Download className="w-4 h-4" />
        Download
        <ChevronDown
          className={`w-4 h-4 transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div
            className={`absolute right-0 mt-2 w-56 ${colors.dropdown} border rounded-lg shadow-xl z-20 overflow-hidden`}
          >
            <button
              onClick={downloadWord}
              className="w-full px-4 py-3 text-left text-white hover:bg-white/10 transition-colors flex items-center gap-3"
            >
              <FileText className="w-4 h-4" />
              <div>
                <div className="font-medium">Word Document</div>
                <div className="text-xs text-gray-400">.docx format</div>
              </div>
            </button>

            <div className="border-t border-white/10" />

            <button
              onClick={downloadMarkdown}
              className="w-full px-4 py-3 text-left text-white hover:bg-white/10 transition-colors flex items-center gap-3"
            >
              <FileCode className="w-4 h-4" />
              <div>
                <div className="font-medium">Markdown</div>
                <div className="text-xs text-gray-400">.md format</div>
              </div>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
