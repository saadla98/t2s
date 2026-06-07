"use client";

import { useEffect, useState } from "react";
import { History, FileText, ChevronDown, ShieldAlert, AlertTriangle, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getPredictionHistory, downloadReport } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";

export default function HistoryPage() {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await getPredictionHistory(50);
        setHistory(res);
      } catch (error) {
        console.error("Error fetching history:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "High":
        return <Badge className="bg-red-500/10 text-red-400 border-red-500/20 gap-1"><ShieldAlert className="w-3 h-3" />Élevé</Badge>;
      case "Medium":
        return <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20 gap-1"><AlertTriangle className="w-3 h-3" />Modéré</Badge>;
      default:
        return <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20 gap-1"><CheckCircle2 className="w-3 h-3" />Faible</Badge>;
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString("fr-FR", {
      day: "2-digit", month: "2-digit", year: "numeric",
      hour: "2-digit", minute: "2-digit"
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <History className="text-sky-400 h-6 w-6" />
          Historique des Prédictions
        </h2>
        <p className="text-slate-400">Consultez l'ensemble des diagnostics IA générés sur le parc de scanners.</p>
      </div>

      {loading ? (
        <div className="flex h-[50vh] items-center justify-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-sky-500/30 border-t-sky-500" />
        </div>
      ) : history.length === 0 ? (
        <Card className="glass-card">
          <CardContent className="flex flex-col items-center justify-center py-16 text-center">
            <History className="h-12 w-12 text-slate-600 mb-4" />
            <h3 className="text-slate-300 font-medium mb-1">Aucun historique disponible</h3>
            <p className="text-sm text-slate-500">Générez votre première prédiction depuis l'onglet "Prédiction IA".</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {history.map((item, idx) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
            >
              <Card className="glass-card overflow-hidden">
                <div
                  className="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-800/40 transition-colors"
                  onClick={() => setExpanded(expanded === item.id ? null : item.id)}
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-slate-800 flex items-center justify-center text-sky-400">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-medium text-white">{item.device_id || `Scan #${item.id}`}</p>
                      <p className="text-xs text-slate-500">{formatDate(item.created_at)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {getRiskBadge(item.predicted_risk)}
                    <span className="text-xs text-slate-400 hidden sm:block">
                      Score: <span className="text-white font-semibold">{item.health_score}</span>/100
                    </span>
                    <ChevronDown
                      className={`h-4 w-4 text-slate-500 transition-transform duration-200 ${expanded === item.id ? "rotate-180" : ""}`}
                    />
                  </div>
                </div>

                <AnimatePresence>
                  {expanded === item.id && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="border-t border-slate-800 p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="rounded-lg bg-slate-900/50 p-3 border border-slate-800">
                          <p className="text-xs text-slate-500 mb-1">Technicien</p>
                          <p className="text-sm font-medium text-white">{item.technician_name || "N/A"}</p>
                        </div>
                        <div className="rounded-lg bg-slate-900/50 p-3 border border-slate-800">
                          <p className="text-xs text-slate-500 mb-1">Score de Santé</p>
                          <p className="text-sm font-bold text-sky-400">{item.health_score} / 100</p>
                        </div>
                        <div className="rounded-lg bg-slate-900/50 p-3 border border-slate-800">
                          <p className="text-xs text-slate-500 mb-1">Niveau de Risque</p>
                          <p className="text-sm font-medium text-white">
                            {item.predicted_risk === 'High' ? 'Élevé' : item.predicted_risk === 'Medium' ? 'Modéré' : 'Faible'}
                          </p>
                        </div>
                        <div className="rounded-lg bg-slate-900/50 p-3 border border-slate-800">
                          <p className="text-xs text-slate-500 mb-1">Confiance</p>
                          <p className="text-sm font-medium text-white">
                            {item.confidence ? `${Number(item.confidence).toFixed(2)}%` : "N/A"}
                          </p>
                        </div>
                        {item.recommendation && (
                          <div className="col-span-2 md:col-span-4 rounded-lg bg-sky-500/10 border border-sky-500/20 p-3">
                            <p className="text-xs text-sky-400 font-medium mb-1">Recommandation IA</p>
                            <p className="text-sm text-slate-300">{item.recommendation}</p>
                          </div>
                        )}
                        <div className="col-span-2 md:col-span-4">
                          <Button
                            size="sm"
                            variant="outline"
                            className="border-slate-700 bg-slate-800/50 text-slate-300 hover:bg-slate-800 hover:text-white gap-2"
                            onClick={() => downloadReport(item.id)}
                          >
                            <FileText className="h-4 w-4" />
                            Télécharger le Rapport PDF
                          </Button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
