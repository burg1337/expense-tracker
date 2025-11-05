import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/transactions', label: 'Transactions' },
    { path: '/budgets', label: 'Budgets' },
    { path: '/categories', label: 'Categories' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <h1 style={{ cursor: 'pointer' }} onClick={() => navigate('/dashboard')}>
          💰 Expense Tracker
        </h1>
        {user && (
          <>
            <div style={{ display: 'flex', gap: '1.5rem' }}>
              {navItems.map((item) => (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: location.pathname === item.path ? 'white' : 'rgba(255,255,255,0.8)',
                    cursor: 'pointer',
                    fontSize: '1rem',
                    fontWeight: location.pathname === item.path ? '600' : '400',
                    textDecoration: location.pathname === item.path ? 'underline' : 'none',
                  }}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <div className="navbar-user">
              <span>Hello, {user.username}!</span>
              <button className="btn btn-secondary" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
