import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAllExpenses = async () => {
  const response = await api.get('/expenses');
  return response.data;
};

export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/expenses/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getExpenseSummary = async () => {
  const response = await api.get('/expenses/summary');
  return response.data;
};

export const getExpenseTimeSeries = async (period = 'month', offset = 0) => {
  const response = await api.get(`/expenses/timeseries?period=${period}&offset=${offset}`);
  return response.data;
};

export const getAvailablePeriods = async (offset = 0) => {
  const response = await api.get(`/expenses/periods?offset=${offset}`);
  return response.data;
};

export const getPeriodLabel = async (period = 'month', offset = 0) => {
  const response = await api.get(`/expenses/period-label?period=${period}&offset=${offset}`);
  return response.data.label;
};

export default api;
