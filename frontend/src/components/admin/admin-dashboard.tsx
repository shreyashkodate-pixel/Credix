"use client";

import React, { useState, useEffect, useCallback } from "react";
import { AdminDashboardMetrics, AdminUserListPage, UserResponse } from "@/types/api";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/context/auth-context";
import { Users, FileText, CheckCircle2, XCircle, TrendingUp, ShieldAlert, RefreshCw } from "lucide-react";
import { formatDateTime } from "@/lib/utils";

export function AdminDashboard() {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState<AdminDashboardMetrics | null>(null);
  const [usersPage, setUsersPage] = useState<AdminUserListPage | null>(null);
  const [page, setPage] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    setError(null);
    try {
      const [dashMetrics, users] = await Promise.all([
        api.getAdminDashboard(token),
        api.getAdminUsers(page, 15, token),
      ]);
      setMetrics(dashMetrics);
      setUsersPage(users);
    } catch (err: unknown) {
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
          ? err.message
          : "Failed to load administrative console."
      );
    } finally {
      setIsLoading(false);
    }
  }, [token, page]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="space-y-6">
      {/* Console Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold tracking-wide text-zinc-100 uppercase font-mono">
            System Administration & Telemetry
          </h1>
          <p className="text-xs text-zinc-400 mt-0.5">
            Platform-wide throughput metrics, user directory, and security audit integrity.
          </p>
        </div>
        <button
          onClick={() => loadData()}
          disabled={isLoading}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-mono transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`h-3 w-3 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refresh Telemetry</span>
        </button>
      </div>

      {error && (
        <div className="p-3 rounded bg-red-950/40 border border-red-900/60 text-xs font-mono text-red-300">
          <span className="font-semibold text-red-200">ADMIN API ERROR:</span> {error}
        </div>
      )}

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-4">
          <div className="flex items-center justify-between text-zinc-500 mb-1">
            <span className="text-[10px] font-mono uppercase tracking-wider">Registered Users</span>
            <Users className="h-4 w-4" />
          </div>
          <div className="text-xl font-bold font-mono text-zinc-100">
            {metrics?.total_users ?? "—"}
          </div>
        </div>

        <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-4">
          <div className="flex items-center justify-between text-zinc-500 mb-1">
            <span className="text-[10px] font-mono uppercase tracking-wider">Total Evaluations</span>
            <FileText className="h-4 w-4" />
          </div>
          <div className="text-xl font-bold font-mono text-zinc-100">
            {metrics?.total_predictions ?? "—"}
          </div>
        </div>

        <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-4">
          <div className="flex items-center justify-between text-zinc-500 mb-1">
            <span className="text-[10px] font-mono uppercase tracking-wider">Approved</span>
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          </div>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {metrics?.approved_predictions ?? "—"}
          </div>
        </div>

        <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-4">
          <div className="flex items-center justify-between text-zinc-500 mb-1">
            <span className="text-[10px] font-mono uppercase tracking-wider">Rejected</span>
            <XCircle className="h-4 w-4 text-rose-500" />
          </div>
          <div className="text-xl font-bold font-mono text-rose-400">
            {metrics?.rejected_predictions ?? "—"}
          </div>
        </div>

        <div className="card-terminal rounded border border-[#22242a] bg-[#111216] p-4">
          <div className="flex items-center justify-between text-zinc-500 mb-1">
            <span className="text-[10px] font-mono uppercase tracking-wider">Approval Ratio</span>
            <TrendingUp className="h-4 w-4 text-zinc-400" />
          </div>
          <div className="text-xl font-bold font-mono text-zinc-100">
            {metrics ? `${metrics.approval_rate_percent}%` : "—"}
          </div>
        </div>
      </div>

      {/* User Directory Table */}
      <div className="card-terminal rounded border border-[#22242a] bg-[#111216] overflow-hidden shadow-sm">
        <div className="px-5 py-4 border-b border-[#22242a] flex items-center justify-between">
          <h2 className="text-sm font-semibold tracking-wide text-zinc-100 uppercase font-mono">
            User Account Directory
          </h2>
          <span className="text-xs font-mono text-zinc-500">
            TOTAL USERS: {usersPage?.total ?? 0}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#22242a] bg-zinc-950/60 text-zinc-400 uppercase tracking-wider text-[11px]">
                <th className="px-5 py-3 font-medium">User Identifier</th>
                <th className="px-4 py-3 font-medium">Email Address</th>
                <th className="px-4 py-3 font-medium">Assigned Role</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Created At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e2025]">
              {isLoading && !usersPage ? (
                <tr>
                  <td colSpan={5} className="px-5 py-8 text-center text-zinc-500">
                    LOADING USER DIRECTORY...
                  </td>
                </tr>
              ) : (
                (usersPage?.users || []).map((u: UserResponse) => (
                  <tr key={u.id} className="hover:bg-zinc-950/50 transition-colors">
                    <td className="px-5 py-3 text-zinc-400">{u.id.slice(0, 8)}...</td>
                    <td className="px-4 py-3 text-zinc-200 font-medium">{u.email}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                          u.role === "admin"
                            ? "border-amber-800/60 bg-amber-950/30 text-amber-300"
                            : "border-zinc-700 bg-zinc-800/60 text-zinc-300"
                        }`}
                      >
                        {u.role.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center space-x-1 text-emerald-400">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                        <span>Active</span>
                      </span>
                    </td>
                    <td className="px-5 py-3 text-right text-zinc-400">
                      {formatDateTime(u.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* User Directory Pagination */}
        {usersPage && usersPage.total > usersPage.page_size && (
          <div className="px-5 py-3 border-t border-[#22242a] flex items-center justify-between text-xs font-mono">
            <span className="text-zinc-500">
              Page {usersPage.page} of {Math.ceil(usersPage.total / usersPage.page_size)}
            </span>
            <div className="flex items-center space-x-2">
              <button
                disabled={usersPage.page <= 1 || isLoading}
                onClick={() => setPage(page - 1)}
                className="px-2.5 py-1 rounded border border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 disabled:opacity-40 transition-colors"
              >
                Previous
              </button>
              <button
                disabled={
                  usersPage.page >= Math.ceil(usersPage.total / usersPage.page_size) || isLoading
                }
                onClick={() => setPage(page + 1)}
                className="px-2.5 py-1 rounded border border-zinc-800 bg-zinc-900 text-zinc-300 hover:bg-zinc-800 disabled:opacity-40 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Security Audit Statement */}
      <div className="p-4 rounded border border-zinc-800/80 bg-zinc-950/60 flex items-start space-x-3 text-xs text-zinc-400 font-mono">
        <ShieldAlert className="h-4 w-4 text-zinc-400 mt-0.5 flex-shrink-0" />
        <p className="leading-relaxed">
          <strong className="text-zinc-300">Security Audit Trail Active:</strong> All administrative
          queries and authentication attempts are immutably logged to the <code className="text-zinc-300">audit_events</code> table. Sensitive credentials (passwords, tokens, applicant payloads) are strictly excluded from logging at the service layer.
        </p>
      </div>
    </div>
  );
}

