import React, { useState, useCallback } from 'react'

// ─── Types ──────────────────────────────────────────────────────────────
interface ParsedResume {
  text: string
  skills: string[]
  experience_years: number
  positions: Array<{ period: string; details: string }>
  education: string[]
  raw_sections: Record<string, string>
}

interface MatchResult {
  match_score: number
  strengths: string[]
  gaps: string[]
  missing_skills: string[]
  recommended_changes: string[]
  interview_questions: Array<{ category: string; question: string; hint: string }>
  preparation_plan: Array<{ day: number; focus: string; tasks: string[] }>
}

type Step = 1 | 2 | 3 | 4

// ─── API Functions ──────────────────────────────────────────────────────
const API_BASE = 'http://localhost:8000'

async function parseResume(file: File): Promise<{ resume_id: string; parsed: ParsedResume }> {
  const formData = new FormData()
  formData.append('file', file)
  const resp = await fetch(`${API_BASE}/parse-resume`, { method: 'POST', body: formData })
  if (!resp.ok) throw new Error('Ошибка парсинга резюме')
  return resp.json()
}

async function fetchVacancy(vacancyUrl: string): Promise<any> {
  const resp = await fetch(`${API_BASE}/vacancy/fetch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: vacancyUrl })
  })
  if (!resp.ok) throw new Error('Не удалось получить вакансию')
  return resp.json()
}

async function matchResume(resumeId: string, vacancyData: any): Promise<{ match_id: string; result: MatchResult }> {
  const resp = await fetch(`${API_BASE}/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_id: resumeId, vacancy_text: vacancyData.description, vacancy_skills: vacancyData.key_skills })
  })
  if (!resp.ok) throw new Error('Ошибка мэтчинга')
  return resp.json()
}

// ─── Components ─────────────────────────────────────────────────────────
function StepIndicator({ currentStep }: { currentStep: Step }) {
  const steps: Array<{ num: Step; title: string; desc: string }> = [
    { num: 1, title: 'Резюме', desc: 'Загрузить PDF/DOCX' },
    { num: 2, title: 'Вакансия', desc: 'Ссылка с HH.ru или текст' },
    { num: 3, title: 'Мэтчинг', desc: 'AI анализ соответствия' },
    { num: 4, title: 'Результат', desc: 'План подготовки' },
  ]

  return (
    <div className="steps">
      {steps.map((step, i) => (
        <div key={step.num} className={`step ${step.num < currentStep ? 'completed' : step.num === currentStep ? 'active' : ''}`}>
          <div className="step-number">{step.num}</div>
          <div className="step-title">{step.title}</div>
          <div className="step-desc">{step.desc}</div>
        </div>
      ))}
    </div>
  )
}

function FileUpload({ onFile, file, parsing, parsed }: {
  onFile: (f: File) => void
  file: File | null
  parsing: boolean
  parsed: ParsedResume | null
}) {
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) onFile(f)
  }, [onFile])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) onFile(f)
  }, [onFile])

  if (parsed) {
    return (
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">✅ Резюме распарсено</div>
            <div className="card-subtitle">{file?.name}</div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => onFile(null as any)}>Загрузить другое</button>
        </div>
        <div className="grid grid-2" style={{ marginTop: '1rem' }}>
          <div>
            <strong>Навыки ({parsed.skills.length}):</strong>
            <div style={{ marginTop: '0.5rem', display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
              {parsed.skills.slice(0, 20).map(s => <span key={s} className="badge badge-info">{s}</span>)}
              {parsed.skills.length > 20 && <span className="badge badge-neutral">+{parsed.skills.length - 20}</span>}
            </div>
          </div>
          <div>
            <strong>Опыт:</strong> {parsed.experience_years} лет
          </div>
          <div>
            <strong>Позиций:</strong> {parsed.positions.length}
          </div>
          <div>
            <strong>Образование:</strong> {parsed.education.length}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="file-upload" onDragOver={e => e.preventDefault()} onDrop={handleDrop}>
        <input type="file" id="resume-file" accept=".pdf,.docx,.doc" onChange={handleChange} disabled={parsing} />
        <label htmlFor="resume-file" style={{ cursor: 'pointer', display: 'block' }}>
          {parsing ? (
            <div className="loading"><div className="spinner"></div> Парсим резюме...</div>
          ) : (
            <>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📄</div>
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Перетащите резюме (PDF, DOCX) или нажмите</div>
              <div className="form-help">Макс. 10 МБ. Парсим навыки, опыт, позиции, образование.</div>
            </>
          )}
        </label>
      </div>
    </div>
  )
}

function VacancyInput({ onSubmit, loading, vacancy }: { onSubmit: (url: string) => void; loading: boolean; vacancy: any }) {
  const [url, setUrl] = useState('')

  if (vacancy) {
    return (
      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">✅ Вакансия загружена</div>
            <div className="card-subtitle">{vacancy.name} — {vacancy.company}</div>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => onSubmit('')}>Изменить</button>
        </div>
        <div style={{ marginTop: '1rem' }}>
          <div className="badge badge-info" style={{ marginBottom: '0.5rem' }}>{vacancy.experience}</div>
          <div className="badge badge-neutral" style={{ marginRight: '0.5rem' }}>{vacancy.salary_from || '—'} – {vacancy.salary_to || '—'} {vacancy.currency}</div>
          <div className="badge badge-neutral">{vacancy.employment}, {vacancy.schedule}</div>
          <div style={{ marginTop: '0.75rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            {vacancy.key_skills.slice(0, 10).map(s => <span key={s} className="badge badge-info" style={{ marginRight: '0.25rem' }}>{s}</span>)}
          </div>
        </div>
      </div>
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (url.trim()) onSubmit(url.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="form-group">
        <label className="form-label">Ссылка на вакансию HH.ru</label>
        <input
          type="url"
          className="form-input"
          placeholder="https://hh.ru/vacancy/12345678"
          value={url}
          onChange={e => setUrl(e.target.value)}
          disabled={loading}
        />
        <div className="form-help">Или вставьте описание вакансии вручную на следующем шаге</div>
      </div>
      <button type="submit" className="btn btn-primary" disabled={loading || !url.trim()} style={{ width: '100%' }}>
        {loading ? <><span className="spinner" style={{width:16,height:16}}></span> Загружаем... </> : 'Получить вакансию'}
      </button>
    </form>
  )
}

function MatchProgress({ onComplete }: { onComplete: (result: MatchResult) => void }) {
  const [stage, setStage] = useState<'embedding' | 'llm' | 'done'>('embedding')
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const steps = [
      { stage: 'embedding' as const, progress: 30, delay: 800 },
      { stage: 'llm' as const, progress: 80, delay: 2500 },
      { stage: 'done' as const, progress: 100, delay: 500 },
    ]
    let idx = 0
    const next = () => {
      if (idx >= steps.length) return
      const s = steps[idx]
      setStage(s.stage)
      setProgress(s.progress)
      setTimeout(() => { idx++; next() }, s.delay)
    }
    next()
  }, [])

  if (stage === 'done') {
    onComplete({} as MatchResult) // placeholder
    return null
  }

  return (
    <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
      <div className="loading" style={{ justifyContent: 'center', fontSize: '1.125rem' }}>
        <div className="spinner" style={{ width: 32, height: 32 }}></div>
        {stage === 'embedding' && 'Создаём эмбеддинги...'}
        {stage === 'llm' && 'Анализируем соответствие с GPT-4o...'}
      </div>
      <div className="progress-bar" style={{ marginTop: '1.5rem' }}>
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>
      <div style={{ marginTop: '0.75rem', color: 'var(--text-muted)' }}>{progress}%</div>
    </div>
  )
}

function ResultsView({ result, onRestart }: { result: MatchResult; onRestart: () => void }) {
  const tabs = [
    { id: 'score', label: 'Мэтч-скор' },
    { id: 'strengths', label: 'Сильные стороны' },
    { id: 'gaps', label: 'Пробелы' },
    { id: 'questions', label: 'Вопросы к собеседованию' },
    { id: 'plan', label: 'План подготовки' },
  ]
  const [activeTab, setActiveTab] = useState(tabs[0].id)

  const renderScore = () => (
    <div className="card" style={{ textAlign: 'center' }}>
      <div className="match-score" style={{ justifyContent: 'center', marginBottom: '1.5rem' }}>
        <div className="score-circle" style={{ '--score': result.match_score }}>
          <span className="score-value">{Math.round(result.match_score)}%</span>
        </div>
        <div>
          <div style={{ fontSize: '1.125rem', color: 'var(--text-muted)' }}>Соответствие вакансии</div>
          <div style={{ marginTop: '0.5rem' }}>
            <span className="badge badge-success">Сильных сторон: {result.strengths.length}</span>
            <span className="badge badge-warning" style={{ marginLeft: '0.5rem' }}>Пробелов: {result.gaps.length}</span>
            <span className="badge badge-danger" style={{ marginLeft: '0.5rem' }}>Нет навыков: {result.missing_skills.length}</span>
          </div>
        </div>
      </div>
      <div style={{ textAlign: 'left' }}>
        <h3 style={{ marginBottom: '1rem' }}>Рекомендуемые правки резюме:</h3>
        <ul style={{ marginLeft: '1.25rem' }}>
          {result.recommended_changes.map((c, i) => <li key={i} style={{ margin: '0.5rem 0' }}>{c}</li>)}
        </ul>
      </div>
    </div>
  )

  const renderList = (title: string, items: string[], iconClass: string) => (
    <div className="card">
      <h3 style={{ marginBottom: '1rem' }}>{title}</h3>
      <div>
        {items.map((item, i) => (
          <div key={i} className="list-item">
            <div className={`list-item-icon ${iconClass}`}>{iconClass === 'success' ? '✓' : iconClass === 'warning' ? '!' : '×'}</div>
            <div className="list-item-content"><div className="list-item-title">{item}</div></div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderQuestions = () => (
    <div className="card">
      <h3 style={{ marginBottom: '1rem' }}>Вопросы, которые скорее всего зададут на собеседовании</h3>
      <div>
        {result.interview_questions.map((q, i) => (
          <div key={i} className="list-item" style={{ borderColor: 'var(--accent)' }}>
            <div className="list-item-icon info">?</div>
            <div className="list-item-content">
              <div className="list-item-title">
                <span className="badge badge-info" style={{ marginRight: '0.5rem' }}>{q.category}</span>
                {q.question}
              </div>
              <div className="list-item-desc">💡 Подсказка: {q.hint}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderPlan = () => (
    <div className="card">
      <h3 style={{ marginBottom: '1rem' }}>План подготовки (7 дней)</h3>
      <div>
        {result.preparation_plan.map((day, i) => (
          <div key={i} className="list-item" style={{ borderColor: 'var(--success)' }}>
            <div className="list-item-icon success">{day.day}</div>
            <div className="list-item-content">
              <div className="list-item-title">{day.focus}</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', marginTop: '0.5rem' }}>
                {day.tasks.map((t, ti) => (
                  <span key={ti} className="badge badge-info" style={{ fontSize: '0.7rem', padding: '0.125rem 0.5rem' }}>{t}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  return (
    <div>
      <div className="tabs" style={{ marginBottom: '1.5rem' }}>
        {tabs.map(t => (
          <button
            key={t.id}
            className={`tab ${activeTab === t.id ? 'active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === 'score' && renderScore()}
      {activeTab === 'strengths' && renderList('✅ Сильные стороны', result.strengths, 'success')}
      {activeTab === 'gaps' && renderList('⚠️ Пробелы в опыте', result.gaps, 'warning')}
      {activeTab === 'questions' && renderQuestions()}
      {activeTab === 'plan' && renderPlan()}

      <div style={{ marginTop: '2rem', textAlign: 'center' }}>
        <button className="btn btn-secondary btn-lg" onClick={onRestart}>🔄 Начать заново</button>
      </div>
    </div>
  )
}

// ─── Main App ───────────────────────────────────────────────────────────
export default function App() {
  const [step, setStep] = useState<Step>(1)
  const [file, setFile] = useState<File | null>(null)
  const [parsed, setParsed] = useState<ParsedResume | null>(null)
  const [parsing, setParsing] = useState(false)
  const [vacancyUrl, setVacancyUrl] = useState('')
  const [vacancy, setVacancy] = useState<any>(null)
  const [vacancyLoading, setVacancyLoading] = useState(false)
  const [matching, setMatching] = useState(false)
  const [result, setResult] = useState<MatchResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFile = useCallback(async (f: File | null) => {
    if (!f) {
      setFile(null)
      setParsed(null)
      return
    }
    setFile(f)
    setParsing(true)
    setError(null)
    try {
      const data = await parseResume(f)
      setParsed(data.parsed)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setParsing(false)
    }
  }, [])

  const handleVacancySubmit = useCallback(async (url: string) => {
    if (!url) {
      setVacancy(null)
      setVacancyUrl('')
      return
    }
    setVacancyUrl(url)
    setVacancyLoading(true)
    setError(null)
    try {
      const data = await fetchVacancy(url)
      setVacancy(data)
      setStep(3)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setVacancyLoading(false)
    }
  }, [])

  const handleMatch = useCallback(async () => {
    if (!parsed || !vacancy) return
    setMatching(true)
    setError(null)
    try {
      const data = await matchResume('resume_' + Date.now(), vacancy)
      setResult(data.result)
      setStep(4)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setMatching(false)
    }
  }, [parsed, vacancy])

  const handleRestart = useCallback(() => {
    setStep(1)
    setFile(null)
    setParsed(null)
    setVacancyUrl('')
    setVacancy(null)
    setResult(null)
    setError(null)
  }, [])

  // ─── Render ──────────────────────────────────────────────────────────
  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <a href="#" className="logo">
            <span className="logo-icon">🎯</span>
            AI Interview Prep
          </a>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Подготовка джуниоров к собеседованиям
          </div>
        </div>
      </header>

      <main className="main-content">
        {error && (
          <div className="alert alert-error" style={{ maxWidth: 800, margin: '0 auto 1.5rem' }}>
            <span>⚠️</span>
            <span>{error}</span>
            <button className="btn btn-ghost btn-sm" onClick={() => setError(null)}>×</button>
          </div>
        )}

        <StepIndicator currentStep={step} />

        {step === 1 && (
          <div style={{ maxWidth: 600, margin: '0 auto' }}>
            <div className="hero">
              <h1 className="hero-title">AI Interview Prep</h1>
              <p className="hero-subtitle">
                Загрузите резюме, вставьте ссылку на вакансию с HH.ru — получите мэтч-скор,
                список пробелов, вопросы к собеседованию и 7-дневный план подготовки.
              </p>
              <div className="hero-actions">
                <span style={{ alignSelf: 'center', color: 'var(--text-muted)' }}>Шаг 1 из 4</span>
              </div>
            </div>
            <FileUpload
              onFile={handleFile}
              file={file}
              parsing={parsing}
              parsed={parsed}
            />
            {parsed && (
              <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                <button className="btn btn-primary btn-lg" onClick={() => setStep(2)} style={{ width: '100%' }}>
                  Далее: указать вакансию →
                </button>
              </div>
            )}
          </div>
        )}

        {step === 2 && (
          <div style={{ maxWidth: 600, margin: '0 auto' }}>
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <div className="card-header">
                <div>
                  <div className="card-title">📄 Резюме готово</div>
                  <div className="card-subtitle">{parsed?.skills.length} навыков · {parsed?.experience_years} лет опыта</div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <div className="card-title">🔗 Вакансия с HH.ru</div>
              </div>
              <VacancyInput onSubmit={handleVacancySubmit} loading={vacancyLoading} vacancy={vacancy} />
            </div>

            {!vacancy && (
              <div className="card" style={{ marginTop: '1rem', background: 'rgba(88,166,255,0.05)', borderColor: 'var(--accent)' }}>
                <strong>Нет ссылки на HH?</strong> Нажмите «Пропустить» и вставьте описание вакансии текстом на следующем шаге.
              </div>
            )}

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <button className="btn btn-secondary" onClick={() => setStep(1)} style={{ flex: 1 }}>← Назад</button>
              {vacancy && (
                <button className="btn btn-primary" onClick={handleMatch} disabled={matching} style={{ flex: 2 }}>
                  {matching ? 'Мэтчинг...' : 'Найти соответствие →'}
                </button>
              )}
            </div>
          </div>
        )}

        {step === 3 && (
          <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center' }}>
            <div className="hero" style={{ background: 'rgba(88,166,255,0.08)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</div>
              <h2 className="hero-title" style={{ fontSize: '2rem' }}>Анализируем соответствие</h2>
              <p className="hero-subtitle">
                GPT-4o сравнивает ваши навыки с требованиями вакансии, ищет пробелы, генерирует вопросы.
              </p>
            </div>
            <MatchProgress onComplete={() => {}} />
          </div>
        )}

        {step === 4 && result && (
          <div style={{ maxWidth: 900, margin: '0 auto' }}>
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <div className="card-header">
                <div>
                  <div className="card-title">🎯 Результат готов</div>
                  <div className="card-subtitle">Вакансия: {vacancy?.name} — {vacancy?.company}</div>
                </div>
                <div className="match-score">
                  <div className="score-circle" style={{ '--score': result.match_score, width: 70, height: 70 }}>
                    <span className="score-value" style={{ fontSize: '1.25rem' }}>{Math.round(result.match_score)}%</span>
                  </div>
                </div>
              </div>
            </div>

            <ResultsView result={result} onRestart={handleRestart} />
          </div>
        )}
      </main>

      <footer className="footer">
        AI Interview Prep — прототип для джуниоров. Backend: FastAPI + GPT-4o + ChromaDB + SentenceTransformers
      </footer>
    </div>
  )
}