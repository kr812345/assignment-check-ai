"use client";

import { useState } from "react";

interface Props {
  onUploadSuccess: (taskId: string) => void;
}

export default function UploadForm({ onUploadSuccess }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [rubric, setRubric] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !question || !rubric) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("question", question);
    formData.append("rubric", rubric);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      onUploadSuccess(data.task_id);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Failed to upload assignment. Please ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Upload Assignment (PDF or Image)</label>
          <label className="upload-dropzone">
            <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="file-name">{file ? file.name : "Click to browse or drag and drop"}</span>
            <span className="upload-text">PNG, JPG, PDF up to 10MB</span>
            <input 
              type="file" 
              className="file-input-hidden" 
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              accept="image/*,.pdf"
            />
          </label>
        </div>

        <div className="form-group">
          <label className="form-label">Assignment Question</label>
          <textarea
            required
            className="text-input"
            rows={3}
            placeholder="e.g., Explain the concept of Neural Networks..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Grading Rubric / Answer Key</label>
          <textarea
            required
            className="text-input"
            rows={4}
            placeholder="e.g., Student should mention: 1. Input layer, 2. Weights, 3. Activation function..."
            value={rubric}
            onChange={(e) => setRubric(e.target.value)}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !file}
          className="btn-primary"
        >
          {loading ? "Uploading..." : "Start Evaluation"}
        </button>
      </form>
    </div>
  );
}
