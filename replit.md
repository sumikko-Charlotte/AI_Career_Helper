# AI Career Helper Platform (职航)

## Overview
This is an AI-assisted career growth platform for university students. It helps with resume analysis, career planning, mock interviews, and job recommendations.

## Project Structure
- **frontend/**: Vue 3 + Vite frontend application
  - Uses Element Plus for UI components
  - Port: 5000 (development)
- **backend/**: Python FastAPI backend API
  - Port: 8000 (development)
  - Uses external MySQL database on Tencent Cloud

## Development Setup

### Frontend
- Framework: Vue 3 with Vite
- UI Library: Element Plus
- Package Manager: npm
- Run: `cd frontend && npm run dev`

### Backend
- Framework: FastAPI with Uvicorn
- Database: MySQL (Tencent Cloud TDSQL-C)
- AI: DeepSeek API integration
- Run: `cd backend && python -m uvicorn main:app --host localhost --port 8000 --reload`

## Workflows
1. **Frontend**: Runs Vite dev server on port 5000
2. **Backend API**: Runs FastAPI server on port 8000

## API Proxy
The Vite dev server proxies `/api` and `/static` requests to the backend at localhost:8000.

## Key Features
- User authentication (login/register)
- Resume analysis and generation
- AI mock interviews
- Career roadmap planning
- Job recommendations
- Admin dashboard

## Recent Changes
- Configured for Replit environment
- Updated API base URL to use Vite proxy
- Set frontend to port 5000 with all hosts allowed
