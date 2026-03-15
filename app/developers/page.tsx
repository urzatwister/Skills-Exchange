"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import SecurityBadge from "../components/SecurityBadge";

const API_BASE = process.env.NEXT_PUBLIC_NEXUS_API_URL || "http://localhost:8000";

interface SkillStat {
  skill_id: string;
  name: string;
  risk_score: number | null;
  price_per_use: number | null;
  total_uses: number;
  developer_revenue: number;
}

interface DeveloperStats {
  author: string;
  skill_count: number;
  total_uses: number;
  unique_agents: number;
  total_revenue: number;
  skills: SkillStat[];
}

function DeveloperPortalContent() {
  const searchParams = useSearchParams();
  const author = searchParams.get("author") || "";
  const [stats, setStats] = useState<DeveloperStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState(author);

  const load = async (a: string) => {
    if (!a.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/developers/${encodeURIComponent(a.trim())}/stats`);
      if (res.status === 404) { setError(`No skills found for author "${a}"`); setStats(null); }
      else { setStats(await res.json()); }
    } catch {
      setError("Could not reach the Nexus API. Is it running?");
    } finally { setLoading(false); }
  };

  useEffect(() => { if (author) load(author); }, []); // eslint-disable-line

  return (
    <div className="min-h-screen p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <Link href="/dashboard" className="text-2xl font-bold tracking-tight">
          <span className="text-cyan-400">Nexus</span> Exchange
        </Link>
        <span className="text-sm text-white/30">Developer Portal</span>
      </div>

      <h1 className="text-3xl font-bold mb-2">Developer Earnings</h1>
      <p className="text-white/40 mb-8">
        Track usage, unique agents, and revenue across all your published skills.
      </p>

      {/* Author search */}
      <form
        onSubmit={(e) => { e.preventDefault(); load(query); }}
        className="flex gap-3 mb-10"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter author name..."
          className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl
                     focus:outline-none focus:border-cyan-500/50 focus:ring-2 focus:ring-cyan-500/20"
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-white/10
                     disabled:text-white/30 rounded-xl font-medium transition-colors"
        >
          {loading ? "Loading..." : "View Stats"}
        </button>
      </form>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 mb-8">
          {error}
        </div>
      )}

      {stats && (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
            {[
              { label: "Skills Published", value: stats.skill_count, unit: "" },
              { label: "Total Uses", value: stats.total_uses, unit: "" },
              { label: "Unique Agents", value: stats.unique_agents, unit: "" },
              { label: "Total Earnings", value: `$${stats.total_revenue.toFixed(4)}`, unit: "", highlight: true },
            ].map(({ label, value, highlight }) => (
              <div key={label} className="p-5 bg-white/5 border border-white/10 rounded-2xl text-center">
                <div className={`text-2xl font-bold mb-1 ${highlight ? "text-cyan-400" : ""}`}>
                  {value}
                </div>
                <div className="text-xs text-white/40">{label}</div>
              </div>
            ))}
          </div>

          {/* Revenue split note */}
          <div className="mb-8 p-4 bg-white/5 border border-white/10 rounded-xl text-sm text-white/40 flex items-center gap-3">
            <span className="text-cyan-400 font-mono text-lg">80/20</span>
            <span>
              Revenue split: <strong className="text-white/70">80%</strong> to you (developer) ·{" "}
              <strong className="text-white/70">20%</strong> to Nexus platform infrastructure.
              Earnings shown are your <em>developer share</em> after split.
            </span>
          </div>

          {/* Per-skill breakdown */}
          <h2 className="text-lg font-semibold mb-4">Skills by {stats.author}</h2>
          <div className="space-y-3">
            {stats.skills.map((skill) => (
              <Link
                key={skill.skill_id}
                href={`/dashboard/${skill.skill_id}`}
                className="flex items-center justify-between p-5 bg-white/5 border border-white/10
                           rounded-2xl hover:border-cyan-500/30 hover:bg-white/[0.07] transition-all group"
              >
                <div className="flex items-center gap-4">
                  <div>
                    <div className="font-semibold group-hover:text-cyan-400 transition-colors">
                      {skill.name}
                    </div>
                    <div className="text-xs text-white/30 font-mono mt-0.5">{skill.skill_id}</div>
                  </div>
                  <SecurityBadge riskScore={skill.risk_score} size="sm" />
                </div>

                <div className="flex items-center gap-8 text-sm text-right">
                  <div>
                    <div className="text-white/30 text-xs mb-0.5">Uses</div>
                    <div className="font-mono font-semibold">{skill.total_uses}</div>
                  </div>
                  <div>
                    <div className="text-white/30 text-xs mb-0.5">Price/use</div>
                    <div className="font-mono text-cyan-400">
                      {skill.price_per_use ? `$${skill.price_per_use}` : "FREE"}
                    </div>
                  </div>
                  <div>
                    <div className="text-white/30 text-xs mb-0.5">Your earnings</div>
                    <div className="font-mono font-semibold text-cyan-400">
                      ${skill.developer_revenue.toFixed(4)}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {stats.skills.length === 0 && (
            <div className="text-center py-12 text-white/30">No skills found for this author.</div>
          )}
        </>
      )}

      {!stats && !loading && !error && (
        <div className="text-center py-20 text-white/20">
          <div className="text-4xl mb-4 font-mono">$$$</div>
          <p>Enter your author name to view earnings across all your published skills.</p>
        </div>
      )}
    </div>
  );
}

export default function DeveloperPortal() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-white/30">Loading...</div>}>
      <DeveloperPortalContent />
    </Suspense>
  );
}
