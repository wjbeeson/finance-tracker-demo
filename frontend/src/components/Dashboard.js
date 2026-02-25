import React, { useState, useEffect, useCallback } from 'react';
import { getAllExpenses, getExpenseSummary, getExpenseTimeSeries, getPeriodLabel } from '../services/expenseApi';
import { useTheme } from '../context/ThemeContext';
import FileUpload from './FileUpload';
import DonutChart from './DonutChart';
import TimeSeriesChart from './TimeSeriesChart';
import ExpenseList from './ExpenseList';

const GRAPH_TYPES = [
  { id: 'donut', label: 'Pie Chart' },
  { id: 'timeseries', label: 'Time Series' },
];

const PERIOD_OPTIONS = [
  { id: 'week', label: 'Week' },
  { id: 'month', label: 'Month' },
  { id: 'year', label: 'Year' },
];

const Dashboard = () => {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { theme, toggleTheme } = useTheme();

  const [graphType, setGraphType] = useState('donut');
  const [showGraphMenu, setShowGraphMenu] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [periodOffset, setPeriodOffset] = useState(0);
  const [periodLabel, setPeriodLabel] = useState('');
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [isTimeSeriesLoading, setIsTimeSeriesLoading] = useState(false);

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

  const fetchTimeSeries = useCallback(async (period, offset) => {
    setIsTimeSeriesLoading(true);
    try {
      const [data, label] = await Promise.all([
        getExpenseTimeSeries(period, offset),
        getPeriodLabel(period, offset),
      ]);
      setTimeSeriesData(data);
      setPeriodLabel(label);
    } catch (err) {
      console.error('Error fetching time series:', err);
      setTimeSeriesData([]);
      setPeriodLabel('');
    } finally {
      setIsTimeSeriesLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (graphType === 'timeseries') {
      fetchTimeSeries(selectedPeriod, periodOffset);
    }
  }, [graphType, selectedPeriod, periodOffset, fetchTimeSeries]);

  const handleUploadSuccess = () => {
    fetchData();
    if (graphType === 'timeseries') {
      fetchTimeSeries(selectedPeriod, periodOffset);
    }
  };

  const handleGraphTypeSelect = (type) => {
    setGraphType(type);
    setShowGraphMenu(false);
  };

  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
    setPeriodOffset(0);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 transition-colors" style={{ minWidth: '768px' }}>
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src="/acme-logo.svg" alt="Acme Expenses" className="w-10 h-10 rounded-lg" />
              <div>
                <h1 className="text-4xl font-bold text-slate-800 dark:text-slate-100">Acme Expenses</h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">Track and visualize your spending</p>
              </div>
            </div>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              aria-label="Toggle dark mode"
            >
              {theme === 'dark' ? (
                <svg className="w-5 h-5 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-colors">
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
            {/* Chart Container */}
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-colors">
              {/* Graph Controls */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {/* Graph Type Dropdown */}
                  <div className="relative">
                    <button
                      onClick={() => setShowGraphMenu(!showGraphMenu)}
                      className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-lg bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors"
                      aria-label="Select graph type"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      Graph
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {showGraphMenu && (
                      <div className="absolute top-full left-0 mt-1 w-44 bg-white dark:bg-slate-700 rounded-lg shadow-lg border border-slate-200 dark:border-slate-600 py-1 z-10">
                        {GRAPH_TYPES.map((type) => (
                          <button
                            key={type.id}
                            onClick={() => handleGraphTypeSelect(type.id)}
                            className={`w-full text-left px-4 py-2 text-sm transition-colors ${
                              graphType === type.id
                                ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-medium'
                                : 'text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-600'
                            }`}
                          >
                            {type.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Period Selector - only visible for time series */}
                  {graphType === 'timeseries' && (
                    <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-700 rounded-lg p-1">
                      {PERIOD_OPTIONS.map((option) => {
                        const isSelected = selectedPeriod === option.id;
                        return (
                          <button
                            key={option.id}
                            onClick={() => handlePeriodChange(option.id)}
                            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                              isSelected
                                ? 'bg-white dark:bg-slate-600 text-indigo-700 dark:text-indigo-300 shadow-sm'
                                : 'text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-slate-100'
                            }`}
                            aria-label={`Select ${option.label} period`}
                          >
                            {option.label}
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* Period Navigation */}
                  {graphType === 'timeseries' && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setPeriodOffset(prev => prev - 1)}
                        className="p-1.5 rounded-md text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
                        aria-label="Previous period"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                      </button>
                      <span className="text-sm font-medium text-slate-700 dark:text-slate-200 min-w-[140px] text-center">
                        {periodLabel}
                      </span>
                      <button
                        onClick={() => setPeriodOffset(prev => prev + 1)}
                        disabled={periodOffset >= 0}
                        className={`p-1.5 rounded-md transition-colors ${
                          periodOffset >= 0
                            ? 'text-slate-300 dark:text-slate-600 cursor-not-allowed'
                            : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-700 dark:hover:text-slate-200'
                        }`}
                        aria-label="Next period"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </button>
                      {periodOffset !== 0 && (
                        <button
                          onClick={() => setPeriodOffset(0)}
                          className="px-2 py-1 text-xs font-medium rounded-md bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors"
                        >
                          Today
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Chart Content */}
              {graphType === 'donut' ? (
                <DonutChart data={summary} isLoading={isLoading} inline />
              ) : (
                <TimeSeriesChart data={timeSeriesData} isLoading={isTimeSeriesLoading} period={selectedPeriod} />
              )}
            </div>

            <ExpenseList expenses={expenses} isLoading={isLoading} summary={summary} />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-700 mt-auto transition-colors">
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
