# Railway Deployment Guide

This guide will help you deploy your Task Manager app to Railway with PostgreSQL database.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Repository

### 1.1 Environment Variables
Create a `.env.example` file in your repository:

```bash
# Database Configuration
DATABASE_URL=sqlite:///task_manager.db

# JWT Secret Key (change this in production)
SECRET_KEY=your-secret-key-change-this-in-production

# Environment
FLASK_ENV=development
```

### 1.2 Railway Configuration
The following files are already created:
- `railway.json` - Railway deployment configuration
- `Procfile` - Process configuration for Railway
- `requirements.txt` - Python dependencies

## Step 2: Deploy to Railway

### 2.1 Create New Project
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2.2 Add PostgreSQL Database
1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. Note the connection details

### 2.3 Configure Environment Variables
In your Railway project settings, add these environment variables:

```
DATABASE_URL=<PostgreSQL connection string from Railway>
SECRET_KEY=<Generate a secure random string>
FLASK_ENV=production
```

**To generate a secure SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### 2.4 Deploy
1. Railway will automatically detect your Python app
2. It will install dependencies from `requirements.txt`
3. It will use the `Procfile` to start your app
4. Your app will be available at the provided Railway URL

## Step 3: Verify Deployment

### 3.1 Test the API
Your app should be available at: `https://your-app-name.railway.app`

Test endpoints:
- `GET /` - Frontend
- `POST /api/auth/login` - Login
- `GET /api/tracks` - Get tracks (requires authentication)

### 3.2 Default Login Credentials
- **Email**: `rob.vandijk@example.com`
- **Password**: `password123`

## Step 4: Custom Domain (Optional)

1. In Railway dashboard, go to your service
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Configure DNS records as instructed

## Step 5: Monitoring and Logs

### 5.1 View Logs
- Go to your Railway project
- Click on your service
- View real-time logs in the "Deployments" tab

### 5.2 Monitor Performance
- Railway provides built-in monitoring
- Check the "Metrics" tab for performance data

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` environment variable
   - Check PostgreSQL service is running
   - Ensure database tables are created

2. **Build Failures**
   - Check `requirements.txt` for correct dependencies
   - Verify Python version compatibility
   - Check build logs for specific errors

3. **App Not Starting**
   - Verify `Procfile` syntax
   - Check environment variables
   - Review application logs

### Database Migration
If you need to reset the database:
1. Go to your PostgreSQL service in Railway
2. Click "Data" tab
3. Use the built-in query interface to drop/recreate tables
4. Restart your app to reinitialize data

## Security Considerations

1. **Change Default Credentials**: Update the default user password
2. **Secure SECRET_KEY**: Use a strong, random secret key
3. **Environment Variables**: Never commit sensitive data to Git
4. **HTTPS**: Railway provides HTTPS by default
5. **Database Access**: Limit database access to your app only

## Scaling

Railway automatically handles:
- Load balancing
- Auto-scaling based on traffic
- Database connection pooling
- SSL certificates

## Cost Optimization

- Railway offers a free tier with usage limits
- Monitor your usage in the dashboard
- Consider upgrading plans for production use

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Railway Status: [status.railway.app](https://status.railway.app)
