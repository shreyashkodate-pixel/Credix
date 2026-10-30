"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { motion } from "framer-motion";
import { Terminal, Lock, Mail, ArrowRight } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { login, token, error, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (token) {
      router.replace("/predict");
    }
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setIsSubmitting(true);
    try {
      await login(email, password);
      router.push("/predict");
    } catch {
      // Error handled by AuthContext
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTestLogin = (userEmail: string, pass: string) => {
    setEmail(userEmail);
    setPassword(pass);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-4 sm:px-6 bg-[#090a0c] text-zinc-100">
      <div className="w-full max-w-sm">
        {/* Brand Header */}
        <div className="text-center mb-6">
          <div className="inline-flex h-9 w-9 items-center justify-center rounded border border-zinc-700 bg-zinc-900 mb-2">
            <Terminal className="h-5 w-5 text-zinc-200" />
          </div>
          <h1 className="text-lg font-semibold font-mono tracking-wider text-zinc-100 uppercase">
            CREDIX // RISK ENGINE
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Institutional Loan Outcome Evaluation Terminal
          </p>
        </div>

        {/* Login Card */}
        <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-6 shadow-md">
          <div className="pb-4 mb-4 border-b border-[#22242a]">
            <h2 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-300">
              Authentication Portal
            </h2>
            <p className="text-[11px] text-zinc-500 mt-0.5">
              Enter registered credentials to access underwriting services.
            </p>
          </div>

          {error && (
            <div className="mb-4 p-2.5 rounded bg-red-950/40 border border-red-900/60 text-xs font-mono text-red-300">
              <span className="font-semibold text-red-200">ERROR:</span> {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Account Email
              </label>
              <div className="relative">
                <Mail className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@credix.internal"
                  className="w-full pl-8 pr-3 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-8 pr-3 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-colors"
                />
              </div>
            </div>

            <motion.button
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 inline-flex items-center justify-center space-x-2 py-2 rounded bg-zinc-100 hover:bg-white text-zinc-900 text-xs font-semibold tracking-wide transition-colors disabled:opacity-50"
            >
              {isSubmitting ? (
                <span className="font-mono">AUTHENTICATING...</span>
              ) : (
                <>
                  <span>Sign In to Terminal</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </>
              )}
            </motion.button>
          </form>

          {/* Quick Credential Presets */}
          <div className="mt-5 pt-4 border-t border-[#22242a]">
            <span className="block text-[10px] font-mono uppercase tracking-wider text-zinc-500 mb-2">
              Development Test Accounts
            </span>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <button
                type="button"
                onClick={() => handleTestLogin("admin@credix.internal", "AdminSecurePass123!")}
                className="p-1.5 rounded border border-zinc-800 bg-zinc-950/60 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 text-left transition-colors"
              >
                <span className="text-zinc-300 block font-semibold">Admin Account</span>
                <span className="text-[10px] text-zinc-500">Full telemetry</span>
              </button>
              <button
                type="button"
                onClick={() => handleTestLogin("applicant@example.com", "ApplicantPass123!")}
                className="p-1.5 rounded border border-zinc-800 bg-zinc-950/60 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 text-left transition-colors"
              >
                <span className="text-zinc-300 block font-semibold">User Account</span>
                <span className="text-[10px] text-zinc-500">Applicant flow</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="mt-4 text-center text-xs font-mono text-zinc-500">
          <span>New applicant? </span>
          <Link href="/register" className="text-zinc-300 hover:underline">
            Register new account
          </Link>
        </div>
      </div>
    </div>
  );
}

