import os
import cv2
import numpy as np
import torch
from PIL import Image
from pdf2image import convert_from_path
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import easyocr
import re

class OCREngine:
    def __init__(self, model_path="microsoft/trocr-base-handwritten"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        self.processor = TrOCRProcessor.from_pretrained(model_path)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_path).to(self.device)
        self.model.eval()
        
        # EasyOCR reader for text detection (CRAFT)
        self.reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())

    def load_document(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            pages = convert_from_path(file_path, dpi=300)
            return pages
        else:
            return [Image.open(file_path).convert("RGB")]

    def crop_to_text_roi_dl(self, pil_image):
        img_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        results = self.reader.detect(img_cv)
        
        boxes = results[0] # List of boxes
        if not boxes:
            return pil_image

        all_coords = []
        for box in boxes:
            all_coords.append((box[0], box[2])) # xmin, ymin
            all_coords.append((box[1], box[3])) # xmax, ymax

        all_coords = np.array(all_coords)
        x_min, y_min = np.min(all_coords, axis=0)
        x_max, y_max = np.max(all_coords, axis=0)

        # Add margin
        h, w = img_cv.shape[:2]
        x_min = max(0, x_min - 50)
        y_min = max(0, y_min - 50)
        x_max = min(w, x_max + 50)
        y_max = min(h, y_max + 50)

        cropped_img = img_cv[int(y_min):int(y_max), int(x_min):int(x_max)]
        return Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))

    def deskew_text_image(self, image):
        if isinstance(image, Image.Image):
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    def segment_lines_hpp(self, pil_image):
        img_cv = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        img_cv = cv2.resize(img_cv, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        if np.median(gray) < 127:
            gray = cv2.bitwise_not(gray)
            img_cv = cv2.bitwise_not(img_cv)

        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 15
        )

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        thresh_clean = cv2.subtract(thresh, detected_lines)

        hpp = np.sum(thresh_clean, axis=1)
        
        # Simple peak detection for lines
        threshold = np.mean(hpp) * 0.5
        peaks = np.where(hpp > threshold)[0]
        
        if len(peaks) == 0:
            return []

        line_indices = []
        if len(peaks) > 0:
            start = peaks[0]
            for i in range(1, len(peaks)):
                if peaks[i] - peaks[i-1] > 10: # Min gap between lines
                    line_indices.append((start, peaks[i-1]))
                    start = peaks[i]
            line_indices.append((start, peaks[-1]))

        line_crops = []
        for (start, end) in line_indices:
            # Add small margin to each line
            start = max(0, start - 5)
            end = min(img_cv.shape[0], end + 5)
            line_img = img_cv[start:end, :]
            line_crops.append(Image.fromarray(cv2.cvtColor(line_img, cv2.COLOR_BGR2RGB)))

        return line_crops

    def extract_text_from_lines(self, line_images):
        full_text = []
        for line_img in line_images:
            pixel_values = self.processor(line_img, return_tensors="pt").pixel_values.to(self.device)
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            full_text.append(generated_text)
        
        return "\n".join(full_text)

    def process_document(self, file_path):
        pages = self.load_document(file_path)
        full_document_text = ""
        
        for page in pages:
            clean_page = self.crop_to_text_roi_dl(page)
            deskewed_cv = self.deskew_text_image(clean_page)
            deskewed_pil = Image.fromarray(cv2.cvtColor(deskewed_cv, cv2.COLOR_BGR2RGB))
            line_crops = self.segment_lines_hpp(deskewed_pil)
            
            if not line_crops:
                continue
                
            page_text = self.extract_text_from_lines(line_crops)
            full_document_text += page_text + "\n"
            
        return full_document_text.strip()
