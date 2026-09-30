import type {
  AnalysisHistoryRow,
  AnalysisResult,
  ApiClient,
  ApiHealth,
  ResumeRecord,
  UploadResumeRequest,
  UploadResumeResponse,
  ExtractedProfile,
} from './types';

type BackendAnalysis = {
  id: string;
  resumeId: string;
  jobId: string;
  overall_score: number;
  matched_skills: string[];
  missing_skills: string[];
  summary: string;
  skill_score: number;
  experience_score: number;
  education_score: number;
  semantic_score: number;
  recommendations: string[];
};

type BackendAnalysisListItem = BackendAnalysis & {
  candidate: string;
  jobTitle: string;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  return (await response.json()) as T;
}

function toAnalysis(result: BackendAnalysis): AnalysisResult {
  return {
    id: result.id,
    resumeId: result.resumeId,
    jobId: result.jobId,
    score: result.overall_score,
    matchedSkills: result.matched_skills,
    missingSkills: result.missing_skills,
    summary: result.summary,
    skillScore: result.skill_score,
    experienceScore: result.experience_score,
    educationScore: result.education_score,
    semanticScore: result.semantic_score,
    recommendations: result.recommendations,
  };
}

export const liveClient: ApiClient = {
  getHealth: () => request<ApiHealth>('/health'),
  uploadResume: (input: UploadResumeRequest) =>
    request<UploadResumeResponse>('/upload', {
      method: 'POST',
      body: JSON.stringify(input),
    }),
  uploadResumeFile: async (file: File, jobDescription: string) => {
    const form = new FormData();
    form.append('resume', file);
    form.append('job_description', jobDescription);
    const response = await fetch(`${API_BASE}/upload-file`, { method: 'POST', body: form });
    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as { detail?: string };
      throw new Error(body.detail ?? `Upload failed (${response.status})`);
    }
    return (await response.json()) as UploadResumeResponse;
  },
  getResume: async (id: string) => {
    const result = await request<{ resume: ResumeRecord & { profile: ExtractedProfile } }>(`/resumes/${encodeURIComponent(id)}`);
    return result.resume;
  },
  analyzeResume: async (resumeId: string, jobId: string) =>
    toAnalysis(
      await request<BackendAnalysis>('/analyze', {
        method: 'POST',
        body: JSON.stringify({ resumeId, jobId }),
      }),
    ),
  listAnalyses: async () => {
    const result = await request<{ rows: BackendAnalysisListItem[] }>('/analyses');
    return result.rows.map((row) => ({
      ...toAnalysis(row),
      candidate: row.candidate,
      jobTitle: row.jobTitle,
    }));
  },
  getAnalysis: async (id: string) => {
    const result = await request<{ analysis: BackendAnalysis }>(`/analyses/${encodeURIComponent(id)}`);
    return toAnalysis(result.analysis);
  },
};
