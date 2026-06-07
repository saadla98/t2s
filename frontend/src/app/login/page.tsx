"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ActivitySquare, Lock, User, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { motion } from "framer-motion";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<"technician" | "manager">("technician");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate authentication delay for effect
    setTimeout(() => {
      // In a real app we'd set a token/cookie here based on the role
      router.push("/dashboard");
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center relative overflow-hidden p-4">
      {/* Background gradients */}
      <div className="absolute top-0 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-sky-900/20 via-slate-950 to-slate-950 pointer-events-none"></div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md z-10"
      >
        <div className="glass-card rounded-2xl overflow-hidden border border-slate-800 shadow-2xl backdrop-blur-xl">
          {/* Header */}
          <div className="p-8 text-center border-b border-slate-800 bg-slate-900/50">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-500/20 text-sky-400 mb-4 shadow-[0_0_15px_rgba(14,165,233,0.3)]">
              <ActivitySquare className="h-8 w-8" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">T2S Predict</h1>
            <p className="text-slate-400 mt-2 text-sm">Portail de Maintenance Prédictive</p>
          </div>

          {/* Form */}
          <div className="p-8">
            <div className="flex gap-2 mb-8 bg-slate-900/50 p-1 rounded-lg border border-slate-800">
              <button
                type="button"
                onClick={() => setRole("technician")}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                  role === "technician" 
                    ? "bg-sky-500 text-white shadow-md" 
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Technicien
              </button>
              <button
                type="button"
                onClick={() => setRole("manager")}
                className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
                  role === "manager" 
                    ? "bg-indigo-500 text-white shadow-md" 
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Responsable
              </button>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="identifiant" className="text-slate-300">Identifiant T2S</Label>
                <div className="relative">
                  <User className="absolute left-3 top-2.5 h-5 w-5 text-slate-500" />
                  <Input 
                    id="identifiant" 
                    placeholder={role === "technician" ? "tech.dupont" : "resp.martin"} 
                    className="pl-10 bg-slate-900/50 border-slate-700 text-white placeholder:text-slate-600 focus-visible:ring-sky-500 h-11"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-slate-300">Mot de passe</Label>
                  <span className="text-xs text-sky-400 cursor-pointer hover:underline">Oublié ?</span>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-5 w-5 text-slate-500" />
                  <Input 
                    id="password" 
                    type="password" 
                    placeholder="••••••••" 
                    className="pl-10 bg-slate-900/50 border-slate-700 text-white placeholder:text-slate-600 focus-visible:ring-sky-500 h-11"
                    required
                  />
                </div>
              </div>

              {role === "manager" && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs mt-4">
                  <ShieldAlert className="h-4 w-4 shrink-0 mt-0.5" />
                  <p>L'accès responsable inclut les droits d'administration des modèles d'IA et la vue globale du parc.</p>
                </div>
              )}

              <Button 
                type="submit" 
                disabled={isLoading}
                className={`w-full h-11 mt-6 text-white font-medium ${
                  role === "technician" ? "bg-sky-500 hover:bg-sky-600" : "bg-indigo-500 hover:bg-indigo-600"
                }`}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                    Authentification...
                  </span>
                ) : (
                  "Se connecter"
                )}
              </Button>
            </form>
          </div>
          
          {/* Footer */}
          <div className="px-8 py-4 bg-slate-900/80 border-t border-slate-800 text-center">
            <p className="text-xs text-slate-500">
              Accès restreint au personnel autorisé T2S.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
