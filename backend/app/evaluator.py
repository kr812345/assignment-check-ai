import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re

class Evaluator:
    def __init__(self, model_id="Qwen/Qwen2.5-1.5B-Instruct"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )
        if self.device == "cpu":
            self.model = self.model.to(self.device)
            
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )

    def correct_ocr(self, raw_text):
        if not raw_text.strip():
            return ""
            
        # Basic cleaning
        cleaned_text = re.sub(r'(?m)^[^a-zA-Z0-9]\s+', '', raw_text)
        cleaned_text = re.sub(r'(?m)^.{1,2}$', '', cleaned_text)
        
        prompt = f"""
You are an expert OCR correction engine.
Fix the spelling and grammar of this transcribed handwriting.
Fix visual typos like 'saw' to 'solve' or 'AIP' to 'AI?' based on context.
Do NOT add any extra conversational text. Output ONLY the corrected text.

RAW TEXT:
{cleaned_text.strip()}
"""
        messages = [
            {"role": "system", "content": "You output only corrected text, nothing else."},
            {"role": "user", "content": prompt}
        ]
        
        outputs = self.pipe(
            messages,
            max_new_tokens=500,
            temperature=0.1,
            do_sample=False
        )
        return outputs[0]["generated_text"][-1]["content"].strip()

    def evaluate(self, extracted_text, question, rubric):
        if not extracted_text or extracted_text.strip() == "":
            return {
                "score": 0,
                "feedback": "No text extracted. Cannot evaluate.",
                "corrected_text": ""
            }

        corrected_text = self.correct_ocr(extracted_text)
        
        prompt = f"""
You are an expert examiner.
STRICTLY evaluate the student's answer.

Question:
{question}

Rubric:
{rubric}

Student Answer:
{corrected_text}

Provide the evaluation in the following format:
Score: X/10
Feedback: Your explanation here
"""
        messages = [
            {"role": "system", "content": "You are a strict academic examiner."},
            {"role": "user", "content": prompt}
        ]
        
        outputs = self.pipe(
            messages,
            max_new_tokens=500,
            temperature=0.1,
            do_sample=False
        )
        
        response = outputs[0]["generated_text"][-1]["content"].strip()
        
        # Parse score and feedback
        score = 0
        feedback = response
        
        score_match = re.search(r"Score:\s*(\d+)/10", response)
        if score_match:
            score = int(score_match.group(1))
            
        feedback_match = re.search(r"Feedback:\s*(.*)", response, re.DOTALL)
        if feedback_match:
            feedback = feedback_match.group(1).strip()
            
        return {
            "score": score,
            "feedback": feedback,
            "corrected_text": corrected_text
        }
