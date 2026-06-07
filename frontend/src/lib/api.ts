import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8005/api";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Data API
export const getDashboardSummary = async () => {
  const res = await api.get("/analytics/summary");
  return res.data;
};

export const getScanners = async (params = {}) => {
  const res = await api.get("/data/scanners", { params });
  return res.data;
};

export const getScannerById = async (id: string) => {
  const res = await api.get(`/data/scanners/${id}`);
  return res.data;
};

// Analytics API
export const getRiskDistribution = async () => {
  const res = await api.get("/analytics/risk-distribution");
  return res.data;
};

export const getModuleDistribution = async () => {
  const res = await api.get("/analytics/modules");
  return res.data;
};

export const getCorrelations = async () => {
  const res = await api.get("/analytics/correlations");
  return res.data;
};

export const getAgeDistribution = async () => {
  const res = await api.get("/analytics/age-distribution");
  return res.data;
};

export const getRiskByAge = async () => {
  const res = await api.get("/analytics/risk-by-age");
  return res.data;
};

// Prediction API
export const predictRisk = async (data: any) => {
  const res = await api.post("/predict/risk", data);
  return res.data;
};

export const predictModule = async (data: any) => {
  const res = await api.post("/predict/module", data);
  return res.data;
};

export const getPredictionHistory = async (limit = 50) => {
  const res = await api.get("/predict/history", { params: { limit } });
  return res.data;
};

export const getShapExplanation = async (id: number, model = "random_forest") => {
  const res = await api.get(`/predict/${id}/shap`, { params: { model_name: model } });
  return res.data;
};

// Download PDF
export const downloadReport = async (id: number) => {
  window.open(`${API_URL}/predict/${id}/report.pdf`, "_blank");
};

// ML API (Admin)
export const trainModels = async () => {
  const res = await api.post("/ml/train");
  return res.data;
};

export const getModelComparison = async () => {
  const res = await api.get("/ml/models");
  return res.data;
};
