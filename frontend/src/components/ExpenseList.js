import React, { useState, useMemo, useRef, useEffect } from 'react';
import { COLORS } from './DonutChart';

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};


const buildCategoryColorMap = (summary) => {
  const colorMap = {};
  if (summary && summary.length > 0) {
    summary.forEach((item, index) => {
      colorMap[item.category] = COLORS[index % COLORS.length];
    });
  }
  return colorMap;
};

const ExpenseList = ({ expenses, isLoading, summary }) => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [sortField, setSortField] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const categoryColorMap = useMemo(() => buildCategoryColorMap(summary), [summary]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setCategoryDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const categories = useMemo(() => {
    if (!expenses || expenses.length === 0) return [];
    const catMap = {};
    expenses.forEach((exp) => {
      if (!catMap[exp.category]) {
        catMap[exp.category] = { count: 0, total: 0 };
      }
      catMap[exp.category].count += 1;
      catMap[exp.category].total += parseFloat(exp.amount);
    });
    return Object.entries(catMap)
      .map(([name, { count, total }]) => ({ name, count, total }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [expenses]);

  const displayedExpenses = useMemo(() => {
    if (!expenses) return [];
    let filtered = selectedCategory
      ? expenses.filter((exp) => exp.category === selectedCategory)
      : [...expenses];
    filtered.sort((a, b) => {
      let cmp = 0;
      if (sortField === 'date') {
        cmp = new Date(a.date) - new Date(b.date);
      } else if (sortField === 'amount') {
        cmp = parseFloat(a.amount) - parseFloat(b.amount);
      } else if (sortField === 'description') {
        cmp = a.description.localeCompare(b.description);
      }
      return sortOrder === 'desc' ? -cmp : cmp;
    });
    return filtered;
  }, [expenses, selectedCategory, sortField, sortOrder]);

  const summaryTotal = useMemo(() => {
    return displayedExpenses.reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
  }, [displayedExpenses]);

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Expenses</h2>
        <div className="flex items-center justify-center h-48">
          <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!expenses || expenses.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-4">Expenses</h2>
        <div className="flex flex-col items-center justify-center h-48 text-slate-500">
          <svg className="w-12 h-12 mb-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p>No expenses recorded yet</p>
          <p className="text-sm">Upload a CSV file to get started</p>
        </div>
      </div>
    );
  }

  const getSortArrow = (field) => {
    if (sortField !== field) return '';
    return sortOrder === 'desc' ? ' ↓' : ' ↑';
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === 'desc' ? 'asc' : 'desc'));
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800">Expenses</h2>
        <span className="text-sm text-slate-500">
          {displayedExpenses.length} of {expenses.length} items
          {selectedCategory && (
            <> &bull; <span className="font-medium text-slate-700">{formatCurrency(summaryTotal)}</span></>
          )}
        </span>
      </div>

      {/* Expense table */}
      <div className="overflow-x-auto h-96 overflow-y-auto">
        <table className="w-full">
          <thead className="sticky top-0 bg-white z-10">
            <tr className="border-b border-slate-200">
              <th
                className="text-left py-3 px-2 text-sm font-medium text-slate-500 cursor-pointer select-none hover:text-indigo-600 transition-colors"
                onClick={() => handleSort('description')}
              >
                Description{getSortArrow('description')}
              </th>
              <th className="text-left py-3 px-2 text-sm font-medium text-slate-500 relative" ref={dropdownRef}>
                <button
                  className="inline-flex items-center gap-1 hover:text-indigo-600 transition-colors select-none"
                  onClick={() => setCategoryDropdownOpen((prev) => !prev)}
                >
                  Category
                  {selectedCategory ? (
                    <svg className="w-3.5 h-3.5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                  ) : (
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                </button>
                {categoryDropdownOpen && (
                  <div className="absolute left-0 top-full mt-1 bg-white border border-slate-200 rounded-lg shadow-lg py-1 min-w-[180px] z-20">
                    <button
                      onClick={() => {
                        setSelectedCategory(null);
                        setCategoryDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3 py-2 text-sm hover:bg-slate-50 transition-colors flex items-center justify-between ${
                        !selectedCategory ? 'text-indigo-600 font-medium' : 'text-slate-700'
                      }`}
                    >
                      All Categories
                      {!selectedCategory && (
                        <svg className="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </button>
                    <div className="border-t border-slate-100 my-1"></div>
                    {categories.map((cat) => (
                      <button
                        key={cat.name}
                        onClick={() => {
                          setSelectedCategory(cat.name);
                          setCategoryDropdownOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-slate-50 transition-colors flex items-center justify-between gap-3 ${
                          selectedCategory === cat.name ? 'text-indigo-600 font-medium' : 'text-slate-700'
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: categoryColorMap[cat.name] || '#94a3b8' }}></span>
                          {cat.name}
                          <span className="text-xs text-slate-400">({cat.count})</span>
                        </span>
                        {selectedCategory === cat.name && (
                          <svg className="w-4 h-4 text-indigo-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </th>
              <th
                className="text-left py-3 px-2 text-sm font-medium text-slate-500 cursor-pointer select-none hover:text-indigo-600 transition-colors"
                onClick={() => handleSort('date')}
              >
                Date{getSortArrow('date')}
              </th>
              <th
                className="text-right py-3 px-2 text-sm font-medium text-slate-500 cursor-pointer select-none hover:text-indigo-600 transition-colors"
                onClick={() => handleSort('amount')}
              >
                Amount{getSortArrow('amount')}
              </th>
            </tr>
          </thead>
          <tbody>
            {displayedExpenses.map((expense) => (
              <tr key={expense.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                <td className="py-3 px-2">
                  <span className="text-slate-800 font-medium">{expense.description}</span>
                </td>
                <td className="py-3 px-2">
                  <span
                    className="inline-flex px-2.5 py-1 rounded-full text-xs font-medium"
                    style={{
                      backgroundColor: categoryColorMap[expense.category]
                        ? `${categoryColorMap[expense.category]}20`
                        : '#f1f5f9',
                      color: categoryColorMap[expense.category] || '#64748b',
                    }}
                  >
                    {expense.category}
                  </span>
                </td>
                <td className="py-3 px-2 text-slate-600 text-sm">
                  {formatDate(expense.date)}
                </td>
                <td className="py-3 px-2 text-right">
                  <span className="text-slate-800 font-semibold">{formatCurrency(expense.amount)}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExpenseList;
