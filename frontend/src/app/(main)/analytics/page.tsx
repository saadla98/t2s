"use client";

import { useEffect, useState } from "react";
import { BarChart3, TrendingUp, Layers } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { getModuleDistribution, getAgeDistribution, getRiskByAge, getCorrelations, getRiskDistribution } from "@/lib/api";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  LineChart, Line
} from "recharts";

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [moduleDist, setModuleDist] = useState([]);
  const [ageDist, setAgeDist] = useState([]);
  const [riskByAge, setRiskByAge] = useState([]);
  const [correlations, setCorrelations] = useState<any>(null);
  const [riskDist, setRiskDist] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [modulesRes, ageRes, riskAgeRes, corrRes, riskRes] = await Promise.all([
          getModuleDistribution(),
          getAgeDistribution(),
          getRiskByAge(),
          getCorrelations(),
          getRiskDistribution()
        ]);
        
        setModuleDist(modulesRes);
        setAgeDist(ageRes);
        setRiskByAge(riskAgeRes);
        setCorrelations(corrRes);
        setRiskDist(riskRes);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center text-slate-400">Chargement des données analytiques...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart3 className="text-sky-400 h-6 w-6" />
            Exploration des Données (EDA)
          </h2>
          <p className="text-slate-400">Analysez les tendances historiques et les corrélations du parc matériel.</p>
        </div>
      </div>

      <Tabs defaultValue="modules" className="space-y-4">
        <TabsList className="bg-slate-900/50 border border-slate-800 flex-wrap h-auto">
          <TabsTrigger value="modules" className="data-[state=active]:bg-sky-500 data-[state=active]:text-white">Modules Affectés</TabsTrigger>
          <TabsTrigger value="demographics" className="data-[state=active]:bg-sky-500 data-[state=active]:text-white">Démographie du Parc</TabsTrigger>
          <TabsTrigger value="correlations" className="data-[state=active]:bg-sky-500 data-[state=active]:text-white">Matrice de Corrélation</TabsTrigger>
        </TabsList>

        <TabsContent value="modules" className="space-y-4">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-5 w-5 text-indigo-400" />
                Fréquence de Panne par Module
              </CardTitle>
              <CardDescription className="text-slate-400">Distribution historique des modules les plus fréquemment affectés.</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={moduleDist} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
                  <XAxis type="number" stroke="#94a3b8" />
                  <YAxis dataKey="module" type="category" stroke="#94a3b8" width={140} tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                  <RechartsTooltip 
                    cursor={{fill: 'rgba(255,255,255,0.05)'}}
                    contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                  />
                  <Bar dataKey="count" name="Nombre d'Occurrences" fill="#38bdf8" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="demographics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Distribution par Âge</CardTitle>
              </CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={ageDist}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="group" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <RechartsTooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', color: '#fff' }} />
                    <Bar dataKey="count" name="Nb. Scanners" fill="#818cf8" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Niveau de Risque selon l'Âge</CardTitle>
              </CardHeader>
              <CardContent className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={riskByAge}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="age_group" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <RechartsTooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', color: '#fff' }} />
                    <Legend />
                    <Bar dataKey="High" name="Risque Élevé" stackId="a" fill="#ef4444" />
                    <Bar dataKey="Medium" name="Risque Modéré" stackId="a" fill="#f59e0b" />
                    <Bar dataKey="Low" name="Risque Faible" stackId="a" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
          
          <Card className="glass-card mt-4">
            <CardHeader>
              <CardTitle>Distribution Globale des Risques</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              {riskDist && (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { name: "Risque Faible", value: riskDist.Low, fill: "#10b981" },
                    { name: "Risque Modéré", value: riskDist.Medium, fill: "#f59e0b" },
                    { name: "Risque Élevé", value: riskDist.High, fill: "#ef4444" }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="name" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <RechartsTooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', color: '#fff' }} />
                    <Bar dataKey="value" name="Nb. Scanners" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="correlations" className="space-y-4">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle>Matrice de Corrélation des Caractéristiques</CardTitle>
              <CardDescription className="text-slate-400">Corrélations linéaires (Pearson) entre les variables numériques continues.</CardDescription>
            </CardHeader>
            <CardContent>
              {correlations && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-center border-collapse">
                    <thead>
                      <tr>
                        <th className="p-2 border border-slate-700 bg-slate-800 text-slate-300">Variable</th>
                        {correlations.columns.map((col: string, i: number) => (
                          <th key={i} className="p-2 border border-slate-700 bg-slate-800 text-slate-300 text-xs truncate max-w-[100px]" title={col}>
                            {col.substring(0, 8)}...
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {correlations.data.map((row: number[], i: number) => (
                        <tr key={i}>
                          <th className="p-2 border border-slate-700 bg-slate-800 text-slate-300 text-left text-xs whitespace-nowrap">
                            {correlations.columns[i]}
                          </th>
                          {row.map((val: number, j: number) => {
                            // Color scale: red for negative, blue for positive, white for neutral
                            const intensity = Math.abs(val);
                            let bg = "";
                            if (val > 0.5) bg = `rgba(56, 189, 248, ${intensity})`; // Blue
                            else if (val > 0.1) bg = `rgba(56, 189, 248, ${intensity * 1.5})`; 
                            else if (val < -0.5) bg = `rgba(239, 68, 68, ${intensity})`; // Red
                            else if (val < -0.1) bg = `rgba(239, 68, 68, ${intensity * 1.5})`;
                            else bg = "transparent";
                            
                            return (
                              <td 
                                key={j} 
                                className="p-2 border border-slate-700 font-mono text-xs"
                                style={{ backgroundColor: bg, color: Math.abs(val) > 0.5 ? '#fff' : '#cbd5e1' }}
                                title={`${correlations.columns[i]} vs ${correlations.columns[j]}: ${val.toFixed(3)}`}
                              >
                                {val.toFixed(2)}
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
