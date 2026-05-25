import { useCallback, useEffect, useMemo, useState } from 'react'
import Editor from '@monaco-editor/react'
import {
  Activity,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Code2,
  Database,
  FileCode2,
  Filter,
  Gauge,
  Layers3,
  Play,
  RefreshCw,
  Search,
  Server,
  Sparkles,
  TerminalSquare,
  XCircle,
} from 'lucide-react'
import './App.css'
import './monacoSetup'
import {
  fetchHealth,
  fetchProblem,
  fetchProblems,
  fetchSubmission,
  fetchSubmissionStats,
  submitCode,
} from './api'
import type { Language, ProblemDetail, ProblemListItem, SubmissionDetail, SubmissionStats } from './types'

const languageTemplates: Record<Language, string> = {
  python: 'a, b = map(int, input().split())\nprint(a + b)\n',
  cpp: '#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    long long a, b;\n    cin >> a >> b;\n    cout << a + b << "\\n";\n    return 0;\n}\n',
}

const difficultyLabels: Record<string, string> = {
  easy: '简单',
  medium: '中等',
  hard: '困难',
}

const statusLabels: Record<string, string> = {
  PENDING: '等待中',
  RUNNING: '评测中',
  AC: '通过',
  WA: '答案错误',
  CE: '编译错误',
  RE: '运行错误',
  TLE: '超时',
}

function App() {
  const [problems, setProblems] = useState<ProblemListItem[]>([])
  const [selectedProblem, setSelectedProblem] = useState<ProblemDetail | null>(null)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [keyword, setKeyword] = useState('')
  const [difficulty, setDifficulty] = useState('')
  const [tag, setTag] = useState('')
  const [language, setLanguage] = useState<Language>('python')
  const [code, setCode] = useState(languageTemplates.python)
  const [submission, setSubmission] = useState<SubmissionDetail | null>(null)
  const [stats, setStats] = useState<SubmissionStats | null>(null)
  const [health, setHealth] = useState<'checking' | 'ok' | 'error'>('checking')
  const [loadingProblems, setLoadingProblems] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const loadProblems = useCallback(async () => {
    setLoadingProblems(true)
    setError('')
    try {
      const response = await fetchProblems({
        keyword: keyword.trim() || undefined,
        difficulty: difficulty || undefined,
        tag: tag.trim() || undefined,
      })
      setProblems(response.items)
      if (!selectedId && response.items[0]) {
        setSelectedId(response.items[0].id)
      }
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setLoadingProblems(false)
    }
  }, [difficulty, keyword, selectedId, tag])

  useEffect(() => {
    void fetchHealth()
      .then(() => setHealth('ok'))
      .catch(() => setHealth('error'))
    void fetchSubmissionStats().then(setStats).catch(() => setStats(null))
  }, [])

  useEffect(() => {
    const handle = window.setTimeout(() => {
      void loadProblems()
    }, 220)
    return () => window.clearTimeout(handle)
  }, [loadProblems])

  useEffect(() => {
    if (!selectedId) {
      return
    }

    fetchProblem(selectedId)
      .then((problem) => {
        setSelectedProblem(problem)
        setSubmission(null)
      })
      .catch((err) => setError(getErrorMessage(err)))
  }, [selectedId])

  useEffect(() => {
    if (!submission || !['PENDING', 'RUNNING'].includes(submission.status)) {
      return
    }

    const handle = window.setInterval(() => {
      fetchSubmission(submission.id)
        .then((next) => {
          setSubmission(next)
          if (!['PENDING', 'RUNNING'].includes(next.status)) {
            void fetchSubmissionStats().then(setStats).catch(() => null)
          }
        })
        .catch((err) => setError(getErrorMessage(err)))
    }, 1200)

    return () => window.clearInterval(handle)
  }, [submission])

  const allTags = useMemo(() => {
    return Array.from(new Set(problems.flatMap((problem) => problem.tags.map((item) => item.name)))).sort()
  }, [problems])

  const activeProblem = selectedProblem ?? (selectedId ? null : undefined)
  const loadingProblem = Boolean(selectedId && selectedProblem?.id !== selectedId)
  const visibleStats = stats ?? {
    total: 0,
    accepted: 0,
    wrong_answer: 0,
    compile_error: 0,
    runtime_error: 0,
    time_limit_exceeded: 0,
    pending: 0,
  }

  function changeLanguage(nextLanguage: Language) {
    setLanguage(nextLanguage)
    setCode(languageTemplates[nextLanguage])
  }

  async function handleSubmit() {
    if (!selectedProblem) {
      return
    }

    setSubmitting(true)
    setError('')
    try {
      const created = await submitCode({
        problem_id: selectedProblem.id,
        language,
        code,
      })
      setSubmission({ ...created, code })
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-block">
          <div className="brand-mark">
            <Code2 size={22} />
          </div>
          <div>
            <h1>Algorithm Lab</h1>
            <p>本地算法题库与在线评测工作台</p>
          </div>
        </div>

        <nav className="nav-tabs" aria-label="Primary">
          <button className="nav-tab active" type="button">
            <BookOpen size={16} />
            题库
          </button>
          <button className="nav-tab" type="button">
            <Activity size={16} />
            提交
          </button>
          <button className="nav-tab" type="button">
            <Sparkles size={16} />
            辅导
          </button>
        </nav>

        <div className={`service-pill ${health}`}>
          <Server size={16} />
          <span>{health === 'ok' ? '后端在线' : health === 'checking' ? '检测中' : '后端离线'}</span>
        </div>
      </header>

      <section className="metrics-grid" aria-label="submission metrics">
        <Metric icon={<Database size={18} />} label="总提交" value={visibleStats.total} />
        <Metric icon={<CheckCircle2 size={18} />} label="通过" value={visibleStats.accepted} tone="success" />
        <Metric icon={<XCircle size={18} />} label="未通过" value={visibleStats.wrong_answer + visibleStats.compile_error + visibleStats.runtime_error + visibleStats.time_limit_exceeded} tone="danger" />
        <Metric icon={<Clock3 size={18} />} label="队列中" value={visibleStats.pending} tone="warning" />
      </section>

      {error && (
        <div className="error-banner" role="alert">
          <XCircle size={18} />
          {error}
        </div>
      )}

      <section className="workspace">
        <aside className="problem-pane" aria-label="problem list">
          <div className="pane-header">
            <div>
              <span className="eyebrow">Problem Set</span>
              <h2>训练题库</h2>
            </div>
            <button className="icon-button" type="button" onClick={() => void loadProblems()} title="刷新题库">
              <RefreshCw size={17} />
            </button>
          </div>

          <div className="filters">
            <label className="search-box">
              <Search size={17} />
              <input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索题目" />
            </label>

            <div className="filter-row">
              <label>
                <Filter size={15} />
                <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
                  <option value="">全部难度</option>
                  <option value="easy">简单</option>
                  <option value="medium">中等</option>
                  <option value="hard">困难</option>
                </select>
              </label>

              <label>
                <Layers3 size={15} />
                <select value={tag} onChange={(event) => setTag(event.target.value)}>
                  <option value="">全部标签</option>
                  {allTags.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </div>

          <div className="problem-list">
            {loadingProblems ? (
              <EmptyState icon={<RefreshCw size={20} />} title="正在加载题库" />
            ) : problems.length ? (
              problems.map((problem) => (
                <button
                  className={`problem-item ${problem.id === selectedId ? 'selected' : ''}`}
                  type="button"
                  key={problem.id}
                  onClick={() => setSelectedId(problem.id)}
                >
                  <div className="problem-title-row">
                    <span className="problem-title">{problem.title}</span>
                    <ChevronRight size={16} />
                  </div>
                  <div className="problem-meta">
                    <span className={`difficulty ${problem.difficulty}`}>{difficultyLabels[problem.difficulty] ?? problem.difficulty}</span>
                    {problem.tags.slice(0, 2).map((item) => (
                      <span className="tag" key={item.id}>
                        {item.name}
                      </span>
                    ))}
                  </div>
                </button>
              ))
            ) : (
              <EmptyState icon={<Search size={20} />} title="没有匹配的题目" />
            )}
          </div>
        </aside>

        <section className="detail-pane" aria-label="problem detail">
          {loadingProblem || activeProblem === null ? (
            <EmptyState icon={<RefreshCw size={22} />} title="正在加载题目详情" />
          ) : selectedProblem ? (
            <>
              <div className="detail-header">
                <div>
                  <span className="eyebrow">Problem #{selectedProblem.id}</span>
                  <h2>{selectedProblem.title}</h2>
                </div>
                <span className={`difficulty ${selectedProblem.difficulty}`}>
                  {difficultyLabels[selectedProblem.difficulty] ?? selectedProblem.difficulty}
                </span>
              </div>

              <div className="tag-strip">
                {selectedProblem.tags.map((item) => (
                  <span className="tag" key={item.id}>
                    {item.name}
                  </span>
                ))}
              </div>

              <ProblemSection title="题目描述" content={selectedProblem.description} />
              <ProblemSection title="输入格式" content={selectedProblem.input_description} />
              <ProblemSection title="输出格式" content={selectedProblem.output_description} />
              <ProblemSection title="数据范围" content={selectedProblem.constraints || '暂无'} />

              <div className="sample-grid">
                <SampleBlock title="样例输入" value={selectedProblem.sample_input || selectedProblem.test_cases[0]?.input_data || ''} />
                <SampleBlock title="样例输出" value={selectedProblem.sample_output || selectedProblem.test_cases[0]?.expected_output || ''} />
              </div>
            </>
          ) : (
            <EmptyState icon={<BookOpen size={22} />} title="请选择一道题目" />
          )}
        </section>

        <section className="judge-pane" aria-label="code runner">
          <div className="pane-header compact">
            <div>
              <span className="eyebrow">Online Judge</span>
              <h2>代码提交</h2>
            </div>
            <div className="language-switch" aria-label="language">
              <button className={language === 'python' ? 'active' : ''} type="button" onClick={() => changeLanguage('python')}>
                Python
              </button>
              <button className={language === 'cpp' ? 'active' : ''} type="button" onClick={() => changeLanguage('cpp')}>
                C++
              </button>
            </div>
          </div>

          <div className="editor-wrap">
            <Editor
              height="100%"
              language={language === 'cpp' ? 'cpp' : 'python'}
              theme="vs-dark"
              value={code}
              onChange={(value) => setCode(value ?? '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineHeight: 22,
                padding: { top: 14, bottom: 14 },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                automaticLayout: true,
              }}
            />
          </div>

          <div className="submit-row">
            <button className="primary-button" type="button" disabled={!selectedProblem || submitting} onClick={() => void handleSubmit()}>
              <Play size={17} />
              {submitting ? '提交中' : '提交评测'}
            </button>
            <button className="ghost-button" type="button" onClick={() => setCode(languageTemplates[language])}>
              <FileCode2 size={16} />
              重置模板
            </button>
          </div>

          <div className="result-panel">
            <div className="result-head">
              <div>
                <span className="eyebrow">Result</span>
                <h3>评测结果</h3>
              </div>
              <Gauge size={18} />
            </div>

            {submission ? (
              <div className={`submission-card ${submission.status.toLowerCase()}`}>
                <div className="submission-status">
                  <StatusIcon status={submission.status} />
                  <div>
                    <strong>{statusLabels[submission.status] ?? submission.status}</strong>
                    <span>Submission #{submission.id}</span>
                  </div>
                </div>
                <div className="score-line">
                  <span>得分</span>
                  <strong>{submission.score}</strong>
                </div>
                <div className="result-facts">
                  <span>{submission.language.toUpperCase()}</span>
                  <span>{submission.time_ms ?? '-'} ms</span>
                  <span>{submission.created_at.replace('T', ' ')}</span>
                </div>
                {submission.error_message && <pre className="error-output">{submission.error_message}</pre>}
              </div>
            ) : (
              <EmptyState icon={<TerminalSquare size={20} />} title="提交后将在这里显示判题结果" />
            )}
          </div>
        </section>
      </section>
    </main>
  )
}

function Metric({
  icon,
  label,
  value,
  tone = 'neutral',
}: {
  icon: React.ReactNode
  label: string
  value: number
  tone?: 'neutral' | 'success' | 'danger' | 'warning'
}) {
  return (
    <div className={`metric ${tone}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  )
}

function ProblemSection({ title, content }: { title: string; content: string }) {
  return (
    <section className="problem-section">
      <h3>{title}</h3>
      <p>{content}</p>
    </section>
  )
}

function SampleBlock({ title, value }: { title: string; value: string }) {
  return (
    <div className="sample-block">
      <span>{title}</span>
      <pre>{value || '暂无样例'}</pre>
    </div>
  )
}

function EmptyState({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="empty-state">
      {icon}
      <span>{title}</span>
    </div>
  )
}

function StatusIcon({ status }: { status: string }) {
  if (status === 'AC') {
    return <CheckCircle2 size={24} />
  }
  if (['WA', 'CE', 'RE', 'TLE'].includes(status)) {
    return <XCircle size={24} />
  }
  return <Clock3 size={24} />
}

function getErrorMessage(err: unknown) {
  if (err instanceof Error) {
    return err.message
  }
  return '请求失败，请确认后端服务正在运行'
}

export default App
