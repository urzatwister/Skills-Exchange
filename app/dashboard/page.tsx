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
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [currentQuery, setCurrentQuery] = useState(initialQuery);
  const LIMIT = 12;

  const handleSearch = async (query: string, pageNum: number = 1) => {
    setLoading(true);
    setSearched(true);
    setCurrentQuery(query);
    setPage(pageNum);
    try {
      const offset = (pageNum - 1) * LIMIT;
      const res = await fetch(`${API_BASE}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ problem_statement: query, offset, limit: LIMIT }),
      });
      const data = await res.json();
      setResults(data.results || []);
      setTotal(data.total || 0);
    } catch {
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const loadAll = async (pageNum: number = 1) => {
    setLoading(true);
    setPage(pageNum);
    setCurrentQuery("");
    try {
      const offset = (pageNum - 1) * LIMIT;
      const res = await fetch(`${API_BASE}/api/skills?offset=${offset}&limit=${LIMIT}`);
      const data = await res.json();
      setResults(data.skills || []);
      setTotal(data.total || 0);
      setSearched(true);
    } catch {
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (initialQuery) {
      handleSearch(initialQuery, 1);
    } else {
      loadAll(1);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handlePageChange = (newPage: number) => {
    if (currentQuery) {
      handleSearch(currentQuery, newPage);
    } else {
      loadAll(newPage);
    }
  };

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div className="min-h-screen p-8 max-w-6xl mx-auto flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <Link href="/" className="text-2xl font-bold tracking-tight">
          <span className="text-cyan-400">Nexus</span> Exchange
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/developers" className="text-sm text-white/40 hover:text-cyan-400 transition-colors">
            Developer Portal
          </Link>
          <span className="text-sm text-white/30 font-mono">
            {total} skill{total !== 1 ? "s" : ""} registry
          </span>
        </div>
      </div>

      <div className="mb-10">
        <SearchBar onSearch={(q) => handleSearch(q, 1)} loading={loading} />
      </div>

      {loading && (
        <div className="text-center py-20 text-white/30 flex-grow">
          <div className="animate-pulse text-lg">Searching the registry...</div>
        </div>
      )}

      {!loading && searched && results.length === 0 && (
        <div className="text-center py-20 text-white/30 flex-grow">
          <div className="text-lg mb-2">No skills found</div>
          <p className="text-sm">Try a different search query or check that the API is running.</p>
        </div>
      )}

      {!loading && results.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-12 flex-grow">
            {results.map((skill) => (
              <SkillCard key={skill.skill_id} {...skill} />
            ))}
          </div>
          
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-6 mt-auto pb-8">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
                className="px-4 py-2 border border-white/10 rounded font-mono text-sm hover:bg-white/5 disabled:opacity-30 transition-colors"
              >
                &lt; Prev
              </button>
              <span className="text-white/50 font-mono text-sm">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
                className="px-4 py-2 border border-white/10 rounded font-mono text-sm hover:bg-white/5 disabled:opacity-30 transition-colors"
              >
                Next &gt;
              </button>
            </div>
          )}
        </>
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
