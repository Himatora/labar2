# Development Environment

This is a **self-contained** development environment. All files needed to run are in this folder.

## 🚀 Quick Start

```bash
# Navigate to dev folder
cd dev

# Start all services
docker-compose up -d --build

# Access application
# Frontend: http://localhost
# Backend API: http://localhost/api/
# Version Control: http://localhost/version-control/
```

## 📁 Structure

```
dev/
├── backend/            # Django backend
├── frontend/           # Vue.js frontend
├── nginx/              # Nginx configuration
├── version_control/    # Version control service
├── tutor/              # Django app module
├── docker-compose.yml  # All services
├── Dockerfile.backend  # Backend container
├── Dockerfile.nginx    # Frontend container
└── Jenkinsfile         # CI/CD pipeline
```

## 🐳 Services

- **Backend:** Port 8000
- **Nginx:** Port 80
- **Version Control:** Port 8001
- **Registry:** Port 5000

## 🔧 Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up -d --build
```

## ✅ Self-Contained

This folder contains everything needed to run independently. No need to reference parent directories.

