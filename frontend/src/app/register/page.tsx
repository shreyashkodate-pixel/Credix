"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { motion } from "framer-motion";
import { Terminal, Lock, Mail, ArrowRight, ShieldCheck } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const { register, error, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError(null);

    if (password.length < 8) {
      setValidationError("Password must be at least 8 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setValidationError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      await register(email, password);
      router.push("/predict");
    } catch {
      // Error handled by AuthContext
    } finally {
      setIsSubmitting(false);
    }
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
            Create Authorized Applicant Account
          </p>
        </div>

        {/* Register Card */}
        <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-6 shadow-md">
          <div className="pb-4 mb-4 border-b border-[#22242a]">
            <h2 className="text-xs font-mono font-medium uppercase tracking-wider text-zinc-300">
              Account Registration
            </h2>
            <p className="text-[11px] text-zinc-500 mt-0.5">
              Role defaults to standard applicant user with private history scoping.
            </p>
          </div>

          {(error || validationError) && (
            <div className="mb-4 p-2.5 rounded bg-red-950/40 border border-red-900/60 text-xs font-mono text-red-300">
              <span className="font-semibold text-red-200">ERROR:</span> {error || validationError}
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
                  placeholder="applicant@example.com"
                  className="w-full pl-8 pr-3 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-zinc-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Password (min. 8 characters)
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

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-zinc-500" />
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
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
                <span className="font-mono">PROVISIONING ACCOUNT...</span>
              ) : (
                <>
                  <span>Create Account & Enter</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </>
              )}
            </motion.button>
          </form>

          {/* Privacy Note */}
          <div className="mt-4 pt-3 border-t border-[#22242a] flex items-center space-x-2 text-[11px] text-zinc-500">
            <ShieldCheck className="h-3.5 w-3.5 text-zinc-400 flex-shrink-0" />
            <span>Passwords securely hashed with native bcrypt.</span>
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="mt-4 text-center text-xs font-mono text-zinc-500">
          <span>Already registered? </span>
          <Link href="/login" className="text-zinc-300 hover:underline">
            Sign in to existing account
          </Link>
        </div>
      </div>
    </div>
  );
}

