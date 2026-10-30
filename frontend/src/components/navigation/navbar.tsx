"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { motion } from "framer-motion";
import { History, Sliders, LogOut, Terminal, Users } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const { user, logout, isAdmin } = useAuth();

  const navItems = [
    { href: "/predict", label: "Evaluate", icon: Sliders },
    { href: "/history", label: "Audit History", icon: History },
    ...(isAdmin ? [{ href: "/admin", label: "Admin Console", icon: Users }] : []),
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#22242a] bg-[#090a0c]/90 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Brand / System Identity */}
        <div className="flex items-center space-x-3">
          <Link href="/predict" className="flex items-center space-x-2 group">
            <div className="flex h-7 w-7 items-center justify-center rounded border border-zinc-700 bg-zinc-900 group-hover:border-zinc-500 transition-colors">
              <Terminal className="h-4 w-4 text-zinc-300" />
            </div>
            <div className="flex flex-col">
              <span className="font-mono text-sm font-semibold tracking-wider text-zinc-100">
                CREDIX
              </span>
              <span className="text-[10px] font-mono tracking-widest text-zinc-500 uppercase -mt-1">
                Risk Engine v0.4.2
              </span>
            </div>
          </Link>

          <div className="hidden md:flex items-center ml-4 pl-4 border-l border-zinc-800">
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono border border-emerald-950/80 bg-emerald-950/30 text-emerald-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              API: ONLINE
            </span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="relative px-3 py-1.5 text-xs font-medium tracking-wide transition-colors"
              >
                <div
                  className={`flex items-center space-x-1.5 ${
                    isActive ? "text-zinc-100" : "text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{item.label}</span>
                </div>
                {isActive && (
                  <motion.div
                    layoutId="navbar-indicator"
                    className="absolute bottom-0 left-0 right-0 h-[2px] bg-zinc-300"
                    transition={{ type: "spring", stiffness: 450, damping: 35 }}
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Badge & Actions */}
        <div className="flex items-center space-x-3">
          {user && (
            <div className="hidden sm:flex items-center space-x-2 text-xs font-mono">
              <span className="text-zinc-400 truncate max-w-[150px]">{user.email}</span>
              <span
                className={`px-1.5 py-0.5 text-[10px] rounded uppercase font-semibold border ${
                  isAdmin
                    ? "border-amber-800/60 bg-amber-950/30 text-amber-300"
                    : "border-zinc-700 bg-zinc-800/60 text-zinc-300"
                }`}
              >
                {user.role}
              </span>
            </div>
          )}

          <button
            onClick={() => logout()}
            title="Terminate Session"
            className="flex items-center space-x-1 px-2.5 py-1 text-xs font-mono rounded border border-zinc-800 hover:border-zinc-600 bg-zinc-900/50 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            <LogOut className="h-3 w-3" />
            <span className="hidden sm:inline">Exit</span>
          </button>
        </div>
      </div>
    </header>
  );
}

