"use client";

import { useState } from "react";
import { Microscope, Target, ArrowRight, Settings2, ShieldCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { motion, AnimatePresence } from "framer-motion";
import { predictModule } from "@/lib/api";

const riskLevels = ["Low", "Medium", "High"];

export default function ExpertModulePage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [formData, setFormData] = useState({
    Age: "",
    Maintenance_Cost: "",
    Downtime: "",
    Maintenance_Frequency: "",
    Failure_Event_Count: "",
    MTBF: "",
    Failure_Rate: "",
    Downtime_Per_Failure: "",
    Maintenance_Intensity: "",
    Historical_Risk_Index: "",
    Failure_Risk: "Medium"
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSelectChange = (value: string | null) => {
    setFormData({ ...formData, Failure_Risk: value ?? "Medium" });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await predictModule({ scanner_data: formData });
      setResult(res);
    } catch (error) {
      console.error("Prediction error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Microscope className="text-indigo-400 h-6 w-6" />
            Module Expert : Diagnostic Composant
          </h2>
          <p className="text-slate-400">Prédisez le composant spécifique (Affected_Module) qui risque de tomber en panne.</p>
        </div>
        <div className="bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full text-xs font-medium border border-indigo-500/30 flex items-center gap-2">
          <ShieldCheck className="h-3 w-3" />
          Niveau Expert (Random Forest)
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="glass-card">
          <CardHeader>
            <CardTitle>Données d'Entrée</CardTitle>
            <CardDescription className="text-slate-400">Saisissez les télémétries et le niveau de risque global.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="Age">Âge (années)</Label>
                  <Input id="Age" name="Age" type="number" step="1" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="Maintenance_Cost">Coût Maintenance (€)</Label>
                  <Input id="Maintenance_Cost" name="Maintenance_Cost" type="number" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="Failure_Event_Count">Nb. Pannes</Label>
                  <Input id="Failure_Event_Count" name="Failure_Event_Count" type="number" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="MTBF">MTBF</Label>
                  <Input id="MTBF" name="MTBF" type="number" step="0.1" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>

                <div className="space-y-2 col-span-2">
                  <Label htmlFor="Failure_Risk">Risque Global Prédit</Label>
                  <Select onValueChange={handleSelectChange} defaultValue="Medium">
                    <SelectTrigger className="bg-slate-900/50 border-slate-700 text-white">
                      <SelectValue placeholder="Niveau de risque" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-800 border-slate-700 text-white">
                      {riskLevels.map((r) => (
                        <SelectItem key={r} value={r}>{r}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button type="submit" disabled={loading} className="w-full bg-indigo-500 hover:bg-indigo-600 text-white mt-4">
                {loading ? "Calcul probabiliste en cours..." : "Isoler le Composant"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div>
          <AnimatePresence>
            {result ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="h-full"
              >
                <Card className="glass-card h-full border-indigo-500/50 shadow-[0_0_30px_rgba(99,102,241,0.15)] flex flex-col">
                  <CardHeader className="bg-indigo-500/10 border-b border-indigo-500/20 pb-6">
                    <CardTitle className="text-indigo-300 flex items-center justify-center gap-2 text-lg">
                      <Target className="h-5 w-5" />
                      Module Critique Identifié
                    </CardTitle>
                    <div className="text-center mt-6">
                      <div className="text-3xl font-bold text-white mb-2">{result.predicted_module}</div>
                      <div className="inline-flex items-center rounded-full border border-indigo-500/30 bg-indigo-500/20 px-3 py-1 text-sm font-medium text-indigo-300">
                        Probabilité Maximale
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="flex-1 pt-6 overflow-y-auto">
                    <h4 className="text-sm font-medium text-slate-300 mb-4 flex items-center gap-2">
                      <Settings2 className="h-4 w-4 text-slate-400" />
                      Répartition Probabiliste par Composant
                    </h4>
                    <div className="space-y-4">
                      {Object.entries(result.module_probabilities || {})
                        .sort(([,a]: any, [,b]: any) => b - a)
                        .map(([module, prob]: [string, any], index) => (
                          <div key={module} className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span className={index === 0 ? "text-indigo-300 font-medium" : "text-slate-400"}>{module}</span>
                              <span className={index === 0 ? "text-indigo-300 font-medium" : "text-slate-400"}>{prob}%</span>
                            </div>
                            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                              <div 
                                className="h-full rounded-full transition-all duration-1000"
                                style={{ 
                                  width: `${prob}%`,
                                  backgroundColor: index === 0 ? '#6366f1' : '#475569'
                                }}
                              />
                            </div>
                          </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              <Card className="glass-card h-full flex items-center justify-center border-dashed border-slate-700 bg-slate-900/20">
                <div className="text-center p-8">
                  <div className="h-16 w-16 mx-auto rounded-full bg-slate-800 flex items-center justify-center mb-4">
                    <Microscope className="h-8 w-8 text-slate-500" />
                  </div>
                  <h3 className="text-slate-300 font-medium mb-2">En attente d'analyse</h3>
                  <p className="text-sm text-slate-500">Le module expert utilise un algorithme Random Forest pour déterminer quel composant matériel est le plus susceptible de nécessiter une intervention.</p>
                </div>
              </Card>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
