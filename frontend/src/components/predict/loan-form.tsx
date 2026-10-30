"use client";

import React, { useState, useEffect } from "react";
import { PredictionInput, AllowedLoanTerm, AllowedCreditHistory, AllowedEducation, AllowedSelfEmployed, AllowedDependents, AllowedPropertyArea } from "@/types/api";
import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight, RefreshCw } from "lucide-react";

interface LoanFormProps {
  onSubmit: (data: PredictionInput) => Promise<void>;
  isLoading: boolean;
  error?: string | null;
}

const DEFAULT_VALUES: PredictionInput = {
  applicant_income: 5400,
  coapplicant_income: 1800,
  loan_amount: 140,
  loan_amount_term: 360,
  credit_history: 1,
  education: "Graduate",
  self_employed: "No",
  dependents: "0",
  property_area: "Semiurban",
};

const PRESETS = [
  {
    name: "Prime Profile (High Approval)",
    data: {
      applicant_income: 6500,
      coapplicant_income: 2200,
      loan_amount: 120,
      loan_amount_term: 360 as AllowedLoanTerm,
      credit_history: 1 as AllowedCreditHistory,
      education: "Graduate" as AllowedEducation,
      self_employed: "No" as AllowedSelfEmployed,
      dependents: "0" as AllowedDependents,
      property_area: "Semiurban" as AllowedPropertyArea,
    },
  },
  {
    name: "Subprime Profile (High Risk)",
    data: {
      applicant_income: 2400,
      coapplicant_income: 0,
      loan_amount: 280,
      loan_amount_term: 360 as AllowedLoanTerm,
      credit_history: 0 as AllowedCreditHistory,
      education: "Not Graduate" as AllowedEducation,
      self_employed: "Yes" as AllowedSelfEmployed,
      dependents: "3+" as AllowedDependents,
      property_area: "Rural" as AllowedPropertyArea,
    },
  },
];

export function LoanForm({ onSubmit, isLoading, error }: LoanFormProps) {
  const [formData, setFormData] = useState<PredictionInput>(DEFAULT_VALUES);

  // Keyboard shortcut listener: Cmd/Ctrl + Enter to submit
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        if (!isLoading) {
          onSubmit(formData);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [formData, isLoading, onSubmit]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handlePreset = (presetData: PredictionInput) => {
    setFormData(presetData);
  };

  return (
    <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-5 shadow-sm">
      {/* Header & Presets */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#22242a] gap-2">
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-zinc-100 uppercase font-mono">
            Application Input Ledger
          </h2>
          <p className="text-xs text-zinc-400 mt-0.5">
            Input verified applicant parameters for underwriting evaluation.
          </p>
        </div>

        {/* Quick Benchmarking Presets */}
        <div className="flex items-center space-x-1.5 self-start sm:self-auto">
          <span className="text-[10px] uppercase font-mono tracking-wider text-zinc-500 mr-1">
            Presets:
          </span>
          {PRESETS.map((preset) => (
            <button
              key={preset.name}
              type="button"
              onClick={() => handlePreset(preset.data)}
              className="text-[11px] font-mono px-2 py-0.5 rounded border border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 hover:text-zinc-200 text-zinc-400 transition-colors"
            >
              {preset.name.split(" ")[0]}
            </button>
          ))}
          <button
            type="button"
            onClick={() => setFormData(DEFAULT_VALUES)}
            title="Reset to default"
            className="p-1 text-zinc-500 hover:text-zinc-300 transition-colors"
          >
            <RefreshCw className="h-3 w-3" />
          </button>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 rounded bg-red-950/40 border border-red-900/60 text-xs font-mono text-red-300">
          <span className="font-semibold text-red-200">VALIDATION REJECTION:</span> {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="mt-5 space-y-6">
        {/* Section 1: Financial Profile */}
        <div>
          <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 mb-2.5 flex items-center justify-between">
            <span>01 // Financial Profile</span>
            <span className="text-zinc-600 text-[10px]">MONTHLY GROSS ($)</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Primary Applicant Income ($/mo)
              </label>
              <div className="relative">
                <span className="absolute left-2.5 top-2 text-xs font-mono text-zinc-500">$</span>
                <input
                  type="number"
                  min="1"
                  step="1"
                  required
                  value={formData.applicant_income}
                  onChange={(e) =>
                    setFormData({ ...formData, applicant_income: parseFloat(e.target.value) || 0 })
                  }
                  className="w-full pl-6 pr-3 py-1.5 text-xs font-mono-numbers bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Co-Applicant Income ($/mo)
              </label>
              <div className="relative">
                <span className="absolute left-2.5 top-2 text-xs font-mono text-zinc-500">$</span>
                <input
                  type="number"
                  min="0"
                  step="1"
                  value={formData.coapplicant_income}
                  onChange={(e) =>
                    setFormData({ ...formData, coapplicant_income: parseFloat(e.target.value) || 0 })
                  }
                  className="w-full pl-6 pr-3 py-1.5 text-xs font-mono-numbers bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Loan Parameters */}
        <div>
          <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 mb-2.5 flex items-center justify-between">
            <span>02 // Loan Parameters</span>
            <span className="text-zinc-600 text-[10px]">AMOUNT & SCHEDULE</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Requested Amount ($ in Thousands)
              </label>
              <div className="relative">
                <span className="absolute left-2.5 top-2 text-xs font-mono text-zinc-500">$</span>
                <input
                  type="number"
                  min="1"
                  step="1"
                  required
                  value={formData.loan_amount}
                  onChange={(e) =>
                    setFormData({ ...formData, loan_amount: parseFloat(e.target.value) || 0 })
                  }
                  className="w-full pl-6 pr-3 py-1.5 text-xs font-mono-numbers bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
                />
              </div>
              <span className="block text-[10px] font-mono text-zinc-500 mt-1">
                Display: ${(formData.loan_amount * 1000).toLocaleString()} USD
              </span>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Loan Duration Term
              </label>
              <select
                value={formData.loan_amount_term}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    loan_amount_term: parseInt(e.target.value) as AllowedLoanTerm,
                  })
                }
                className="w-full px-3 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
              >
                <option value={12}>12 Months (1 Year)</option>
                <option value={36}>36 Months (3 Years)</option>
                <option value={60}>60 Months (5 Years)</option>
                <option value={120}>120 Months (10 Years)</option>
                <option value={180}>180 Months (15 Years)</option>
                <option value={240}>240 Months (20 Years)</option>
                <option value={300}>300 Months (25 Years)</option>
                <option value={360}>360 Months (30 Years)</option>
                <option value={480}>480 Months (40 Years)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 3: Credit History & Permitted Demographics */}
        <div>
          <div className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 mb-2.5 flex items-center justify-between">
            <span>03 // Underwriting Guidelines & Qualifications</span>
            <span className="text-zinc-600 text-[10px]">ECOA COMPLIANT</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Credit Guidelines Flag
              </label>
              <select
                value={formData.credit_history}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    credit_history: parseInt(e.target.value) as AllowedCreditHistory,
                  })
                }
                className="w-full px-2.5 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
              >
                <option value={1}>1 — Meets Guidelines</option>
                <option value={0}>0 — Criteria Deficient</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Completed Education
              </label>
              <select
                value={formData.education}
                onChange={(e) =>
                  setFormData({ ...formData, education: e.target.value as AllowedEducation })
                }
                className="w-full px-2.5 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
              >
                <option value="Graduate">Graduate</option>
                <option value="Not Graduate">Not Graduate</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Self Employment
              </label>
              <select
                value={formData.self_employed}
                onChange={(e) =>
                  setFormData({ ...formData, self_employed: e.target.value as AllowedSelfEmployed })
                }
                className="w-full px-2.5 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
              >
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Dependents
              </label>
              <select
                value={formData.dependents}
                onChange={(e) =>
                  setFormData({ ...formData, dependents: e.target.value as AllowedDependents })
                }
                className="w-full px-2.5 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
              >
                <option value="0">0 Dependents</option>
                <option value="1">1 Dependent</option>
                <option value="2">2 Dependents</option>
                <option value="3+">3+ Dependents</option>
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="block text-xs font-medium text-zinc-300 mb-1">
                Property Geographic Zone
              </label>
              <select
                value={formData.property_area}
                onChange={(e) =>
                  setFormData({ ...formData, property_area: e.target.value as AllowedPropertyArea })
                }
                className="w-full px-2.5 py-1.5 text-xs font-mono bg-zinc-950 border border-zinc-800 rounded text-zinc-100 focus:outline-none focus:border-zinc-500 transition-colors"
              >
                <option value="Urban">Urban</option>
                <option value="Semiurban">Semiurban</option>
                <option value="Rural">Rural</option>
              </select>
            </div>
          </div>
        </div>

        {/* Regulatory Fair Lending Banner */}
        <div className="p-3 rounded border border-zinc-800/80 bg-zinc-950/60 flex items-start space-x-2.5">
          <ShieldCheck className="h-4 w-4 text-zinc-400 mt-0.5 flex-shrink-0" />
          <p className="text-[11px] leading-relaxed text-zinc-400">
            <strong className="text-zinc-300 font-medium">ECOA Fair Lending Compliance:</strong> In
            accordance with Equal Credit Opportunity Act principles (Decision D-023), demographic
            variables (gender, marital status, race) are strictly omitted from the model feature
            vector and purged at the API schema boundary.
          </p>
        </div>

        {/* Action Button */}
        <div className="pt-2 flex items-center justify-between">
          <div className="hidden sm:flex items-center space-x-1 text-[11px] font-mono text-zinc-500">
            <span>Press</span>
            <kbd className="px-1.5 py-0.5 rounded border border-zinc-800 bg-zinc-900 text-zinc-400">
              ⌘ / Ctrl
            </kbd>
            <span>+</span>
            <kbd className="px-1.5 py-0.5 rounded border border-zinc-800 bg-zinc-900 text-zinc-400">
              Enter
            </kbd>
            <span>to evaluate</span>
          </div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={isLoading}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-5 py-2.5 rounded bg-zinc-100 hover:bg-white text-zinc-900 text-xs font-semibold tracking-wide transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <span className="inline-flex items-center space-x-2 font-mono">
                <span className="w-2 h-2 rounded-full bg-zinc-900 animate-ping" />
                <span>EXECUTING INFERENCE...</span>
              </span>
            ) : (
              <>
                <span>Evaluate Loan Risk</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </>
            )}
          </motion.button>
        </div>
      </form>
    </div>
  );
}

