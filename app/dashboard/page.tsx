"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import SearchBar from "../components/SearchBar";
import SkillCard from "../components/SkillCard";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_NEXUS_API_URL || "http://localhost:8000";

interface SkillResult {
  skill_id: string;
  name: string;
  description: string;
  confidence?: number;
  risk_score?: number | null;
  price_per_use?: number | null;
  author: string;
  tags?: string[];
}

function DashboardContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const [results, setResults] = useState<SkillResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setSearched(true);
    try {
      const res = await fetch(`${API_BASE}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problem_statement: query }),
      });
      const data = await res.json();
      setResults(data.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const loadAll = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/skills`);
      const data = await res.json();
      setResults(data.skills || []);
      setSearched(true);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      handleSearch(initialQuery);
    } else {
      loadAll();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="min-h-screen p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <Link href="/" className="text-2xl font-bold tracking-tight">
          <span className="text-cyan-400">Nexus</span> Exchange
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/developers" className="text-sm text-white/40 hover:text-cyan-400 transition-colors">
            Developer Portal
          </Link>
          <span className="text-sm text-white/30 font-mono">
            {results.length} skill{results.length !== 1 ? "s" : ""}
          </span>
        </div>
      </div>

      <div className="mb-10">
        <SearchBar onSearch={handleSearch} loading={loading} />
      </div>

      {loading && (
        <div className="text-center py-20 text-white/30">
          <div className="animate-pulse text-lg">Searching the registry...</div>
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="text-center py-20 text-white/30">
          <div className="text-lg mb-2">No skills found</div>
          <p className="text-sm">Try a different search query or check that the API is running.</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((skill) => (
            <SkillCard key={skill.skill_id} {...skill} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center text-white/30">Loading...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
