// Button style mappings - consistent across the app
export const BUTTON_STYLES = {
  // Known buttons
  Website: "bg-[#95E913]/20 hover:bg-[#95E913]/30 border-[#95E913]/50 text-[#C6F486]",
  Demo: "bg-blue-500/20 hover:bg-blue-500/30 border-blue-500/50 text-blue-300",
  GitHub: "bg-purple-500/20 hover:bg-purple-500/30 border-purple-500/50 text-purple-300",
  Admin: "bg-orange-500/20 hover:bg-orange-500/30 border-orange-500/50 text-orange-300",
  Docs: "bg-cyan-500/20 hover:bg-cyan-500/30 border-cyan-500/50 text-cyan-300",
  LinkedIn: "bg-[#9D6777]/20 hover:bg-blue-500/30 border-[#9D6777]/30 text-blue-300",
  WhatsApp: "bg-green-500/20 hover:bg-green-500/30 border-green-500/30 text-green-300",
  Email: "bg-[#9D6777]/20 hover:bg-red-500/30 border-[#9D6777]/30 text-red-300",
  Portfolio: "bg-[#542C3C]/20 hover:bg-orange-500/30 border-[#542C3C]/30 text-orange-300",
  Live: "bg-[#95E913]/20 hover:bg-[#95E913]/30 border-[#95E913]/50 text-[#C6F486]",
  Production: "bg-[#95E913]/20 hover:bg-[#95E913]/30 border-[#95E913]/50 text-[#C6F486]",
  
  // Generic fallback styles (for unknown button labels)
  fallback: [
    "bg-[#549E06]/20 hover:bg-[#549E06]/30 border-[#549E06]/30 text-[#C6F486]",
    "bg-[#542C3C]/20 hover:bg-[#542C3C]/30 border-[#542C3C]/30 text-[#9D6777]",
    "bg-indigo-500/20 hover:bg-indigo-500/30 border-indigo-500/30 text-indigo-300",
    "bg-pink-500/20 hover:bg-pink-500/30 border-pink-500/30 text-pink-300",
    "bg-yellow-500/20 hover:bg-yellow-500/30 border-yellow-500/30 text-yellow-300",
    "bg-teal-500/20 hover:bg-teal-500/30 border-teal-500/30 text-teal-300",
    "bg-red-500/20 hover:bg-red-500/30 border-red-500/30 text-red-300",
    "bg-emerald-500/20 hover:bg-emerald-500/30 border-emerald-500/30 text-emerald-300",
    "bg-violet-500/20 hover:bg-violet-500/30 border-violet-500/30 text-violet-300",
    "bg-amber-500/20 hover:bg-amber-500/30 border-amber-500/30 text-amber-300",
  ]
};

// Get style for a button label
export const getButtonStyle = (label) => {
  if (BUTTON_STYLES[label]) {
    return BUTTON_STYLES[label];
  }
  
  // Use a consistent fallback based on label hash
  const hash = label.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const index = hash % BUTTON_STYLES.fallback.length;
  return BUTTON_STYLES.fallback[index];
};