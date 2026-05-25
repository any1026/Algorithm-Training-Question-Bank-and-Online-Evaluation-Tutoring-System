import type {
  ProblemDetail,
  ProblemListResponse,
  SubmissionDetail,
  SubmissionRead,
  SubmissionStats,
  SubmitPayload,
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type ProblemQuery = {
  keyword?: string
  difficulty?: string
  tag?: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
    ...init,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed with status ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function fetchHealth() {
  return request<{ status: string; app: string }>('/health')
}

export function fetchProblems(query: ProblemQuery = {}) {
  const params = new URLSearchParams()
  if (query.keyword) params.set('keyword', query.keyword)
  if (query.difficulty) params.set('difficulty', query.difficulty)
  if (query.tag) params.set('tag', query.tag)
  return request<ProblemListResponse>(`/api/v1/problems?${params.toString()}`)
}

export function fetchProblem(problemId: number) {
  return request<ProblemDetail>(`/api/v1/problems/${problemId}`)
}

export function submitCode(payload: SubmitPayload) {
  return request<SubmissionRead>('/api/v1/submissions', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchSubmission(submissionId: number) {
  return request<SubmissionDetail>(`/api/v1/submissions/${submissionId}`)
}

export function fetchSubmissionStats() {
  return request<SubmissionStats>('/api/v1/submissions/stats')
}
