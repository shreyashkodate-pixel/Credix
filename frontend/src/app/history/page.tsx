"use client";

import React, { useState, useEffect, useCallback } from "react";
import { AuthGuard } from "@/components/auth/auth-guard";
import { Navbar } from "@/components/navigation/navbar";
import { HistoryTable } from "@/components/history/history-table";
import { PredictionHistoryItem } from "@/types/api";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/context/auth-context";

export default function HistoryPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<PredictionHistoryItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(20);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getPredictionHistory(page, pageSize, token);
      setItems(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
          ? err.message
          : "Failed to retrieve historical evaluations."
      );
    } finally {
      setIsLoading(false);
    }
  }, [token, page, pageSize]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  return (
    <AuthGuard>
      <div className="min-h-screen bg-[#090a0c] text-zinc-100 flex flex-col">
        <Navbar />

        <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 py-6 sm:py-8">
          {/* Page Subtitle Banner */}
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-[#22242a] gap-2">
            <div>
              <h1 className="text-base font-semibold font-mono tracking-wider uppercase text-zinc-100">
                Evaluation Audit Ledger
              </h1>
              <p className="text-xs text-zinc-400 mt-0.5">
                Cryptographically tracked evaluation history scoped strictly to your authenticated
                account ID (Decision D-016).
              </p>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded bg-red-950/40 border border-red-900/60 text-xs font-mono text-red-300">
              <span className="font-semibold text-red-200">QUERY ERROR:</span> {error}
            </div>
          )}

          <HistoryTable
            items={items}
            total={total}
            page={page}
            pageSize={pageSize}
            onPageChange={(newPage) => setPage(newPage)}
            isLoading={isLoading}
          />
        </main>
      </div>
    </AuthGuard>
  );
}

