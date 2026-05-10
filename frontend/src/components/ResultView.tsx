"use client";

interface Result {
  extracted_text: string;
  corrected_text: string;
  score: number;
  feedback: string;
}

interface Props {
  result: Result;
}

export default function ResultView({ result }: Props) {
  return (
    <div className="results-container">
      {/* Transcription Side */}
      <div className="result-panel">
        <h3 className="panel-header">
          <svg className="panel-icon transcription" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Transcription
        </h3>
        
        <div className="text-box">
          <h4 className="text-box-label" style={{ color: 'var(--text-secondary)' }}>Raw OCR</h4>
          <div className="text-content" style={{ fontStyle: 'italic', opacity: 0.8 }}>
            {result.extracted_text || "No raw text available."}
          </div>
        </div>
        
        <div className="text-box" style={{ borderLeft: '3px solid var(--accent-color)' }}>
          <h4 className="text-box-label">LLM Corrected</h4>
          <div className="text-content">
            {result.corrected_text || "No corrected text available."}
          </div>
        </div>
      </div>

      {/* Evaluation Side */}
      <div className="result-panel" style={{ borderTop: '4px solid var(--success-color)' }}>
        <h3 className="panel-header">
          <svg className="panel-icon evaluation" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Expert Evaluation
        </h3>
        
        <div className="score-display">
          <span className="score-value">{result.score}</span>
          <span className="score-max">/ 10</span>
        </div>
        
        <div className="progress-bar-bg">
          <div 
            className="progress-bar-fill" 
            style={{ width: `${result.score * 10}%` }}
          ></div>
        </div>

        <div className="feedback-box">
          <h4 className="feedback-title">Examiner Feedback</h4>
          <div className="text-content" style={{ maxHeight: 'none', color: 'var(--text-primary)' }}>
            {result.feedback}
          </div>
        </div>
      </div>

      <div className="reset-btn-container" style={{ gridColumn: '1 / -1' }}>
        <button 
          onClick={() => window.location.reload()}
          className="btn-secondary"
        >
          Evaluate Another Assignment
        </button>
      </div>
    </div>
  );
}
