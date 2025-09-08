# Production-Ready Task Manager

A complete, full-stack task management application with tracks, goals, and tasks. Built with Flask backend and React frontend, ready for production deployment on Railway with PostgreSQL database.

## ✨ Features

- **Full CRUD Operations**: Create, read, update, and delete tracks, goals, and tasks
- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Database Support**: Works with both SQLite (development) and PostgreSQL (production)
- **Production Ready**: Configured for Railway deployment with proper security
- **Responsive UI**: Modern React frontend with beautiful design
- **Data Validation**: Input sanitization and validation for security

## 🚀 Quick Start (Development)

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run the Application
```bash
python3 app.py
```

### 3. Access the App
Open your browser to: **http://localhost:5000**

### 4. Login
- **Email**: `rob.vandijk@example.com`
- **Password**: `password123`

## ✅ What This Solves

### Single Domain
- Frontend and API both served from `localhost:5000`
- No CORS issues
- No cross-origin problems

### No Caching Issues
- All files served from same Flask server
- No CDN caching problems
- Immediate updates when restarted

### Simplified Architecture
```
Flask App (port 5000)
├── /api/auth/login     → API endpoints
├── /api/tracks         → API endpoints
├── /api/goals          → API endpoints
├── /api/tasks          → API endpoints
├── /                   → React frontend
└── /static/*           → Frontend assets
```

## 🔧 How It Works

1. **Flask serves the React app** at the root URL (`/`)
2. **API endpoints** are available at `/api/*`
3. **Static files** (CSS, JS) served from `/static/`
4. **Client-side routing** handled by fallback to React app
5. **Database** automatically initialized with your data

## 📁 File Structure

```
single-flask-app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── task_manager.db     # SQLite database (auto-created)
└── static/            # React frontend files
    ├── index.html
    ├── assets/
    └── ...
```

## 🎯 Benefits

- **No deployment complexity** - single file to run
- **No connectivity issues** - everything on same server
- **No caching problems** - direct file serving
- **Easy to debug** - all logs in one place
- **Simple to deploy** - just upload and run

## 🚀 Production Deployment

### Railway Deployment (Recommended)
This app is configured for easy deployment on Railway with PostgreSQL:

1. **Follow the detailed guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)
2. **Quick steps**:
   - Push code to GitHub
   - Connect to Railway
   - Add PostgreSQL database
   - Set environment variables
   - Deploy!

### Other Deployment Options

#### Docker
```dockerfile
FROM python:3.9
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

#### Traditional Hosting
- Upload the entire folder
- Install requirements: `pip install -r requirements.txt`
- Set environment variables
- Run with gunicorn: `gunicorn app:app --bind 0.0.0.0:5000`

## 📚 API Documentation

### Authentication
All API endpoints (except login) require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Endpoints

#### Authentication
- `POST /api/auth/login` - User login

#### Tracks
- `GET /api/tracks` - Get all tracks for user
- `POST /api/tracks` - Create new track
- `PUT /api/tracks/<id>` - Update track
- `DELETE /api/tracks/<id>` - Delete track

#### Goals
- `GET /api/goals?track_id=<id>` - Get goals for track
- `POST /api/goals` - Create new goal
- `PUT /api/goals/<id>` - Update goal
- `DELETE /api/goals/<id>` - Delete goal

#### Tasks
- `GET /api/tasks?goal_id=<id>` - Get tasks for goal
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

## 🔑 Pre-configured Data

The app automatically creates:
- Rob van Dijk user account
- 7 tracks with sample goals and tasks
- Complete database schema

No manual setup required!

## 🛡️ Security Features

- **Password Hashing**: bcrypt for secure password storage
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Email format, color format, and length validation
- **Input Sanitization**: Protection against XSS attacks
- **SQL Injection Protection**: Parameterized queries
- **CORS Configuration**: Proper cross-origin resource sharing

