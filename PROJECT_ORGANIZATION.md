# Project Organization

This project has been reorganized for better structure and maintainability.

## Folder Structure

### /research_paper
Contains all research paper versions and related documentation.

- **/final/** - Final publication-ready paper
  - Research_Paper_IPO_Madras_Enhanced_Complete.txt (⭐ USE THIS)
  
- **/drafts/** - Earlier versions and drafts
  - Research_Paper_IPO_Madras.txt (original)
  - Research_Paper_IPO_Madras_Enhanced.txt (partial)
  
- **/guides/** - Documentation about the paper
  - RESEARCH_PAPER_GUIDE.txt
  - RESEARCH_PAPER_IMPROVEMENTS.txt
  - HOW_TO_USE_ENHANCED_PAPER.txt

### /documentation
Project documentation and status reports.

- **/project_status/** - Status reports and test results
  - BACKEND_FIX_SUMMARY.txt
  - FINAL_PROJECT_STATUS_REPORT.txt
  - COMPREHENSIVE_PROJECT_STATUS_REPORT.md
  - COMPREHENSIVE_BACKEND_TEST.py
  - backend_test_results.json

### /research
Backtesting charts and analysis (UNCHANGED - all images preserved)

- 9 backtesting charts (bt_chart1-9.png)
- IPO analysis notebooks
- Research scripts and data

### /web
Web application (backend + frontend)

- **/backend/** - FastAPI backend with all fixed endpoints
- **/frontend/** - React frontend

### /core
Core configuration and services

### /data
Database files

### /docs
Historical project documentation

### /exports
Export files (Excel reports, etc.)

## Key Files in Root

- main_ultimate_final.py - Main Streamlit application
- README.md - Project overview
- .env - Environment variables (GROQ_API_KEY)

## Recent Changes

1. ✅ Fixed all backend API endpoints (100% operational)
2. ✅ Created enhanced research paper with clear equations and paragraphs
3. ✅ Organized project structure
4. ✅ All 9 backtesting charts preserved in research/
5. ✅ Complete documentation

## Getting Started

1. Backend: `cd web/backend && python -m uvicorn main:app --reload --port 8000`
2. Frontend: `cd web/frontend && npm start`
3. Streamlit: `python main_ultimate_final.py`
4. Research Paper: Open `research_paper/final/Research_Paper_IPO_Madras_Enhanced_Complete.txt`

## Repository

GitHub: https://github.com/Amanarun2907/Sarthak_Nivesh_Finance_Tool
