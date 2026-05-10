# Project: Handwritten Assignment Checking & Evaluation

## Role: Expert Machine Learning Engineer
I am acting as a Senior Machine Learning Engineer specializing in Computer Vision (OCR) and Natural Language Processing (LLM integration). My focus is on building a robust, scalable, and accurate system for digitizing handwritten assignments and evaluating them against specific rubrics using Large Language Models.

## Project Overview
This project aims to automate the grading/checking of handwritten student assignments. The pipeline involves:
1.  **Image Preprocessing**: Cleaning and preparing handwritten images/PDFs.
2.  **OCR (Optical Character Recognition)**: Converting handwriting to machine-readable text using models like TrOCR or EasyOCR.
3.  **Content Extraction & Structuring**: Organizing the transcribed text into logical segments (questions, answers).
4.  **LLM Evaluation**: Using LLMs (like Gemini, GPT, or Claude) to grade the content based on provided keys or rubrics.
5.  **Application Interface**: A user-friendly interface for uploading assignments and viewing results.

## Technical Roadmap

### Phase 1: Research & Analysis (Completed)
- Analyzed `nlp_project_notebook.ipynb` and extracted OCR (TrOCR) and LLM (Qwen) logic.

### Phase 2: System Design (Completed)
- Designed a FastAPI backend with modular OCR and Evaluation services.
- Designed a Next.js frontend with Tailwind CSS for a modern, responsive UI.

### Phase 3: Modular Implementation (Completed)
- **OCR Module**: Implemented `OCREngine` with preprocessing (CRAFT detection, deskewing, HPP segmentation).
- **Evaluation Module**: Implemented `Evaluator` for OCR correction and academic grading.
- **API Layer**: Created FastAPI endpoints for file uploads and status tracking.

### Phase 4: Frontend Development (Completed)
- Built a Next.js dashboard with upload forms and detailed result visualizations.

## How to Run the Application

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) CUDA-enabled GPU for faster inference.

### 1. Start the Backend
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload --port 8000
```
*Note: On first run, it will download TrOCR and Qwen models (~3-4 GB).*

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
The app will be available at `http://localhost:3000`.

## Guidelines & Constraints
- **Notebook Integrity**: `nlp_project_notebook.ipynb` remains untouched.
- **Code Quality**: Modular Python services and typed React components.
- **Performance**: Uses BackgroundTasks for long-running ML processes.
