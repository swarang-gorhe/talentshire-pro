# Environment Configuration Template

## Frontend Environment Variables (.env)
Create a file at the project root: `.env.local`

```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Talentshire
VITE_API_TIMEOUT=30000
VITE_ENABLE_DEBUG=true
```

## Backend Environment Variables (.env)
Create a file at `backend/.env`

```
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:Admin%40123@127.0.0.1:5432/talentshire
MONGODB_URL=mongodb://127.0.0.1:27017
MONGODB_DB_NAME=talentshire

# API Configuration
API_TITLE=Talentshire API
API_VERSION=1.0.0
DEBUG=True
CORS_ORIGINS=["http://localhost:8080", "http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

## Production Configuration

### PostgreSQL Production
```
DATABASE_URL=postgresql+asyncpg://prod_user:STRONG_PASSWORD@prod-host:5432/talentshire_prod
```

### MongoDB Production
```
MONGODB_URL=mongodb+srv://prod_user:STRONG_PASSWORD@prod-cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=talentshire_prod
```

### Security Production
```
SECRET_KEY=generate-strong-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=False
```

### CORS Production
```
CORS_ORIGINS=["https://yourdomain.com", "https://admin.yourdomain.com"]
```
