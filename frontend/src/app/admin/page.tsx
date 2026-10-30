"use client";

import React from "react";
import { AuthGuard } from "@/components/auth/auth-guard";
import { Navbar } from "@/components/navigation/navbar";
import { AdminDashboard } from "@/components/admin/admin-dashboard";

export default function AdminPage() {
  return (
    <AuthGuard requireAdmin={true}>
      <div className="min-h-screen bg-[#090a0c] text-zinc-100 flex flex-col">
        <Navbar />

        <main className="flex-1 mx-auto max-w-7xl w-full px-4 sm:px-6 py-6 sm:py-8">
          <AdminDashboard />
        </main>
      </div>
    </AuthGuard>
  );
}

