import React, { useState, useEffect, useCallback } from 'react';
import { getAllExpenses, getExpenseSummary } from '../services/expenseApi';
import { useTheme } from '../context/ThemeContext';
import FileUpload from './FileUpload';
import DonutChart from './DonutChart';
import ExpenseList from './ExpenseList';

const Dashboard = () => {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { theme, toggleTheme } = useTheme();

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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900" style={{ minWidth: '768px' }}>
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src="/acme-logo.svg" alt="Acme Expenses" className="w-10 h-10 rounded-lg" />
              <div>
                <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Acme Expenses</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">Track and visualize your spending</p>
              </div>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-600 dark:text-slate-300 transition-colors"
              aria-label="Toggle dark mode"
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400">
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
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
              <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Quick Stats</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-slate-600 dark:text-slate-300">Total Expenses</span>
                  <span className="text-2xl font-bold text-slate-800 dark:text-slate-100">{expenses.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600 dark:text-slate-300">Categories</span>
                  <span className="text-2xl font-bold text-slate-800 dark:text-slate-100">{summary.length}</span>
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
      <footer className="border-t border-slate-200 dark:border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-slate-500 dark:text-slate-400">
            Acme Expenses • Track and visualize your spending
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
