import React, { useState, useEffect, useCallback } from 'react';
import { getAllExpenses, getExpenseSummary } from '../services/expenseApi';
import FileUpload from './FileUpload';
import DonutChart from './DonutChart';
import ExpenseList from './ExpenseList';

const Dashboard = () => {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const [expensesData, summaryData] = await Promise.all([
        getAllExpenses(),
        getExpenseSummary(),
      ]);
      setExpenses(expensesData);
      setSummary(summaryData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load expense data. Please make sure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleUploadSuccess = () => {
    fetchData();
  };

  return (
    <div className="min-h-screen bg-slate-50" style={{ minWidth: '768px' }}>
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <img src="/acme-logo.svg" alt="Acme Expenses" className="w-10 h-10 rounded-lg" />
            <div>
              <h1 className="text-2xl font-bold text-slate-800">Acme Expenses</h1>
              <p className="text-sm text-slate-500">Track and visualize your spending</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload & Chart */}
          <div className="lg:col-span-1 space-y-6">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
            
            {/* Quick Stats */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h2 className="text-lg font-semibold text-slate-800 mb-4">Quick Stats</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Total Expenses</span>
                  <span className="text-2xl font-bold text-slate-800">{expenses.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600">Categories</span>
                  <span className="text-2xl font-bold text-slate-800">{summary.length}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Chart & List */}
          <div className="lg:col-span-2 space-y-6">
            <DonutChart data={summary} isLoading={isLoading} />
            <ExpenseList expenses={expenses} isLoading={isLoading} summary={summary} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-slate-500">
            Acme Expenses • Track and visualize your spending
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
