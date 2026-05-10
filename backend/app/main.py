from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from typing import Dict
from .ocr_engine import OCREngine
from .evaluator import Evaluator

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task store
tasks: Dict[str, Dict] = {}

# Initialize engines (Lazy loading to avoid startup delay if needed, 
# but here we'll load them at startup for simplicity in this prototype)
ocr_engine = None
evaluator = None

def get_engines():
    global ocr_engine, evaluator
    if ocr_engine is None:
        ocr_engine = OCREngine()
    if evaluator is None:
        evaluator = Evaluator()
    return ocr_engine, evaluator

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_task(task_id: str, file_path: str, question: str, rubric: str):
    try:
        tasks[task_id]["status"] = "Processing OCR..."
        ocr, eval_engine = get_engines()
        
        extracted_text = ocr.process_document(file_path)
        
        tasks[task_id]["status"] = "Evaluating..."
        result = eval_engine.evaluate(extracted_text, question, rubric)
        
        tasks[task_id]["status"] = "Completed"
        tasks[task_id]["result"] = {
            "extracted_text": extracted_text,
            **result
        }
    except Exception as e:
        tasks[task_id]["status"] = "Failed"
        tasks[task_id]["error"] = str(e)
    finally:
        # Cleanup uploaded file if needed
        # os.remove(file_path)
        pass

@app.post("/upload")
async def upload_assignment(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    question: str = Form(...),
    rubric: str = Form(...)
):
    task_id = str(uuid.uuid4())
    file_ext = file.filename.split('.')[-1]
    file_path = os.path.join(UPLOAD_DIR, f"{task_id}.{file_ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    tasks[task_id] = {
        "status": "Queued",
        "filename": file.filename,
        "question": question,
        "rubric": rubric
    }
    
    background_tasks.add_task(process_task, task_id, file_path, question, rubric)
    
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

@app.get("/health")
async def health():
    return {"status": "ok"}
