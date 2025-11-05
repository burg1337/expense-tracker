# Expense Tracker - Personal Finance Management System

A full-stack web application for tracking expenses, managing budgets, and analyzing personal finances. Built with FastAPI, React, PostgreSQL, and Redis.

## Features

### Core Functionality
- **User Authentication**: Secure JWT-based authentication system
- **Transaction Management**: Create, read, update, and delete income and expense transactions
- **Category Management**: Organize transactions with custom categories
- **Budget Tracking**: Set budgets and monitor spending against limits
- **Financial Analytics**: Visualize spending patterns with interactive charts
- **Pagination**: Efficient data loading for large transaction lists
- **Caching**: Redis-based caching for improved performance

### Technical Highlights
- RESTful API with comprehensive CRUD operations
- PostgreSQL database with SQLAlchemy ORM
- Pydantic models for robust data validation
- Redis caching for dashboard analytics
- Responsive React UI with modern styling
- Docker containerization for easy deployment
- Interactive charts using Recharts library

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **JWT**: Secure authentication tokens
- **Redis**: In-memory caching
- **Uvicorn**: ASGI server

### Frontend
- **React**: UI library
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Recharts**: Chart library
- **Vite**: Build tool and dev server

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Web server for production frontend

## Project Structure

```
expense-tracker/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuration, database, security
│   │   ├── models/        # SQLAlchemy database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # API endpoints
│   │   ├── utils/         # Helper functions, cache, dependencies
│   │   └── main.py        # FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── contexts/      # React context providers
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Installation & Setup

### Prerequisites
- Docker and Docker Compose installed
- Git

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd expense-tracker
```

2. Start all services with Docker Compose:
```bash
docker-compose up --build
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start PostgreSQL and Redis locally (or use Docker)

6. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

4. Access at http://localhost:3000

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation (Swagger UI).

### Main API Endpoints

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

#### Categories
- `GET /categories` - List all categories
- `POST /categories` - Create category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

#### Transactions
- `GET /transactions` - List transactions (with pagination)
- `POST /transactions` - Create transaction
- `PUT /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

#### Budgets
- `GET /budgets` - List all budgets
- `GET /budgets/{id}/status` - Get budget status with spending
- `POST /budgets` - Create budget
- `PUT /budgets/{id}` - Update budget
- `DELETE /budgets/{id}` - Delete budget

#### Analytics
- `GET /analytics/summary` - Financial summary
- `GET /analytics/spending-by-category` - Spending breakdown
- `GET /analytics/income-by-category` - Income breakdown
- `GET /analytics/monthly-trend` - Monthly trends

## Database Schema

### Users
- id (Primary Key)
- email (Unique)
- username (Unique)
- hashed_password
- created_at

### Categories
- id (Primary Key)
- name
- type (income/expense)
- user_id (Foreign Key)

### Transactions
- id (Primary Key)
- user_id (Foreign Key)
- category_id (Foreign Key)
- amount
- description
- type (income/expense)
- date
- created_at

### Budgets
- id (Primary Key)
- user_id (Foreign Key)
- category_id (Foreign Key)
- amount
- period (weekly/monthly/yearly)
- start_date
- end_date

## Usage Guide

### 1. Register an Account
Navigate to the registration page and create a new account with email, username, and password.

### 2. Create Categories
Before adding transactions, create categories for your income and expenses (e.g., Salary, Groceries, Rent).

### 3. Add Transactions
Record your income and expenses by selecting a category, entering the amount, and adding a description.

### 4. Set Budgets
Create budgets for expense categories to track your spending limits. The system will show:
- Total budget amount
- Amount spent
- Remaining budget
- Visual progress bar
- Alerts when budget is exceeded

### 5. View Dashboard
Monitor your financial health with:
- Total income, expenses, and balance
- Savings rate
- Spending breakdown by category (pie chart)
- Monthly income/expense trends (bar chart)

## Features Showcase

### JWT Authentication
Secure token-based authentication ensures user data privacy. Tokens are stored in localStorage and automatically included in API requests.

### Data Validation
Pydantic models validate all incoming data, ensuring data integrity and providing clear error messages.

### Pagination
Transaction lists support pagination with configurable page size, improving performance for users with many transactions.

### Caching
Redis caches analytics data for 5-10 minutes, significantly improving dashboard load times. Cache is automatically invalidated when data changes.

### Responsive Design
The UI works seamlessly on desktop, tablet, and mobile devices with a clean, modern interface.

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/expense_tracker
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
```

## Testing

### Manual Testing
1. Use the Swagger UI at http://localhost:8000/docs
2. Test authentication flow: register → login → access protected endpoints
3. Test CRUD operations for all resources
4. Verify pagination works with multiple pages of data
5. Check caching by monitoring API response times

### Database Migrations
The application automatically creates tables on startup. For production, consider using Alembic for migrations:

```bash
cd backend
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Deployment

### Production Considerations
1. Change `SECRET_KEY` to a strong random value
2. Use environment-specific `.env` files
3. Enable HTTPS
4. Set up proper CORS origins
5. Configure database backups
6. Monitor Redis memory usage
7. Set up logging and error tracking

### Docker Production Build
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.

## Contact

For questions or feedback, please open an issue on GitHub.

## Acknowledgments

- FastAPI documentation and examples
- React and Recharts communities
- SQLAlchemy and Pydantic teams

---

Built with ❤️ using FastAPI and React
