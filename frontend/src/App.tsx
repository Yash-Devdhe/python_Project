import { useMemo, useState } from 'react'
import './App.css'

interface Highlight {
	token: string
	score: number
}

interface ClassifyResponse {
	label: 'real' | 'fake' | 'unverified' | string
	confidence: number
	reasons: string[]
	highlights: Highlight[]
	model_version: string
	latency_ms: number
}

const API_BASE = (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000'

function confidenceColor(label: string) {
	switch (label) {
		case 'real':
			return '#16a34a' // green-600
		case 'fake':
			return '#dc2626' // red-600
		default:
			return '#d97706' // amber-600
	}
}

function App() {
	const [text, setText] = useState('')
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string | null>(null)
	const [result, setResult] = useState<ClassifyResponse | null>(null)

	const topHighlights = useMemo(() => {
		if (!result?.highlights) return [] as Highlight[]
		return [...result.highlights]
			.sort((a, b) => Math.abs(b.score) - Math.abs(a.score))
			.slice(0, 10)
	}, [result])

	async function onVerify() {
		setLoading(true)
		setError(null)
		setResult(null)
		try {
			const resp = await fetch(`${API_BASE}/classify`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ text })
			})
			if (!resp.ok) {
				const data = await resp.json().catch(() => ({}))
				throw new Error(data.detail || `Request failed: ${resp.status}`)
			}
			const data = (await resp.json()) as ClassifyResponse
			setResult(data)
		} catch (e: any) {
			setError(e?.message || 'Something went wrong')
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="container">
			<header className="header">
				<h1>Fake News Detector</h1>
				<p className="subtitle">Multimodal-ready NLP baseline with explanations</p>
			</header>

			<section className="card">
				<label htmlFor="news-text" className="label">Paste news text or claim</label>
				<textarea
					id="news-text"
					className="textarea"
					value={text}
					onChange={(e) => setText(e.target.value)}
					rows={8}
					placeholder="e.g., Scientists confirm water is dry in groundbreaking study"
				/>
				<div className="actions">
					<button className="button" onClick={onVerify} disabled={loading || text.trim().length === 0}>
						{loading ? 'Verifying…' : 'Verify'}
					</button>
				</div>
				{error && <div className="error">{error}</div>}
			</section>

			{result && (
				<section className="card">
					<div className="verdict">
						<span
							className="chip"
							style={{ backgroundColor: confidenceColor(result.label) }}
						>
							{result.label.toUpperCase()}
						</span>
						<div className="confidence">
							<div className="confidence-bar-bg">
								<div
									className="confidence-bar"
									style={{ width: `${Math.round(result.confidence * 100)}%`, backgroundColor: confidenceColor(result.label) }}
								/>
							</div>
							<span className="confidence-text">Confidence: {Math.round(result.confidence * 100)}%</span>
						</div>
					</div>
					{result.reasons?.length > 0 && (
						<ul className="reasons">
							{result.reasons.map((r, i) => (
								<li key={i}>{r}</li>
							))}
						</ul>
					)}

					{topHighlights.length > 0 && (
						<div className="highlights">
							<h3>Top cues</h3>
							<div className="tokens">
								{topHighlights.map((h, i) => {
									const intensity = Math.min(1, Math.abs(h.score) / 0.5)
									const bg = h.score >= 0 ? 'rgba(22,163,74,' + intensity + ')' : 'rgba(220,38,38,' + intensity + ')'
									return (
										<span key={i} className="token" style={{ backgroundColor: bg }}>
											{h.token}
										</span>
									)
								})}
							</div>
						</div>
					)}

					<div className="meta">
						<span>Model: {result.model_version}</span>
						<span>Latency: {result.latency_ms} ms</span>
					</div>
				</section>
			)}

			<footer className="footer">Made with FastAPI + React</footer>
		</div>
	)
}

export default App
