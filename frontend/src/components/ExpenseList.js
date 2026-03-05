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

const ExpenseList = ({ expenses, isLoading, summary, onDeleteExpense, onToggleExcluded }) => {
  const [selectedCategories, setSelectedCategories] = useState(new Set());
  const [sortField, setSortField] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [categoryDropdownOpen, setCategoryDropdownOpen] = useState(false);
  const [openMenuId, setOpenMenuId] = useState(null);
  const [expensePendingDelete, setExpensePendingDelete] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);
  const actionMenuRef = useRef(null);

  const categoryColorMap = useMemo(() => buildCategoryColorMap(summary), [summary]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setCategoryDropdownOpen(false);
      }
      if (actionMenuRef.current && !actionMenuRef.current.contains(event.target)) {
        setOpenMenuId(null);
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

  const isCategoryFilterActive = selectedCategories.size > 0 && selectedCategories.size < categories.length;
  const isFilterActive = isCategoryFilterActive || searchTerm.trim().length > 0;

  const displayedExpenses = useMemo(() => {
    if (!expenses) return [];
    let filtered = selectedCategories.size > 0 && selectedCategories.size < categories.length
      ? expenses.filter((exp) => selectedCategories.has(exp.category))
      : [...expenses];

    if (searchTerm.trim()) {
      const lowerSearch = searchTerm.trim().toLowerCase();
      filtered = filtered.filter((exp) =>
        exp.description.toLowerCase().includes(lowerSearch)
      );
    }

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
  }, [expenses, selectedCategories, categories.length, sortField, sortOrder, searchTerm]);

  const summaryTotal = useMemo(() => {
    return displayedExpenses.reduce((sum, exp) => sum + parseFloat(exp.amount), 0);
  }, [displayedExpenses]);

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 transition-colors">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Expenses</h2>
        <div className="flex items-center justify-center h-48">
          <div className="w-8 h-8 border-2 border-indigo-600 dark:border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!expenses || expenses.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 transition-colors">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-4">Expenses</h2>
        <div className="flex flex-col items-center justify-center h-48 text-slate-500 dark:text-slate-400">
          <svg className="w-12 h-12 mb-3 text-slate-300 dark:text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-6 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-slate-800 dark:text-slate-100">Expenses</h2>
        <span className="text-sm text-slate-500 dark:text-slate-400">
          {displayedExpenses.length} of {expenses.length} items
          {isFilterActive && (
            <> &bull; <span className="font-medium text-slate-700 dark:text-slate-300">{formatCurrency(summaryTotal)}</span></>
          )}
        </span>
      </div>

      {/* Expense table */}
      <div className="overflow-x-auto h-96 overflow-y-auto">
        <table className="w-full">
          <thead className="sticky top-0 bg-white dark:bg-slate-900 z-10">
            <tr className="border-b border-slate-200 dark:border-slate-800">
              <th
                className="text-left py-3 px-2 text-sm font-medium text-slate-500 dark:text-slate-400 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                onClick={() => handleSort('description')}
              >
                Description{getSortArrow('description')}
              </th>
              <th className="text-left py-3 px-2 text-sm font-medium text-slate-500 dark:text-slate-400 relative" ref={dropdownRef}>
                <button
                  className="inline-flex items-center gap-1 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors select-none"
                  onClick={() => setCategoryDropdownOpen((prev) => !prev)}
                >
                  Category
                  {isCategoryFilterActive ? (
                    <svg className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                  ) : (
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  )}
                </button>
                {categoryDropdownOpen && (
                  <div className="absolute left-0 top-full mt-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-lg py-1 min-w-[180px] z-20">
                    <button
                      onClick={() => {
                        setSelectedCategories(new Set(categories.map((c) => c.name)));
                      }}
                      className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-slate-700 dark:text-slate-300"
                    >
                      Select All
                    </button>
                    <button
                      onClick={() => {
                        setSelectedCategories(new Set());
                      }}
                      className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-slate-700 dark:text-slate-300"
                    >
                      Unselect All
                    </button>
                    <div className="border-t border-slate-100 dark:border-slate-800 my-1"></div>
                    {categories.map((cat) => (
                      <button
                        key={cat.name}
                        onClick={() => {
                          setSelectedCategories((prev) => {
                            const next = new Set(prev);
                            if (next.has(cat.name)) {
                              next.delete(cat.name);
                            } else {
                              next.add(cat.name);
                            }
                            return next;
                          });
                        }}
                        className={`w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors flex items-center justify-between gap-3 ${
                          selectedCategories.has(cat.name) ? 'text-indigo-600 dark:text-indigo-400 font-medium' : 'text-slate-700 dark:text-slate-300'
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: categoryColorMap[cat.name] || '#94a3b8' }}></span>
                          {cat.name}
                          <span className="text-xs text-slate-400 dark:text-slate-500">({cat.count})</span>
                        </span>
                        {selectedCategories.has(cat.name) && (
                          <svg className="w-4 h-4 text-indigo-600 dark:text-indigo-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </th>
              <th
                className="text-left py-3 px-2 text-sm font-medium text-slate-500 dark:text-slate-400 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                onClick={() => handleSort('date')}
              >
                Date{getSortArrow('date')}
              </th>
              <th
                className="text-right py-3 px-2 text-sm font-medium text-slate-500 dark:text-slate-400 cursor-pointer select-none hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
                onClick={() => handleSort('amount')}
              >
                Amount{getSortArrow('amount')}
              </th>
              <th className="w-10 py-3 px-2"></th>
            </tr>
          </thead>
          <tbody>
            {displayedExpenses.map((expense) => (
              <tr key={expense.id} className={`border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors ${expense.excluded ? 'opacity-50' : ''}`}>
                <td className="py-3 px-2">
                  <span className={`text-slate-800 dark:text-slate-100 font-medium ${expense.excluded ? 'line-through' : ''}`}>{expense.description}</span>
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
                <td className="py-3 px-2 text-slate-600 dark:text-slate-300 text-sm">
                  {formatDate(expense.date)}
                </td>
                <td className="py-3 px-2 text-right">
                  <span className={`text-slate-800 dark:text-slate-100 font-semibold ${expense.excluded ? 'line-through' : ''}`}>{formatCurrency(expense.amount)}</span>
                </td>
                <td className="py-3 px-2 text-right relative" ref={openMenuId === expense.id ? actionMenuRef : null}>
                  <button
                    onClick={() => setOpenMenuId(openMenuId === expense.id ? null : expense.id)}
                    className="p-1 rounded-md text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                    </svg>
                  </button>
                  {openMenuId === expense.id && (
                    <div className="absolute right-0 top-full mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg py-1 z-30 min-w-[200px]">
                      <button
                        onClick={() => { onToggleExcluded(expense.id, !expense.excluded); setOpenMenuId(null); }}
                        className="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors flex items-center gap-2"
                      >
                        {expense.excluded ? (
                          <>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                            Include in calculations
                          </>
                        ) : (
                          <>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                            Exclude from calculations
                          </>
                        )}
                      </button>
                      <div className="border-t border-slate-100 dark:border-slate-700 my-1"></div>
                      <button
                        onClick={() => { setExpensePendingDelete(expense); setOpenMenuId(null); }}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                        Delete
                      </button>
                    </div>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Confirmation modal */}
      {expensePendingDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 mb-2">Delete Expense?</h3>
            <p className="text-slate-600 dark:text-slate-300 text-sm mb-6">
              Are you sure you want to delete this expense? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setExpensePendingDelete(null)}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600 dark:text-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => { onDeleteExpense(expensePendingDelete.id); setExpensePendingDelete(null); }}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-red-600 hover:bg-red-700 text-white transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExpenseList;
