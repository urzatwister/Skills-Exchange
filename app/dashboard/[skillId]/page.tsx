"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import SecurityBadge from "../../components/SecurityBadge";

const API_BASE = process.env.NEXT_PUBLIC_NEXUS_API_URL || "http://localhost:8000";

interface SkillDetail {
  skill_id: string;
  name: string;
  version: string;
  description: string;
  author: string;
  tags: string[];
  skill_md_content: string;
  permissions: Record<string, string>;
  price_per_use: number | null;
  license_fee: number | null;
  risk_score: number | null;
  usage_stats: {
    total_uses: number;
    unique_agents: number;
    total_revenue: number;
  };
}

export default function SkillDetailPage({ params }: { params: Promise<{ skillId: string }> }) {
  const { skillId } = use(params);
  const [skill, setSkill] = useState<SkillDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/skills/${skillId}`)
      .then((r) => r.json())
      .then(setSkill)
      .catch(() => setSkill(null))
      .finally(() => setLoading(false));
  }, [skillId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-white/30">
        <div className="animate-pulse">Loading skill...</div>
      </div>
    );
  }

  if (!skill) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <div className="text-white/40">Skill not found</div>
        <Link href="/dashboard" className="text-cyan-400 hover:underline">
          Back to dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 max-w-4xl mx-auto">
      <Link href="/dashboard" className="text-cyan-400 hover:underline text-sm mb-6 inline-block">
        &larr; Back to dashboard
      </Link>

      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-1">{skill.name}</h1>
          <p className="text-white/40 font-mono text-sm">
            {skill.skill_id} &middot; v{skill.version} &middot; by{" "}
            <Link
              href={`/developers?author=${encodeURIComponent(skill.author)}`}
              className="text-cyan-400/70 hover:text-cyan-400 hover:underline transition-colors"
            >
              {skill.author}
            </Link>
          </p>
        </div>
        <SecurityBadge riskScore={skill.risk_score} />
      </div>

      <p className="text-white/60 mb-8">{skill.description}</p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="p-4 bg-white/5 border border-white/10 rounded-xl text-center">
          <div className="text-2xl font-bold text-cyan-400">{skill.usage_stats.total_uses}</div>
          <div className="text-xs text-white/40 mt-1">Total Uses</div>
        </div>
        <div className="p-4 bg-white/5 border border-white/10 rounded-xl text-center">
          <div className="text-2xl font-bold text-cyan-400">{skill.usage_stats.unique_agents}</div>
          <div className="text-xs text-white/40 mt-1">Unique Agents</div>
        </div>
        <div className="p-4 bg-white/5 border border-white/10 rounded-xl text-center">
          <div className="text-2xl font-bold text-cyan-400">
            ${skill.usage_stats.total_revenue.toFixed(2)}
          </div>
          <div className="text-xs text-white/40 mt-1">Revenue</div>
        </div>
      </div>

      {/* Permissions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Permission Manifest</h2>
        <div className="flex gap-3 flex-wrap">
          {Object.entries(skill.permissions).map(([scope, level]) => (
            <div
              key={scope}
              className="px-3 py-2 bg-white/5 border border-white/10 rounded-lg"
            >
              <div className="text-xs text-white/40 uppercase">{scope}</div>
              <div className="font-mono text-sm">{level}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Pricing */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Pricing</h2>
        <div className="flex gap-4">
          <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg">
            <span className="text-white/40 text-sm">Per use: </span>
            <span className="font-mono text-cyan-400">
              {skill.price_per_use ? `$${skill.price_per_use}` : "FREE"}
            </span>
          </div>
          {skill.license_fee && (
            <div className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg">
              <span className="text-white/40 text-sm">License: </span>
              <span className="font-mono text-cyan-400">${skill.license_fee}</span>
            </div>
          )}
        </div>
      </div>

      {/* Tags */}
      {skill.tags.length > 0 && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Tags</h2>
          <div className="flex flex-wrap gap-2">
            {skill.tags.map((tag) => (
              <span
                key={tag}
                className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full text-sm text-cyan-400"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Install command */}
      <div className="mb-8 p-4 bg-white/5 border border-white/10 rounded-xl">
        <div className="text-xs text-white/40 mb-2">Install via CLI</div>
        <code className="text-cyan-400 font-mono">nexus-skill use {skill.skill_id}</code>
      </div>

      {/* SKILL.md content */}
      <div>
        <h2 className="text-lg font-semibold mb-3">SKILL.md</h2>
        <pre className="p-6 bg-white/5 border border-white/10 rounded-xl overflow-x-auto text-sm text-white/70 whitespace-pre-wrap">
          {skill.skill_md_content}
        </pre>
      </div>
    </div>
  );
}
