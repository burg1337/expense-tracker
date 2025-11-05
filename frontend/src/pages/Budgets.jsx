import React, { useState, useEffect } from 'react';
import { budgetsAPI, categoriesAPI } from '../services/api';

const Budgets = () => {
  const [budgets, setBudgets] = useState([]);
  const [budgetStatuses, setBudgetStatuses] = useState({});
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingBudget, setEditingBudget] = useState(null);
  const [formData, setFormData] = useState({
    category_id: '',
    amount: '',
    period: 'monthly',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
  });

  useEffect(() => {
    fetchCategories();
    fetchBudgets();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.getAll();
      setCategories(response.data.filter(cat => cat.type === 'expense'));
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchBudgets = async () => {
    setLoading(true);
    try {
      const response = await budgetsAPI.getAll();
      setBudgets(response.data);

      // Fetch status for each budget
      const statuses = {};
      for (const budget of response.data) {
        try {
          const statusRes = await budgetsAPI.getStatus(budget.id);
          statuses[budget.id] = statusRes.data;
        } catch (error) {
          console.error(`Failed to fetch status for budget ${budget.id}:`, error);
        }
      }
      setBudgetStatuses(statuses);
    } catch (error) {
      console.error('Failed to fetch budgets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingBudget) {
        await budgetsAPI.update(editingBudget.id, formData);
      } else {
        await budgetsAPI.create(formData);
      }
      setShowModal(false);
      resetForm();
      fetchBudgets();
    } catch (error) {
      console.error('Failed to save budget:', error);
      alert('Failed to save budget');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this budget?')) {
      try {
        await budgetsAPI.delete(id);
        fetchBudgets();
      } catch (error) {
        console.error('Failed to delete budget:', error);
      }
    }
  };

  const handleEdit = (budget) => {
    setEditingBudget(budget);
    setFormData({
      category_id: budget.category_id,
      amount: budget.amount,
      period: budget.period,
      start_date: budget.start_date,
      end_date: budget.end_date,
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      category_id: '',
      amount: '',
      period: 'monthly',
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
    });
    setEditingBudget(null);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const getProgressBarColor = (percentageUsed) => {
    if (percentageUsed >= 100) return '#f56565';
    if (percentageUsed >= 80) return '#ed8936';
    if (percentageUsed >= 60) return '#ecc94b';
    return '#48bb78';
  };

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Budgets</h2>
          <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
            Add Budget
          </button>
        </div>

        {loading ? (
          <div className="loading">Loading budgets...</div>
        ) : budgets.length === 0 ? (
          <div className="text-center">No budgets found. Create one to get started!</div>
        ) : (
          <div>
            {budgets.map((budget) => {
              const category = categories.find(c => c.id === budget.category_id);
              const status = budgetStatuses[budget.id];

              return (
                <div key={budget.id} style={{ marginBottom: '1.5rem', padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <div>
                      <h4 style={{ margin: 0, marginBottom: '0.25rem' }}>{category?.name || 'Unknown Category'}</h4>
                      <div style={{ fontSize: '0.875rem', color: '#718096' }}>
                        {budget.period.charAt(0).toUpperCase() + budget.period.slice(1)} Budget
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: '600' }}>
                        ${status?.spent?.toFixed(2) || '0.00'} / ${budget.amount.toFixed(2)}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#718096' }}>
                        ${status?.remaining?.toFixed(2) || budget.amount.toFixed(2)} remaining
                      </div>
                    </div>
                  </div>

                  {status && (
                    <div style={{ marginBottom: '0.5rem' }}>
                      <div style={{ height: '20px', background: '#e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${Math.min(status.percentage_used, 100)}%`,
                            background: getProgressBarColor(status.percentage_used),
                            transition: 'width 0.3s ease',
                          }}
                        />
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#718096', marginTop: '0.25rem' }}>
                        {status.percentage_used.toFixed(1)}% used
                        {status.is_exceeded && <span style={{ color: '#f56565', marginLeft: '0.5rem' }}>⚠️ Budget Exceeded!</span>}
                      </div>
                    </div>
                  )}

                  <div style={{ fontSize: '0.875rem', color: '#718096', marginBottom: '0.5rem' }}>
                    Period: {budget.start_date} to {budget.end_date}
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-secondary" onClick={() => handleEdit(budget)}>
                      Edit
                    </button>
                    <button className="btn btn-danger" onClick={() => handleDelete(budget.id)}>
                      Delete
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{editingBudget ? 'Edit Budget' : 'Add Budget'}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select name="category_id" className="form-select" value={formData.category_id} onChange={handleChange} required>
                  <option value="">Select a category</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Budget Amount</label>
                <input
                  type="number"
                  name="amount"
                  className="form-input"
                  value={formData.amount}
                  onChange={handleChange}
                  step="0.01"
                  min="0"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Period</label>
                <select name="period" className="form-select" value={formData.period} onChange={handleChange} required>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Start Date</label>
                <input
                  type="date"
                  name="start_date"
                  className="form-input"
                  value={formData.start_date}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">End Date</label>
                <input
                  type="date"
                  name="end_date"
                  className="form-input"
                  value={formData.end_date}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingBudget ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budgets;
