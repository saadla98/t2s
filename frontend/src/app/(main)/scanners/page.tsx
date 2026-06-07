"use client";

import { useEffect, useState } from "react";
import { Search, ActivitySquare, AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getScanners } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export default function ScannersPage() {
  const [scanners, setScanners] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchScanners = async () => {
      try {
        setLoading(true);
        const res = await getScanners({ limit: 100, search: searchTerm });
        setScanners(res.scanners);
        setTotal(res.total);
      } catch (error) {
        console.error("Error fetching scanners:", error);
      } finally {
        setLoading(false);
      }
    };
    
    // Debounce search
    const timer = setTimeout(() => {
      fetchScanners();
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "Low":
        return <Badge className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20"><CheckCircle2 className="w-3 h-3 mr-1"/> Faible</Badge>;
      case "Medium":
        return <Badge className="bg-amber-500/10 text-amber-400 border-amber-500/20"><AlertTriangle className="w-3 h-3 mr-1"/> Modéré</Badge>;
      case "High":
        return <Badge className="bg-red-500/10 text-red-400 border-red-500/20"><ShieldAlert className="w-3 h-3 mr-1"/> Élevé</Badge>;
      default:
        return <Badge variant="outline">{risk}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Parc Scanners CT</h2>
          <p className="text-slate-400">Gérez et consultez l'historique de tous les équipements supervisés.</p>
        </div>
        
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500" />
          <Input
            type="search"
            placeholder="Rechercher par ID, modèle..."
            className="w-full bg-slate-900/50 border-slate-700 text-white pl-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <Card className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-slate-900/80">
              <TableRow className="border-slate-800 hover:bg-transparent">
                <TableHead className="text-slate-300">ID Scanner</TableHead>
                <TableHead className="text-slate-300">Modèle</TableHead>
                <TableHead className="text-slate-300">Âge</TableHead>
                <TableHead className="text-slate-300">Temps d'Arrêt</TableHead>
                <TableHead className="text-slate-300">Coût Maint.</TableHead>
                <TableHead className="text-slate-300">Module Critique</TableHead>
                <TableHead className="text-slate-300 text-right">Niveau de Risque</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-10 text-slate-400">
                    Chargement des scanners...
                  </TableCell>
                </TableRow>
              ) : scanners.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-10 text-slate-400">
                    Aucun scanner trouvé.
                  </TableCell>
                </TableRow>
              ) : (
                scanners.map((scanner) => (
                  <TableRow key={scanner.id} className="border-slate-800 hover:bg-slate-800/50 transition-colors">
                    <TableCell className="font-medium text-white flex items-center gap-2">
                      <ActivitySquare className="h-4 w-4 text-sky-400" />
                      {scanner.device_id}
                    </TableCell>
                    <TableCell className="text-slate-300">{scanner.model || "GE Optima 540"}</TableCell>
                    <TableCell className="text-slate-300">{scanner.age} ans</TableCell>
                    <TableCell className="text-slate-300">{scanner.downtime} jours</TableCell>
                    <TableCell className="text-slate-300">{formatCurrency(scanner.maintenance_cost)}</TableCell>
                    <TableCell className="text-slate-300">{scanner.affected_module || "N/A"}</TableCell>
                    <TableCell className="text-right">
                      {getRiskBadge(scanner.failure_risk)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-right">
          Affichage de {scanners.length} sur {total} scanners
        </div>
      </Card>
    </div>
  );
}
