"use client";

import { useEffect, useState } from "react";
import { Network, Trophy, Cpu, Search, HelpCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getModelComparison, getShapExplanation } from "@/lib/api";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from "recharts";

export default function ModelsPage() {
  const [loading, setLoading] = useState(true);
  const [modelData, setModelData] = useState<any>(null);
  const [featureImportance, setFeatureImportance] = useState<any>(null);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const [modelsRes, shapRes] = await Promise.all([
          getModelComparison(),
          getShapExplanation(1, "random_forest").catch(() => null) // We'll just fetch global feature importance using the models endpoint data or SHAP if available
        ]);
        setModelData(modelsRes);
        
        // Extract feature importance from the best model
        if (modelsRes.models && modelsRes.models.length > 0) {
          const bestModel = modelsRes.models.find((m: any) => m.is_best) || modelsRes.models[0];
          if (bestModel.feature_importance) {
            const formattedFi = Object.entries(bestModel.feature_importance)
              .map(([name, value]) => ({ name, value: Number(value) }))
              .sort((a, b) => b.value - a.value)
              .slice(0, 10);
            setFeatureImportance(formattedFi);
          }
        }
      } catch (error) {
        console.error("Error fetching models:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center text-slate-400">Chargement des métriques des modèles...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Network className="text-sky-400 h-6 w-6" />
            Évaluation des Modèles ML
          </h2>
          <p className="text-slate-400">Comparaison des performances et analyse d'explicabilité (SHAP).</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="glass-card md:col-span-2">
          <CardHeader>
            <CardTitle>Comparaison des Performances</CardTitle>
            <CardDescription className="text-slate-400">Évaluation basée sur la validation croisée stratifiée à 5 plis.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader className="bg-slate-900/50">
                <TableRow className="border-slate-800">
                  <TableHead className="text-slate-300">Algorithme</TableHead>
                  <TableHead className="text-slate-300">Accuracy</TableHead>
                  <TableHead className="text-slate-300">Précision</TableHead>
                  <TableHead className="text-slate-300">Rappel</TableHead>
                  <TableHead className="text-slate-300">F1 Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {modelData?.models?.map((model: any) => (
                  <TableRow key={model.model_name} className={`border-slate-800 ${model.is_best ? 'bg-sky-500/10' : ''}`}>
                    <TableCell className="font-medium text-white flex items-center gap-2">
                      {model.is_best && <Trophy className="h-4 w-4 text-amber-400" />}
                      {model.model_name}
                    </TableCell>
                    <TableCell className="text-slate-300">{(model.accuracy * 100).toFixed(2)}%</TableCell>
                    <TableCell className="text-slate-300">{(model.precision * 100).toFixed(2)}%</TableCell>
                    <TableCell className="text-slate-300">{(model.recall * 100).toFixed(2)}%</TableCell>
                    <TableCell className={`font-bold ${model.is_best ? 'text-sky-400' : 'text-slate-300'}`}>
                      {(model.f1_score * 100).toFixed(2)}%
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-indigo-400" />
              Modèle en Production
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center space-y-4 pt-4 pb-6">
            <div className="h-20 w-20 rounded-full bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
              <Trophy className="h-10 w-10 text-amber-400" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-white">
                {modelData?.best_model || "N/A"}
              </h3>
              <p className="text-slate-400 mt-1 text-xs">Sélectionné automatiquement</p>
            </div>
            {(() => {
              const best = modelData?.models?.find((m: any) => m.is_best);
              return best ? (
                <div className="w-full space-y-2 text-sm border-t border-slate-800 pt-4">
                  <div className="flex justify-between text-slate-400">
                    <span>Accuracy</span>
                    <span className="text-white font-semibold">{(best.accuracy * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>F1 Score</span>
                    <span className="text-sky-400 font-bold">{(best.f1_score * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Version</span>
                    <span className="text-white font-semibold">v1.0.0</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Entraîné le</span>
                    <span className="text-white font-semibold text-xs">
                      {best.training_date
                        ? new Date(best.training_date).toLocaleDateString("fr-FR", { day:"2-digit", month:"2-digit", year:"numeric" })
                        : "N/A"}
                    </span>
                  </div>
                </div>
              ) : null;
            })()}
            <div className="flex gap-2">
              <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">Actif</Badge>
              <Badge className="bg-sky-500/10 text-sky-400 border-sky-500/20">Production</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-emerald-400" />
            Explicabilité SHAP : Importance des Variables
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <HelpCircle className="h-4 w-4 text-slate-500 cursor-help" />
                </TooltipTrigger>
                <TooltipContent className="bg-slate-800 border-slate-700 text-slate-200 p-3 max-w-xs">
                  <p>Les valeurs de Shapley (SHAP) mesurent l'impact marginal de chaque variable sur la prédiction finale du modèle. Plus la barre est longue, plus la variable est déterminante pour l'IA.</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardTitle>
          <CardDescription className="text-slate-400">
            Top 10 des facteurs les plus influents dans la décision de l'IA (Modèle Actif).
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[400px]">
          {featureImportance ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureImportance} layout="vertical" margin={{ top: 5, right: 30, left: 160, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={true} vertical={false} />
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" width={150} tick={{ fill: '#cbd5e1', fontSize: 12 }} />
                <RechartsTooltip 
                  cursor={{fill: 'rgba(255,255,255,0.05)'}}
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                  formatter={(value) => [typeof value === 'number' ? value.toFixed(4) : String(value), 'Importance SHAP']}
                />
                <Bar dataKey="value" name="Importance Relative" fill="#10b981" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-500">
              Données d'importance des variables non disponibles.
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
