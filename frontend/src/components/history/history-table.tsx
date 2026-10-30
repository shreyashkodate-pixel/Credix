"use client";

import React, { useState } from "react";
import { PredictionHistoryItem } from "@/types/api";
import { motion, AnimatePresence } from "framer-motion";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { CheckCircle2, XCircle, ChevronRight, X } from "lucide-react";

interface HistoryTableProps {
  items: PredictionHistoryItem[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  isLoading: boolean;
}

export function HistoryTable({
  items,
  total,
  page,
  pageSize,
  onPageChange,
  isLoading,
}: HistoryTableProps) {
  const [selectedRecord, setSelectedRecord] = useState<PredictionHistoryItem | null>(null);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="relative">
      <div className="card-terminal rounded border border-[#22242a] bg-[#111216] overflow-hidden shadow-sm">
        {/* Table Header */}
        <div className="px-5 py-4 border-b border-[#22242a] flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-zinc-100 uppercase font-mono">
              Prediction Audit History
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Personal immutable log of submitted loan outcome evaluations.
            </p>
          </div>
          <span className="text-xs font-mono text-zinc-500">
            TOTAL RECORDS: {total}
          </span>
        </div>

        {/* Table Body */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#22242a] bg-zinc-950/60 text-zinc-400 uppercase tracking-wider text-[11px]">
                <th className="px-5 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">Loan Requested</th>
                <th className="px-4 py-3 font-medium">Term</th>
                <th className="px-4 py-3 font-medium">Outcome</th>
                <th className="px-4 py-3 font-medium text-right">Probability</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2025]">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-zinc-500">
                    <div className="flex items-center justify-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-zinc-500 animate-ping" />
                      <span>RETRIEVING HISTORICAL LOGS...</span>
                    </div>
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-zinc-500">
                    No historical evaluation records found for this account.
                  </td>
                </tr>
              ) : (
                items.map((item) => {
                  const isApproved = item.outcome === "Approved";
                  const rawLoan = Number(item.input_snapshot?.loan_amount) || 0;
                  const loanAmountDollars = rawLoan * 1000;

                  return (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="hover:bg-zinc-950/50 transition-colors group cursor-pointer"
                      onClick={() => setSelectedRecord(item)}
                    >
                      <td className="px-5 py-3 text-zinc-300">
                        {formatDateTime(item.created_at)}
                      </td>
                      <td className="px-4 py-3 text-zinc-200 font-mono-numbers">
                        {formatCurrency(loanAmountDollars)}
                      </td>
                      <td className="px-4 py-3 text-zinc-400">
                        {String(item.input_snapshot?.loan_amount_term ?? 360)}m
                      </td>
                      <td className="px-4 py-3">
                        {isApproved ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 text-[11px] font-semibold">
                            <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                            <span>Approved</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-rose-950/60 border border-rose-800/60 text-rose-300 text-[11px] font-semibold">
                            <XCircle className="h-3 w-3 text-rose-400" />
                            <span>Rejected</span>
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-zinc-200 font-mono-numbers">
                        {item.probability ? `${(item.probability * 100).toFixed(1)}%` : "—"}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <button
                          type="button"
                          className="inline-flex items-center space-x-1 px-2 py-1 rounded border border-zinc-800 bg-zinc-900 group-hover:border-zinc-700 text-zinc-400 group-hover:text-zinc-200 transition-colors text-[11px]"
                        >
                          <span>Inspect</span>
                          <ChevronRight className="h-3 w-3" />
                        </button>
                      </td>
                    </motion.tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="px-5 py-3 border-t border-[#22242a] flex items-center justify-between text-xs font-mono">
            <span className="text-zinc-500">
              Page {page} of {totalPages}
            </span>
            <div className="flex items-center space-x-2">
              <button
                disabled={page <= 1 || isLoading}
                onClick={() => onPageChange(page - 1)}
                className="px-2.5 py-1 rounded border border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 disabled:opacity-40 transition-colors"
              >
                Previous
              </button>
              <button
                disabled={page >= totalPages || isLoading}
                onClick={() => onPageChange(page + 1)}
                className="px-2.5 py-1 rounded border border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 disabled:opacity-40 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Slide-over Inspection Drawer */}
      <AnimatePresence>
        {selectedRecord && (
          <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end">
            <motion.div
              initial={{ x: "100%" }}
              animate={{ x: 0 }}
              exit={{ x: "100%" }}
              transition={{ type: "spring", stiffness: 350, damping: 35 }}
              className="w-full max-w-lg bg-[#111216] border-l border-[#22242a] h-full overflow-y-auto p-6 shadow-2xl flex flex-col justify-between"
            >
              <div>
                {/* Drawer Header */}
                <div className="flex items-center justify-between pb-4 border-b border-[#22242a]">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-500">
                      HISTORICAL SNAPSHOT
                    </span>
                    <h3 className="text-sm font-semibold font-mono text-zinc-100 mt-0.5">
                      Evaluation #{selectedRecord.id.slice(0, 8)}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedRecord(null)}
                    className="p-1 rounded text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>

                {/* Outcome Summary Pill */}
                <div className="mt-5 p-3 rounded border border-zinc-800 bg-zinc-950/70 flex items-center justify-between">
                  <div>
                    <span className="text-[10px] font-mono text-zinc-500 uppercase block">Outcome</span>
                    <span
                      className={`text-xs font-mono font-bold ${
                        selectedRecord.outcome === "Approved" ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {selectedRecord.outcome.toUpperCase()}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-mono text-zinc-500 uppercase block">
                      Probability
                    </span>
                    <span className="text-xs font-mono font-bold text-zinc-200">
                      {selectedRecord.probability
                        ? `${(selectedRecord.probability * 100).toFixed(1)}%`
                        : "—"}
                    </span>
                  </div>
                </div>

                {/* Input Snapshot Values */}
                <div className="mt-5">
                  <h4 className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 mb-2.5">
                    Applicant Input Ledger Snapshot
                  </h4>
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">APPLICANT INCOME</span>
                      <span className="text-zinc-200 font-mono-numbers">
                        ${Number(selectedRecord.input_snapshot?.applicant_income || 0).toLocaleString()}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">CO-APPLICANT INCOME</span>
                      <span className="text-zinc-200 font-mono-numbers">
                        ${Number(selectedRecord.input_snapshot?.coapplicant_income || 0).toLocaleString()}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">LOAN REQUESTED</span>
                      <span className="text-zinc-200 font-mono-numbers">
                        ${((Number(selectedRecord.input_snapshot?.loan_amount) || 0) * 1000).toLocaleString()}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">TERM DURATION</span>
                      <span className="text-zinc-200">
                        {String(selectedRecord.input_snapshot?.loan_amount_term ?? "360")} Months
                      </span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">CREDIT CRITERIA</span>
                      <span className="text-zinc-200">
                        {Number(selectedRecord.input_snapshot?.credit_history) === 1
                          ? "Meets Guidelines (1)"
                          : "Deficient (0)"}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">EDUCATION</span>
                      <span className="text-zinc-200">
                        {String(selectedRecord.input_snapshot?.education ?? "")}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">SELF EMPLOYED</span>
                      <span className="text-zinc-200">
                        {String(selectedRecord.input_snapshot?.self_employed ?? "")}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-zinc-950 border border-zinc-900">
                      <span className="text-zinc-500 block text-[10px]">PROPERTY AREA</span>
                      <span className="text-zinc-200">
                        {String(selectedRecord.input_snapshot?.property_area ?? "")}
                      </span>
                    </div>
                  </div>
                </div>

                {/* TreeSHAP Explanation Factors */}
                <div className="mt-5">
                  <h4 className="text-[11px] font-mono uppercase tracking-wider text-zinc-400 mb-2.5">
                    Attribution Factors (TreeSHAP)
                  </h4>
                  <div className="space-y-2">
                    {(selectedRecord.explanation?.factors || []).map((factor, i) => (
                      <div
                        key={i}
                        className="p-2 rounded border border-zinc-900 bg-zinc-950/60 text-xs font-mono"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-zinc-300">{factor.factor}</span>
                          <span
                            className={
                              factor.impact === "positive"
                                ? "text-emerald-400 font-semibold"
                                : "text-rose-400 font-semibold"
                            }
                          >
                            {factor.impact === "positive" ? "+" : ""}
                            {factor.weight.toFixed(3)}
                          </span>
                        </div>
                        <p className="text-[10px] text-zinc-500 mt-0.5">{factor.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Drawer Footer */}
              <div className="pt-4 border-t border-[#22242a] text-[10px] font-mono text-zinc-500 flex items-center justify-between">
                <span>MODEL: {selectedRecord.model_version}</span>
                <span>{formatDateTime(selectedRecord.created_at)}</span>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

