"use client";

import { useState, useEffect } from "react";
import UploadForm from "@/components/UploadForm";
import ResultView from "@/components/ResultView";

export default function Home() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (taskId && status?.status !== "Completed" && status?.status !== "Failed") {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://localhost:8000/status/${taskId}`);
          const data = await res.json();
          setStatus(data);
        } catch (error) {
          console.error("Error fetching status:", error);
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [taskId, status]);

  return (
    <main className="page-wrapper">
      <div className="header-container">
        <h1 className="main-title">AI Assignment Checker</h1>
        <p className="subtitle">Handwriting OCR & Expert LLM Evaluation</p>
      </div>

      {!taskId ? (
        <UploadForm onUploadSuccess={(id) => setTaskId(id)} />
      ) : (
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {status?.status !== "Completed" && status?.status !== "Failed" && (
            <div className="glass-card status-card">
              <svg className="status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
              <h2 className="status-text">Processing Assignment</h2>
              <p className="status-subtext">Task ID: {taskId}</p>
              <p className="status-subtext" style={{ color: 'var(--accent-color)', marginTop: '1rem', fontWeight: 600 }}>{status?.status || "Initializing..."}</p>
            </div>
          )}

          {status?.status === "Completed" && (
            <ResultView result={status.result} />
          )}

          {status?.status === "Failed" && (
            <div className="glass-card status-card">
              <svg className="status-icon failed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h2 className="status-text" style={{ color: 'var(--error-color)' }}>Error Processing Assignment</h2>
              <p className="error-message">{status.error}</p>
              <button 
                onClick={() => setTaskId(null)}
                className="btn-danger"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
