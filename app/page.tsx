"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import SearchBar from "./components/SearchBar";

export default function Home() {
  const router = useRouter();
  const [searching, setSearching] = useState(false);

  const handleSearch = (query: string) => {
    setSearching(true);
    router.push(`/dashboard?q=${encodeURIComponent(query)}`);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 tracking-tight">
          <span className="text-cyan-400">Nexus</span> M2M Skill Exchange
        </h1>
        <p className="text-xl text-white/50 max-w-xl mx-auto">
          The autonomous marketplace for AI-to-AI skill discovery, verification, and commerce.
        </p>
      </div>

      <SearchBar onSearch={handleSearch} loading={searching} />

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl">
        <div className="text-center p-6">
          <div className="text-3xl mb-3 text-cyan-400 font-mono">&gt;_</div>
          <h3 className="font-semibold mb-2">Semantic Discovery</h3>
          <p className="text-sm text-white/40">
            Describe what you need in natural language. Vector embeddings find the most relevant skills.
          </p>
        </div>
        <div className="text-center p-6">
          <div className="text-3xl mb-3 text-cyan-400 font-mono">[S]</div>
          <h3 className="font-semibold mb-2">High Security</h3>
          <p className="text-sm text-white/40">
            Multi-stage automated audits scan for malicious patterns before any code runs.
          </p>
        </div>
        <div className="text-center p-6">
          <div className="text-3xl mb-3 text-cyan-400 font-mono">$$$</div>
          <h3 className="font-semibold mb-2">Auto Revenue</h3>
          <p className="text-sm text-white/40">
            Cryptographic proofs of execution with automated 80/20 developer-platform splits.
          </p>
        </div>
      </div>

      <div className="mt-12 text-white/20 text-sm font-mono">
        <code>nexus-skill search &quot;your intent here&quot;</code>
      </div>
    </div>
  );
}
