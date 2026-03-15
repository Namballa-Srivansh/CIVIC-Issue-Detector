import { useState, useRef, useCallback } from 'react'
import './App.css'

const ISSUE_CONFIG = {
  Pothole: {
    icon: '🕳️',
    cssClass: 'pothole',
    description: 'Road surface damage detected. This can cause vehicle damage and safety hazards.',
  },
  'Pipeline Leakage': {
    icon: '💧',
    cssClass: 'pipeline-leakage',
    description: 'Water/gas pipeline leak detected. Immediate maintenance is recommended.',
  },
  Garbage: {
    icon: '🗑️',
    cssClass: 'garbage',
    description: 'Waste accumulation detected. Sanitation services should be notified.',
  },
  'No issue detected': {
    icon: '✅',
    cssClass: 'no-issue',
    description: 'No civic issues were detected in this image.',
  },
}

function App() {
  const [selectedImage, setSelectedImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileSelect = useCallback((file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file)
      setPreview(URL.createObjectURL(file))
      setResult(null)
      setError(null)
    }
  }, [])

  const handleInputChange = (e) => {
    if (e.target.files[0]) handleFileSelect(e.target.files[0])
  }

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true) }
  const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false) }
  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files[0]) handleFileSelect(e.dataTransfer.files[0])
  }

  const handleAnalyze = async () => {
    if (!selectedImage) return
    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('image', selectedImage)

    try {
      const res = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setResult(data)
      } else {
        setError(data.error || 'Something went wrong during analysis.')
      }
    } catch {
      setError('Cannot connect to the server. Make sure the backend is running on port 5000.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedImage(null)
    setPreview(null)
    setResult(null)
    setError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const config = result ? (ISSUE_CONFIG[result.label] || ISSUE_CONFIG['No issue detected']) : null

  return (
    <div className="app-wrapper">
      {/* ambient blobs */}
      <div className="ambient">
        <div className="blob blob-1" />
        <div className="blob blob-2" />
        <div className="blob blob-3" />
      </div>

      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="badge">
            <span className="dot" />
            AI-Powered Detection
          </div>
          <h1>
            <span className="line-1">Civic Issue</span>
            <br />
            <span className="line-2">Detector</span>
          </h1>
          <p>
            Upload a photo to instantly detect{' '}
            <span className="hl-amber">potholes</span>,{' '}
            <span className="hl-blue">pipeline leakages</span>, or{' '}
            <span className="hl-green">garbage</span> using advanced AI.
          </p>
        </header>

        <div className="main-grid">
          {/* Upload Card */}
          <div className="glass-card">
            <div className="card-title">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Upload Image
            </div>

            <div
              className={`drop-zone ${isDragging ? 'dragging' : ''} ${preview ? 'has-preview' : 'empty'}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input ref={fileInputRef} type="file" accept="image/*" onChange={handleInputChange} />

              {preview ? (
                <div className="preview-wrapper">
                  <img src={preview} alt="Preview" />
                  {loading && <div className="scan-overlay" />}
                </div>
              ) : (
                <div className="drop-placeholder">
                  <div className="drop-icon-box">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                    </svg>
                  </div>
                  <p className="primary">Drop your image here</p>
                  <p className="secondary">or click to browse files</p>
                  <p className="hint">Supports JPG, PNG, WEBP</p>
                </div>
              )}
            </div>

            <div className="btn-row">
              <button className="btn-analyze" onClick={handleAnalyze} disabled={!selectedImage || loading}>
                {loading ? (
                  <>
                    <svg className="spinner" fill="none" viewBox="0 0 24 24">
                      <circle opacity="0.25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path opacity="0.75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
                    </svg>
                    Analyze Image
                  </>
                )}
              </button>

              {selectedImage && (
                <button className="btn-reset" onClick={handleReset}>Reset</button>
              )}
            </div>
          </div>

          {/* Results Card */}
          <div className="glass-card results-card">
            <div className="card-title">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Detection Result
            </div>

            <div className="results-body">
              {loading ? (
                <div className="state-box">
                  <div className="loading-spinner" />
                  <p className="title" style={{ color: '#94a3b8' }}>Analyzing your image...</p>
                  <p className="subtitle">Running AI detection model</p>
                </div>
              ) : result ? (
                <div className="result-content">
                  <div className={`result-badge ${config.cssClass}`}>
                    <div className="emoji">{config.icon}</div>
                    <h3 className={config.cssClass}>{result.label}</h3>
                    <p className="desc">{config.description}</p>
                  </div>

                  <div className="confidence-box">
                    <div className="confidence-header">
                      <span className="label">Confidence</span>
                      <span className={`value ${config.cssClass}`}>{result.confidence}%</span>
                    </div>
                    <div className="confidence-track">
                      <div
                        className={`confidence-fill ${config.cssClass}`}
                        style={{ width: `${result.confidence}%` }}
                      />
                    </div>
                  </div>
                </div>
              ) : error ? (
                <div className="state-box">
                  <div className="state-icon-box error">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                    </svg>
                  </div>
                  <p className="title err">Analysis Failed</p>
                  <p className="subtitle">{error}</p>
                </div>
              ) : (
                <div className="state-box">
                  <div className="state-icon-box empty">
                    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.41a2.25 2.25 0 013.182 0l2.909 2.91m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                    </svg>
                  </div>
                  <p className="title" style={{ color: '#64748b' }}>No results yet</p>
                  <p className="subtitle">Upload an image and click analyze</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Info Cards */}
        <div className="info-cards">
          <div className="glass-card info-card">
            <span className="emoji">🕳️</span>
            <div>
              <h3 className="amber">Potholes</h3>
              <p className="desc">Detects road damage &amp; surface cracks</p>
            </div>
          </div>
          <div className="glass-card info-card">
            <span className="emoji">💧</span>
            <div>
              <h3 className="blue">Pipeline Leaks</h3>
              <p className="desc">Identifies water &amp; gas leakages</p>
            </div>
          </div>
          <div className="glass-card info-card">
            <span className="emoji">🗑️</span>
            <div>
              <h3 className="green">Garbage</h3>
              <p className="desc">Spots waste &amp; debris accumulation</p>
            </div>
          </div>
        </div>

        <footer className="footer">
          Civic Issue Detector &mdash; Powered by YOLO &amp; React
        </footer>
      </div>
    </div>
  )
}

export default App
