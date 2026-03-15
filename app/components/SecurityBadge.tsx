interface SecurityBadgeProps {
  riskScore: number | null | undefined;
  size?: "sm" | "md";
}

export default function SecurityBadge({ riskScore, size = "md" }: SecurityBadgeProps) {
  if (riskScore == null) {
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/10 text-white/40 ${size === "sm" ? "text-xs" : "text-sm"}`}>
        N/A
      </span>
    );
  }

  const label = riskScore < 30 ? "LOW RISK" : riskScore < 60 ? "MEDIUM" : "HIGH RISK";
  const colors =
    riskScore < 30
      ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
      : riskScore < 60
        ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
        : "bg-red-500/20 text-red-400 border-red-500/30";

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border ${colors} ${size === "sm" ? "text-xs" : "text-sm"} font-medium`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${riskScore < 30 ? "bg-emerald-400" : riskScore < 60 ? "bg-amber-400" : "bg-red-400"}`} />
      {label}
    </span>
  );
}
