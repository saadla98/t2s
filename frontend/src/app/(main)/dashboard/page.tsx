"use client";

import { useEffect, useState } from "react";
import { Activity, AlertTriangle, CheckCircle2, ShieldAlert, Cpu } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardSummary } from "@/lib/api";
import { formatCurrency, formatPercent } from "@/lib/utils";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await getDashboardSummary();
        setSummary(res);
      } catch (error) {
        console.error("Error fetching summary:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-sky-500/30 border-t-sky-500" />
          <p className="text-slate-400">Chargement des données du parc...</p>
        </div>
      </div>
    );
  }

  const riskData = [
    { name: "Risque Faible", value: summary?.low_risk_count || 0, color: "#10B981" },
    { name: "Risque Modéré", value: summary?.medium_risk_count || 0, color: "#F59E0B" },
    { name: "Risque Élevé", value: summary?.high_risk_count || 0, color: "#EF4444" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Vue d'ensemble du Parc CT</h2>
          <p className="text-slate-400">Suivi en temps réel de l'état de santé des scanners GE Optima 540.</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="glass-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Scanners Supervisés</CardTitle>
            <Activity className="h-4 w-4 text-sky-400" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">{summary?.total_scanners || 0}</div>
            <p className="text-xs text-slate-400 mt-1">Équipements actifs</p>
          </CardContent>
        </Card>

        <Card className="glass-card border-emerald-500/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Risque Faible</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-emerald-400">{summary?.low_risk_count || 0}</div>
            <p className="text-xs text-slate-400 mt-1">Fonctionnement optimal</p>
          </CardContent>
        </Card>

        <Card className="glass-card border-amber-500/20">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Risque Modéré</CardTitle>
            <AlertTriangle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-400">{summary?.medium_risk_count || 0}</div>
            <p className="text-xs text-slate-400 mt-1">Maintenance à planifier</p>
          </CardContent>
        </Card>

        <Card className="glass-card border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.1)]">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">Risque Élevé</CardTitle>
            <ShieldAlert className="h-4 w-4 text-red-500 animate-pulse" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-400">{summary?.high_risk_count || 0}</div>
            <p className="text-xs text-red-400/80 mt-1 font-medium">Intervention urgente requise</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="glass-card col-span-4">
          <CardHeader>
            <CardTitle>Indicateurs Moyens du Parc</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-slate-900/50 p-4 border border-slate-800">
                <div className="text-sm text-slate-400 mb-1">Âge Moyen</div>
                <div className="text-2xl font-bold text-white">{summary?.average_age || 0} <span className="text-sm font-normal text-slate-500">ans</span></div>
              </div>
              <div className="rounded-lg bg-slate-900/50 p-4 border border-slate-800">
                <div className="text-sm text-slate-400 mb-1">Temps d'Arrêt Moyen</div>
                <div className="text-2xl font-bold text-white">{summary?.average_downtime || 0} <span className="text-sm font-normal text-slate-500">jours</span></div>
              </div>
              <div className="rounded-lg bg-slate-900/50 p-4 border border-slate-800">
                <div className="text-sm text-slate-400 mb-1">MTBF (Moyenne)</div>
                <div className="text-2xl font-bold text-white">{summary?.average_mtbf || 0} <span className="text-sm font-normal text-slate-500">jours</span></div>
              </div>
              <div className="rounded-lg bg-slate-900/50 p-4 border border-slate-800">
                <div className="text-sm text-slate-400 mb-1">Coût Maintenance Moyen</div>
                <div className="text-2xl font-bold text-white">{formatCurrency(summary?.average_maintenance_cost || 0)}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card col-span-3">
          <CardHeader>
            <CardTitle>Répartition des Risques</CardTitle>
          </CardHeader>
          <CardContent className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
