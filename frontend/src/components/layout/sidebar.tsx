"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  ActivitySquare,
  BarChart3,
  Network,
  Stethoscope,
  LogOut,
  Microscope,
  History
} from "lucide-react";

const navItems = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Tableau de Bord" },
  { href: "/scanners", icon: ActivitySquare, label: "Parc Scanners" },
  { href: "/prediction", icon: Stethoscope, label: "Prédiction IA" },
  { href: "/history", icon: History, label: "Historique" },
  { href: "/analytics", icon: BarChart3, label: "Analytiques EDA" },
  { href: "/models", icon: Network, label: "Modèles ML & SHAP" },
  { href: "/expert", icon: Microscope, label: "Module Expert" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-900/50 backdrop-blur-xl">
      <div className="flex h-[84px] items-center justify-center px-5 border-b border-slate-800">
        <Image
          src="/t2s_logo.png"
          alt="Techniques Science Santé by T2S Group"
          width={106}
          height={68}
          className="object-contain brightness-0 invert opacity-90"
          priority
        />
      </div>

      <div className="flex-1 overflow-y-auto py-6">
        <nav className="grid gap-1 px-4">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all duration-200",
                pathname === item.href
                  ? "bg-sky-500/10 text-sky-400 shadow-[inset_2px_0_0_0_#0ea5e9]"
                  : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-100"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          ))}
        </nav>
      </div>

      <div className="border-t border-slate-800 p-4">
        <div className="mb-4 rounded-lg bg-slate-800/50 p-4">
          <p className="text-sm font-medium text-slate-200">Jean Dupont</p>
          <p className="text-xs text-slate-400">Technicien Expert</p>
        </div>
        <Link
          href="/login"
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-400 hover:bg-slate-800/50 hover:text-red-400 transition-colors"
        >
          <LogOut className="h-4 w-4" />
          Déconnexion
        </Link>
      </div>
    </div>
  );
}
