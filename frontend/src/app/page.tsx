"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { Terminal, ShieldCheck, ArrowRight, BarChart3, Cpu } from "lucide-react";

export default function HomePage() {
  const { user, token, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && token && user) {
      router.replace("/predict");
    }
  }, [user, token, isLoading, router]);

  return (
    <div className="min-h-screen bg-[#090a0c] text-zinc-100 flex flex-col justify-between">
      {/* Top Header */}
      <header className="border-b border-[#22242a] px-6 py-4">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="flex h-7 w-7 items-center justify-center rounded border border-zinc-700 bg-zinc-900">
              <Terminal className="h-4 w-4 text-zinc-200" />
            </div>
            <span className="font-mono text-sm font-semibold tracking-wider text-zinc-100">
              CREDIX
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono">
            <Link
              href="/login"
              className="px-3 py-1.5 rounded border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="px-3 py-1.5 rounded bg-zinc-100 hover:bg-white text-zinc-900 font-semibold transition-colors"
            >
              Register
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-5xl px-4 sm:px-6 py-16 sm:py-24 text-center">
        {/* Release Tag */}
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-zinc-800 bg-zinc-900/60 text-[11px] font-mono text-zinc-400 mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>PRODUCTION CANDIDATE v0.4.2 — PHASE 5 COMPLETE</span>
        </div>

        {/* Hero Title */}
        <h1 className="text-3xl sm:text-5xl font-mono font-bold tracking-tight text-zinc-100 max-w-3xl mx-auto uppercase">
          Institutional Loan Underwriting & Attribution
        </h1>

        <p className="mt-4 text-sm sm:text-base text-zinc-400 max-w-2xl mx-auto font-sans leading-relaxed">
          High-performance algorithmic loan outcome evaluation powered by a calibrated Random Forest
          champion model and sub-millisecond local TreeSHAP feature attributions. Built with strict ECOA
          Fair Lending compliance.
        </p>

        {/* Action Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/login"
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-2.5 rounded bg-zinc-100 hover:bg-white text-zinc-900 text-xs font-semibold tracking-wide transition-colors"
          >
            <span>Launch Evaluation Terminal</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
          <Link
            href="/register"
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-2.5 rounded border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 text-xs font-mono transition-colors"
          >
            <span>Create Applicant Account</span>
          </Link>
        </div>

        {/* Architectural Highlights Grid */}
        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
          <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-5">
            <div className="w-8 h-8 rounded border border-zinc-800 bg-zinc-900 flex items-center justify-center mb-3 text-zinc-300">
              <Cpu className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-mono font-semibold uppercase text-zinc-200">
              Champion Model
            </h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              150-tree Random Forest with 5-fold CV (ROC-AUC 0.7639, PR-AUC 0.8569, Rejected Precision 92.2%).
            </p>
          </div>

          <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-5">
            <div className="w-8 h-8 rounded border border-zinc-800 bg-zinc-900 flex items-center justify-center mb-3 text-zinc-300">
              <BarChart3 className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-mono font-semibold uppercase text-zinc-200">
              TreeSHAP Explainability
            </h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Sub-millisecond local attribution delivering exact marginal mathematical weights for every applicant factor.
            </p>
          </div>

          <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-5">
            <div className="w-8 h-8 rounded border border-zinc-800 bg-zinc-900 flex items-center justify-center mb-3 text-zinc-300">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
            </div>
            <h3 className="text-xs font-mono font-semibold uppercase text-zinc-200">
              ECOA Fair Lending
            </h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Strict exclusion of demographic markers (gender, marital status, race) at the API schema boundary.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#22242a] px-6 py-4 text-center text-xs font-mono text-zinc-500">
        <div className="mx-auto max-w-7xl flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>CREDIX UNDERWRITING ENGINE // PORTFOLIO ARCHITECTURE</span>
          <span>FASTAPI + SCIKIT-LEARN + NEXT.JS 14</span>
        </div>
      </footer>
    </div>
  );
}
