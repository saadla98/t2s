"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, ActivitySquare, ShieldCheck, Zap, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col relative overflow-hidden">
      {/* Background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-sky-600/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-600/20 blur-[120px] pointer-events-none" />
      <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] rounded-full bg-indigo-600/10 blur-[100px] pointer-events-none" />

      {/* Navigation */}
      <header className="flex items-center justify-between px-8 py-6 z-10">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-sky-500/20 text-sky-400">
            <ActivitySquare className="h-6 w-6" />
          </div>
          <span className="text-2xl font-bold tracking-tight text-white">
            T2S <span className="text-sky-400">Predict</span>
          </span>
        </div>
        <Link href="/login">
          <Button variant="outline" className="border-slate-700 bg-slate-800/50 hover:bg-slate-800 text-white backdrop-blur-md">
            Connexion au Portail
          </Button>
        </Link>
      </header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center z-10 mt-[-5vh]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto space-y-8"
        >
          <div className="inline-flex items-center rounded-full border border-sky-500/30 bg-sky-500/10 px-3 py-1 text-sm font-medium text-sky-300">
            <span className="flex h-2 w-2 rounded-full bg-sky-400 mr-2 animate-pulse"></span>
            Intelligence Artificielle pour la Maintenance Biomédicale
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white">
            Anticipez les pannes.<br/>
            <span className="text-gradient">Maximisez la disponibilité.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
            La plateforme d'aide à la décision nouvelle génération pour l'estimation du risque de panne des scanners CT GE Optima 540. Propulsée par l'apprentissage automatique.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href="/login">
              <Button size="lg" className="bg-sky-500 hover:bg-sky-600 text-white h-12 px-8 text-lg rounded-full shadow-[0_0_20px_rgba(14,165,233,0.4)]">
                Accéder à la plateforme
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Feature Cards */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mt-24"
        >
          <div className="glass-card p-6 rounded-2xl text-left border-t border-t-white/10">
            <div className="h-12 w-12 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400 mb-4">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Maintenance Prédictive</h3>
            <p className="text-slate-400">Passez d'une approche réactive à une stratégie proactive grâce à nos modèles prédictifs haute précision.</p>
          </div>
          
          <div className="glass-card p-6 rounded-2xl text-left border-t border-t-white/10">
            <div className="h-12 w-12 rounded-xl bg-sky-500/20 flex items-center justify-center text-sky-400 mb-4">
              <Activity className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Diagnostic Expert</h3>
            <p className="text-slate-400">Identifiez précisément le module en cause avant même l'intervention pour optimiser la logistique des pièces.</p>
          </div>
          
          <div className="glass-card p-6 rounded-2xl text-left border-t border-t-white/10">
            <div className="h-12 w-12 rounded-xl bg-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
              <Zap className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Décisions Éclairées</h3>
            <p className="text-slate-400">Explications SHAP transparentes pour comprendre les facteurs clés derrière chaque prédiction de risque.</p>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
