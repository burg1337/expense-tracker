import React, { useState, useEffect } from 'react';
import { transactionsAPI, categoriesAPI } from '../services/api';
import { format } from 'date-fns';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [page, setPage] = useState(0);
  const [formData, setFormData] = useState({
    category_id: '',
    amount: '',
    description: '',
    type: 'expense',
    date: new Date().toISOString().split('T')[0],
  });

  useEffect(() => {
    fetchCategories();
    fetchTransactions();
  }, [activeTab, page]);

  const fetchCategories = async () => {
    try {
      const response = await categoriesAPI.getAll();
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const params = {
        skip: page * 50,
        limit: 50,
      };
      if (activeTab !== 'all') {
        params.type = activeTab;
      }
      const response = await transactionsAPI.getAll(params);
      setTransactions(response.data);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTransaction) {
        await transactionsAPI.update(editingTransaction.id, formData);
      } else {
        await transactionsAPI.create(formData);
      }
      setShowModal(false);
      resetForm();
      fetchTransactions();
    } catch (error) {
      console.error('Failed to save transaction:', error);
      alert('Failed to save transaction');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this transaction?')) {
      try {
        await transactionsAPI.delete(id);
        fetchTransactions();
      } catch (error) {
        console.error('Failed to delete transaction:', error);
      }
    }
  };

  const handleEdit = (transaction) => {
    setEditingTransaction(transaction);
    setFormData({
      category_id: transaction.category_id,
      amount: transaction.amount,
      description: transaction.description || '',
      type: transaction.type,
      date: transaction.date,
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      category_id: '',
      amount: '',
      description: '',
      type: 'expense',
      date: new Date().toISOString().split('T')[0],
    });
    setEditingTransaction(null);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Transactions</h2>
          <button className="btn btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>
            Add Transaction
          </button>
        </div>

        <div className="tabs">
          <button className={`tab ${activeTab === 'all' ? 'active' : ''}`} onClick={() => setActiveTab('all')}>
            All
          </button>
          <button className={`tab ${activeTab === 'expense' ? 'active' : ''}`} onClick={() => setActiveTab('expense')}>
            Expenses
          </button>
          <button className={`tab ${activeTab === 'income' ? 'active' : ''}`} onClick={() => setActiveTab('income')}>
            Income
          </button>
        </div>

        {loading ? (
          <div className="loading">Loading transactions...</div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Category</th>
                  <th>Description</th>
                  <th>Amount</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {transactions.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="text-center">No transactions found</td>
                  </tr>
                ) : (
                  transactions.map((transaction) => {
                    const category = categories.find(c => c.id === transaction.category_id);
                    return (
                      <tr key={transaction.id}>
                        <td>{transaction.date}</td>
                        <td>
                          <span style={{ textTransform: 'capitalize' }}>{transaction.type}</span>
                        </td>
                        <td>{category?.name || 'Unknown'}</td>
                        <td>{transaction.description || '-'}</td>
                        <td style={{ color: transaction.type === 'income' ? '#48bb78' : '#f56565' }}>
                          ${transaction.amount.toFixed(2)}
                        </td>
                        <td>
                          <button className="btn btn-secondary" onClick={() => handleEdit(transaction)} style={{ marginRight: '0.5rem' }}>
                            Edit
                          </button>
                          <button className="btn btn-danger" onClick={() => handleDelete(transaction.id)}>
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        )}

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem' }}>
          <button className="btn btn-secondary" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>
            Previous
          </button>
          <span>Page {page + 1}</span>
          <button className="btn btn-secondary" onClick={() => setPage(page + 1)} disabled={transactions.length < 50}>
            Next
          </button>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">{editingTransaction ? 'Edit Transaction' : 'Add Transaction'}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Type</label>
                <select name="type" className="form-select" value={formData.type} onChange={handleChange} required>
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select name="category_id" className="form-select" value={formData.category_id} onChange={handleChange} required>
                  <option value="">Select a category</option>
                  {categories
                    .filter(cat => cat.type === formData.type)
                    .map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Amount</label>
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
                <label className="form-label">Description</label>
                <input
                  type="text"
                  name="description"
                  className="form-input"
                  value={formData.description}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Date</label>
                <input
                  type="date"
                  name="date"
                  className="form-input"
                  value={formData.date}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingTransaction ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Transactions;
