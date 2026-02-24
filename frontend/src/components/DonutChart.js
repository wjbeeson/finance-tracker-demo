import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { useTheme } from '../context/ThemeContext';

export const COLORS = [
  '#6366f1', // indigo-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#ef4444', // red-500
  '#8b5cf6', // violet-500
  '#06b6d4', // cyan-500
  '#ec4899', // pink-500
  '#64748b', // slate-500
  '#84cc16', // lime-500
  '#f97316', // orange-500
];

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

const CustomTooltip = ({ active, payload, total }) => {
  if (active && payload && payload.length) {
    const item = payload[0];
    const percentage = ((item.value / total) * 100).toFixed(1);
    return (
      <div className="bg-white dark:bg-slate-800 px-4 py-3 shadow-lg rounded-lg border border-slate-200 dark:border-slate-700">
        <p className="font-medium text-slate-800 dark:text-slate-100">{item.name}</p>
        <p className="text-slate-600 dark:text-slate-300">{formatCurrency(item.value)}</p>
        <p className="text-sm text-slate-500 dark:text-slate-400">{percentage}% of total</p>
      </div>
    );
  }
  return null;
};

const renderLegend = (props) => {
  const { payload } = props;
  return (
    <ul className="flex flex-wrap justify-center gap-4 mt-4">
      {payload.map((entry, index) => (
        <li key={`legend-${index}`} className="flex items-center gap-2">
          <span 
            className="w-3 h-3 rounded-full" 
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-sm text-slate-600 dark:text-slate-300">{entry.value}</span>
        </li>
      ))}
    </ul>
  );
};

const DonutChart = ({ data, isLoading }) => {
  const { theme } = useTheme();
  const total = data?.reduce((sum, item) => sum + parseFloat(item.total), 0) || 0;
  const strokeColor = theme === 'dark' ? '#1e293b' : 'white';

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-colors">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Spending by Category</h2>
        <div className="h-80 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-indigo-600 dark:border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-colors">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Spending by Category</h2>
        <div className="h-80 flex flex-col items-center justify-center text-slate-500 dark:text-slate-400">
          <svg className="w-16 h-16 mb-4 text-slate-300 dark:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
          </svg>
          <p>No expense data available</p>
          <p className="text-sm">Upload a CSV file to see your spending breakdown</p>
        </div>
      </div>
    );
  }

  const chartData = data.map(item => ({
    name: item.category,
    value: parseFloat(item.total),
  }));

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Spending by Category</h2>
        <div className="text-right">
          <p className="text-sm text-slate-500 dark:text-slate-400">Total Spending</p>
          <p className="text-xl font-bold text-slate-800 dark:text-slate-100">{formatCurrency(total)}</p>
        </div>
      </div>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="45%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={COLORS[index % COLORS.length]}
                  stroke={strokeColor}
                  strokeWidth={2}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip total={total} />} isAnimationActive={false} />
            <Legend content={renderLegend} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default DonutChart;
