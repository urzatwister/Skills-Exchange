import Link from "next/link";
import SecurityBadge from "./SecurityBadge";

interface SkillCardProps {
  skill_id: string;
  name: string;
  description: string;
  confidence?: number;
  risk_score?: number | null;
  price_per_use?: number | null;
  author: string;
  tags?: string[];
}

export default function SkillCard({
  skill_id,
  name,
  description,
  confidence,
  risk_score,
  price_per_use,
  author,
  tags = [],
}: SkillCardProps) {
  return (
    <Link
      href={`/dashboard/${skill_id}`}
      className="block p-6 bg-white/5 border border-white/10 rounded-2xl hover:border-cyan-500/30
                 hover:bg-white/[0.07] transition-all group"
    >
      <div className="flex items-start justify-between gap-4 mb-3">
        <h3 className="text-lg font-semibold group-hover:text-cyan-400 transition-colors">
          {name}
        </h3>
        <SecurityBadge riskScore={risk_score} size="sm" />
      </div>

      <p className="text-white/50 text-sm mb-4 line-clamp-2">{description}</p>

      {confidence != null && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-white/40">Confidence</span>
            <span className="text-cyan-400 font-mono">{Math.round(confidence * 100)}%</span>
          </div>
          <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-500 rounded-full transition-all"
              style={{ width: `${Math.round(confidence * 100)}%` }}
            />
          </div>
        </div>
      )}

      <div className="flex items-center justify-between">
        <div className="flex flex-wrap gap-1.5">
          {tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 bg-white/5 border border-white/10 rounded-md text-xs text-white/40"
            >
              {tag}
            </span>
          ))}
        </div>
        <div className="text-right text-xs">
          <div className="text-white/30">{author}</div>
          <div className="text-cyan-400 font-mono">
            {price_per_use ? `$${price_per_use}/use` : "FREE"}
          </div>
        </div>
      </div>
    </Link>
  );
}
