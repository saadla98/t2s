"use client";

import { useState } from "react";
import { Download, Stethoscope, AlertCircle, HeartPulse, FileText, Cpu } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { motion, AnimatePresence } from "framer-motion";
import { predictRisk, downloadReport, getScanners } from "@/lib/api";
import { useEffect } from "react";

export default function PredictionPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [scanners, setScanners] = useState<any[]>([]);
  const [selectedScannerId, setSelectedScannerId] = useState<string>("");
  const [formData, setFormData] = useState({
    Device_ID: "",
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
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  useEffect(() => {
    const fetchScanners = async () => {
      try {
        const res = await getScanners({ limit: 1000 }); // Fetch enough for the dropdown
        setScanners(res.scanners);
      } catch (error) {
        console.error("Error fetching scanners:", error);
      }
    };
    fetchScanners();
  }, []);

  const handleScannerSelect = (deviceId: string | null) => {
    if (!deviceId) return;
    setSelectedScannerId(deviceId);
    if (deviceId === "manual") {
      // Reset form
      setFormData({
        Device_ID: "", Age: "", Maintenance_Cost: "", Downtime: "",
        Maintenance_Frequency: "", Failure_Event_Count: "", MTBF: "",
        Failure_Rate: "", Downtime_Per_Failure: "", Maintenance_Intensity: "",
        Historical_Risk_Index: "",
      });
      return;
    }
    
    const scanner = scanners.find(s => s.device_id === deviceId);
    if (scanner) {
      setFormData({
        Device_ID: scanner.device_id,
        Age: scanner.age?.toString() || "",
        Maintenance_Cost: scanner.maintenance_cost?.toString() || "",
        Downtime: scanner.downtime?.toString() || "",
        Maintenance_Frequency: scanner.maintenance_frequency?.toString() || "",
        Failure_Event_Count: scanner.failure_event_count?.toString() || "",
        MTBF: scanner.mtbf?.toString() || "",
        Failure_Rate: scanner.failure_rate?.toString() || "",
        Downtime_Per_Failure: scanner.downtime_per_failure?.toString() || "",
        Maintenance_Intensity: scanner.maintenance_intensity?.toString() || "",
        Historical_Risk_Index: scanner.historical_risk_index?.toString() || "",
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await predictRisk({
        scanner_data: formData,
        technician_name: "Jean Dupont", // Mocked for UI
        technician_role: "technician",
      });
      setResult(res);
    } catch (error) {
      console.error("Prediction error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (result?.prediction_id) {
      downloadReport(result.prediction_id);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Stethoscope className="text-sky-400 h-6 w-6" />
            Prédiction du Risque de Panne
          </h2>
          <p className="text-slate-400">Saisissez les paramètres du scanner pour obtenir un diagnostic IA.</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="glass-card md:col-span-2">
          <CardHeader>
            <CardTitle>Paramètres du Scanner</CardTitle>
            <CardDescription className="text-slate-400">Veuillez remplir les données télémétriques et d'historique.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="mb-6 space-y-2 p-4 bg-slate-900/40 rounded-lg border border-slate-800">
              <Label htmlFor="scanner_select" className="text-sky-400">Remplissage Automatique (Optionnel)</Label>
              <Select onValueChange={handleScannerSelect} value={selectedScannerId}>
                <SelectTrigger id="scanner_select" className="bg-slate-800 border-slate-700 text-white">
                  <SelectValue placeholder="Sélectionnez un scanner existant ou saisissez manuellement" />
                </SelectTrigger>
                <SelectContent className="bg-slate-800 border-slate-700 text-white max-h-60">
                  <SelectItem value="manual">-- Saisie Manuelle --</SelectItem>
                  {scanners.map((s) => (
                    <SelectItem key={s.device_id} value={s.device_id}>
                      {s.device_id} - {s.model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="Device_ID">ID du Scanner</Label>
                  <Input id="Device_ID" name="Device_ID" value={formData.Device_ID} required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" placeholder="ex: CT-540-001" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="Age">Âge (années)</Label>
                  <Input id="Age" name="Age" value={formData.Age} type="number" step="1" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="Maintenance_Cost">Coût Maintenance (€)</Label>
                  <Input id="Maintenance_Cost" name="Maintenance_Cost" value={formData.Maintenance_Cost} type="number" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="Downtime">Temps d'arrêt (jours)</Label>
                  <Input id="Downtime" name="Downtime" value={formData.Downtime} type="number" step="0.1" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="Failure_Event_Count">Nb. de Pannes</Label>
                  <Input id="Failure_Event_Count" name="Failure_Event_Count" value={formData.Failure_Event_Count} type="number" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="MTBF">MTBF (jours)</Label>
                  <Input id="MTBF" name="MTBF" value={formData.MTBF} type="number" step="0.1" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="Failure_Rate">Taux de Panne</Label>
                  <Input id="Failure_Rate" name="Failure_Rate" value={formData.Failure_Rate} type="number" step="0.001" required onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="Historical_Risk_Index">Indice de Risque Hist.</Label>
                  <Input id="Historical_Risk_Index" name="Historical_Risk_Index" value={formData.Historical_Risk_Index} type="number" step="0.01" onChange={handleChange} className="bg-slate-900/50 border-slate-700 text-white" />
                </div>

              </div>

              <Button type="submit" disabled={loading} className="w-full bg-sky-500 hover:bg-sky-600 text-white mt-6 h-12 text-lg">
                {loading ? "Analyse en cours..." : "Générer le Diagnostic IA"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="md:col-span-1">
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-6"
              >
                <Card className={`glass-card overflow-hidden border-t-4 ${
                  result.risk_level === 'High' ? 'border-t-red-500 shadow-[0_0_20px_rgba(239,68,68,0.2)]' : 
                  result.risk_level === 'Medium' ? 'border-t-amber-500 shadow-[0_0_20px_rgba(245,158,11,0.2)]' : 
                  'border-t-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.2)]'
                }`}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-center text-lg text-slate-300">Niveau de Risque IA</CardTitle>
                  </CardHeader>
                  <CardContent className="flex flex-col items-center">
                    <div className="text-4xl font-extrabold my-4 tracking-tight" style={{
                      color: result.risk_level === 'High' ? '#ef4444' : result.risk_level === 'Medium' ? '#f59e0b' : '#10b981'
                    }}>
                      {result.risk_level === 'High' ? 'ÉLEVÉ' : result.risk_level === 'Medium' ? 'MODÉRÉ' : 'FAIBLE'}
                    </div>

                    <div className="w-full space-y-3 mt-4">
                      {Object.entries(result.probabilities).map(([level, prob]: [string, any]) => (
                        <div key={level} className="space-y-1">
                          <div className="flex justify-between text-xs text-slate-400">
                            <span>{level === 'High' ? 'Élevé' : level === 'Medium' ? 'Modéré' : 'Faible'}</span>
                            <span>{Number(prob).toFixed(2)}%</span>
                          </div>
                          <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                            <div 
                              className="h-full rounded-full transition-all duration-1000"
                              style={{ 
                                width: `${prob}%`,
                                backgroundColor: level === 'High' ? '#ef4444' : level === 'Medium' ? '#f59e0b' : '#10b981'
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card className="glass-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <HeartPulse className="h-5 w-5 text-sky-400" />
                      Score de Santé
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-end gap-2">
                      <span className="text-5xl font-bold text-white">{result.health_score}</span>
                      <span className="text-slate-400 mb-1">/ 100</span>
                    </div>
                    <p className="text-sm text-slate-400 mt-2">Indicateur global de fiabilité de l'équipement.</p>
                  </CardContent>
                </Card>

                {result.predicted_module && (
                  <Card className="glass-card border border-sky-500/30 bg-sky-500/5">
                    <CardHeader className="pb-2">
                      <CardTitle className="flex items-center gap-2 text-lg">
                        <Cpu className="h-5 w-5 text-sky-400" />
                        Module Prédit par IA
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-base font-semibold text-white">{result.predicted_module}</span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30">IA Généré</span>
                      </div>
                      {result.module_probabilities && Object.keys(result.module_probabilities).length > 0 && (
                        <div className="space-y-1.5 max-h-40 overflow-y-auto pr-1">
                          {Object.entries(result.module_probabilities)
                            .sort(([, a], [, b]) => (b as number) - (a as number))
                            .slice(0, 4)
                            .map(([mod, prob]: [string, any]) => (
                              <div key={mod} className="space-y-0.5">
                                <div className="flex justify-between text-xs text-slate-400">
                                  <span className={mod === result.predicted_module ? "text-sky-300 font-medium" : ""}>{mod}</span>
                                  <span>{Number(prob).toFixed(1)}%</span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                                  <div
                                    className="h-full rounded-full transition-all duration-1000"
                                    style={{
                                      width: `${prob}%`,
                                      backgroundColor: mod === result.predicted_module ? '#38bdf8' : '#475569'
                                    }}
                                  />
                                </div>
                              </div>
                            ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}

                <Card className={`bg-${result.recommendation.color}-500/10 border border-${result.recommendation.color}-500/20`}>
                  <CardContent className="p-4 flex gap-3">
                    <div className="text-2xl mt-1">{result.recommendation.icon}</div>
                    <div>
                      <h4 className={`font-semibold text-${result.recommendation.color}-400 mb-1`}>
                        {result.recommendation.title}
                      </h4>
                      <p className="text-sm text-slate-300 leading-relaxed">
                        {result.recommendation.message}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Button onClick={handleDownload} variant="outline" className="w-full bg-slate-800/50 text-white border-slate-700 hover:bg-slate-800">
                  <FileText className="mr-2 h-4 w-4" />
                  Générer le Rapport PDF
                </Button>
              </motion.div>
            )}
          </AnimatePresence>

          {!result && !loading && (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 border border-dashed border-slate-700 rounded-xl bg-slate-900/20">
              <AlertCircle className="h-10 w-10 text-slate-600 mb-4" />
              <h3 className="text-slate-300 font-medium">Aucun résultat</h3>
              <p className="text-sm text-slate-500 mt-2">Remplissez le formulaire et générez le diagnostic pour voir l'analyse IA.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
