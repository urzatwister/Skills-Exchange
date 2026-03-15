"use client";

import { useState } from "react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  loading?: boolean;
}

export default function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe what you need... e.g. 'parse and validate CSV data'"
          className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl text-lg
                     placeholder:text-white/30 focus:outline-none focus:border-cyan-500/50
                     focus:ring-2 focus:ring-cyan-500/20 transition-all"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2.5 bg-cyan-600
                     hover:bg-cyan-500 disabled:bg-white/10 disabled:text-white/30
                     rounded-xl font-medium transition-colors"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
    </form>
  );
}
