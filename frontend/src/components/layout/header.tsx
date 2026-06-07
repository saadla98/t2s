"use client";

import { usePathname } from "next/navigation";
import { Bell, Search } from "lucide-react";
import { Input } from "@/components/ui/input";

export function Header() {
  const pathname = usePathname();
  
  // Format pathname into a readable title
  const title = pathname === "/" 
    ? "Tableau de Bord" 
    : pathname.split("/").filter(Boolean).map(p => 
        p.charAt(0).toUpperCase() + p.slice(1).replace("-", " ")
      ).join(" / ");

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-900/50 px-6 backdrop-blur-xl">
      <div>
        <h1 className="text-xl font-semibold text-slate-100">{title}</h1>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="relative hidden md:block">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
          <Input
            type="search"
            placeholder="Rechercher..."
            className="w-64 border-slate-800 bg-slate-900/50 pl-9 text-slate-300 placeholder:text-slate-500 focus-visible:ring-sky-500"
          />
        </div>
        
        <button className="relative flex h-9 w-9 items-center justify-center rounded-full border border-slate-800 bg-slate-900/50 text-slate-400 hover:bg-slate-800 hover:text-slate-100 transition-colors">
          <Bell className="h-4 w-4" />
          <span className="absolute right-2 top-2 flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-sky-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-sky-500"></span>
          </span>
        </button>
      </div>
    </header>
  );
}
