import React, { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0'];

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [spendingByCategory, setSpendingByCategory] = useState([]);
  const [monthlyTrend, setMonthlyTrend] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [summaryRes, spendingRes, trendRes] = await Promise.all([
        analyticsAPI.getSummary(),
        analyticsAPI.getSpendingByCategory(),
        analyticsAPI.getMonthlyTrend({ months: 6 }),
      ]);

      setSummary(summaryRes.data);
      setSpendingByCategory(spendingRes.data.data);
      setMonthlyTrend(trendRes.data.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Loading dashboard...</div></div>;
  }

  return (
    <div className="container">
      <h2 className="card-title mb-2">Financial Overview</h2>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Income</div>
          <div className="stat-value stat-positive">
            ${summary?.total_income?.toFixed(2) || '0.00'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Expenses</div>
          <div className="stat-value stat-negative">
            ${summary?.total_expenses?.toFixed(2) || '0.00'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Balance</div>
          <div className={`stat-value ${summary?.balance >= 0 ? 'stat-positive' : 'stat-negative'}`}>
            ${summary?.balance?.toFixed(2) || '0.00'}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Savings Rate</div>
          <div className="stat-value">
            {summary?.savings_rate?.toFixed(1) || '0.0'}%
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Spending by Category</h3>
        </div>
        {spendingByCategory.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={spendingByCategory}
                dataKey="total"
                nameKey="category_name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(entry) => `${entry.category_name}: $${entry.total.toFixed(2)}`}
              >
                {spendingByCategory.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center">No spending data available</div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Monthly Trend</h3>
        </div>
        {monthlyTrend.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="income" fill="#48bb78" name="Income" />
              <Bar dataKey="expense" fill="#f56565" name="Expenses" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center">No trend data available</div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
