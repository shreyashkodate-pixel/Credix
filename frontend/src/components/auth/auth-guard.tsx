"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";

interface AuthGuardProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export function AuthGuard({ children, requireAdmin = false }: AuthGuardProps) {
  const { user, token, isLoading, isAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!token || !user) {
        router.replace("/login");
      } else if (requireAdmin && !isAdmin) {
        router.replace("/predict");
      }
    }
  }, [user, token, isLoading, isAdmin, requireAdmin, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-400 font-mono text-xs">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>INITIALIZING SECURITY CONTEXT...</span>
        </div>
      </div>
    );
  }

  if (!token || !user || (requireAdmin && !isAdmin)) {
    return null;
  }

  return <>{children}</>;
}

