import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';
import { useTheme } from '../context/ThemeContext';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

const formatDateLabel = (dateStr, period) => {
  if (period === 'year') {
    const [year, month] = dateStr.split('-');
    const date = new Date(year, month - 1);
    return date.toLocaleDateString('en-US', { month: 'short' });
  }
  const date = new Date(dateStr + 'T00:00:00');
  if (period === 'week') {
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
  }
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

const CustomTooltip = ({ active, payload, label, period }) => {
  if (active && payload && payload.length) {
    const item = payload[0];
    return (
      <div className="bg-white dark:bg-slate-800 px-4 py-3 shadow-lg rounded-lg border border-slate-200 dark:border-slate-700">
        <p className="font-medium text-slate-800 dark:text-slate-100">
          {formatDateLabel(label, period)}
        </p>
        <p className="text-slate-600 dark:text-slate-300">{formatCurrency(item.value)}</p>
      </div>
    );
  }
  return null;
};

const TimeSeriesChart = ({ data, isLoading, period }) => {
  const { theme } = useTheme();
  const total = data?.reduce((sum, item) => sum + item.total, 0) || 0;

  const gridColor = theme === 'dark' ? '#334155' : '#e2e8f0';
  const textColor = theme === 'dark' ? '#94a3b8' : '#64748b';

  if (isLoading) {
    return (
      <div className="h-80 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-indigo-600 dark:border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-80 flex flex-col items-center justify-center text-slate-500 dark:text-slate-400">
        <svg className="w-16 h-16 mb-4 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        <p>No data for this period</p>
        <p className="text-sm">Try selecting a different time period</p>
      </div>
    );
  }

  const chartData = data.map(item => ({
    date: item.date,
    total: item.total,
    label: formatDateLabel(item.date, period),
  }));

  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Spending Over Time</h2>
        <div className="text-right">
          <p className="text-sm text-slate-500 dark:text-slate-400">Total for Period</p>
          <p className="text-xl font-bold text-slate-800 dark:text-slate-100">{formatCurrency(total)}</p>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis
              dataKey="date"
              tickFormatter={(val) => formatDateLabel(val, period)}
              stroke={textColor}
              tick={{ fontSize: 12 }}
            />
            <YAxis
              tickFormatter={(val) => `$${val}`}
              stroke={textColor}
              tick={{ fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip period={period} />} isAnimationActive={false} />
            <Area
              type="monotone"
              dataKey="total"
              stroke="#6366f1"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorTotal)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default TimeSeriesChart;
