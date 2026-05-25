export type Language = 'python' | 'cpp'

export type Tag = {
  id: number
  name: string
}

export type PageMeta = {
  total: number
  limit: number
  offset: number
}

export type ProblemListItem = {
  id: number
  title: string
  difficulty: 'easy' | 'medium' | 'hard'
  tags: Tag[]
  created_at: string
}

export type TestCase = {
  id: number
  input_data: string
  expected_output: string
  is_sample: boolean
  sort_order: number
}

export type ProblemDetail = {
  id: number
  title: string
  difficulty: 'easy' | 'medium' | 'hard'
  description: string
  input_description: string
  output_description: string
  constraints: string
  sample_input: string
  sample_output: string
  tags: Tag[]
  test_cases: TestCase[]
  created_at: string
  updated_at: string
}

export type ProblemListResponse = {
  items: ProblemListItem[]
  meta: PageMeta
}

export type SubmissionRead = {
  id: number
  problem_id: number
  language: Language
  status: string
  score: number
  time_ms: number | null
  memory_kb: number | null
  error_message: string | null
  created_at: string
  judged_at: string | null
}

export type SubmissionDetail = SubmissionRead & {
  code: string
}

export type SubmissionStats = {
  total: number
  accepted: number
  wrong_answer: number
  compile_error: number
  runtime_error: number
  time_limit_exceeded: number
  pending: number
}

export type SubmitPayload = {
  problem_id: number
  language: Language
  code: string
}
