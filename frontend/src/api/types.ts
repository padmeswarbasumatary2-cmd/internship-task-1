export type UploadResumeRequest = {
  file: string;
  jobDescription: string;
};

export type UploadResumeResponse = {
  resumeId: string;
  jobId: string;
  analysisId: string;
};

export type ExtractedProfile = {
  name: string | null;
  contact: { email: string | null; phone: string | null; linkedin: string | null; github: string | null };
  education: string[];
  experienceHighlights: string[];
  graduationYears: number[];
  skills: string[];
  educationEntries: number;
  experienceEntries: number;
};

export type ResumeRecord = {
  id: string;
  filename: string;
  jobDescription: string;
  jobId: string;
  profile: ExtractedProfile;
};

export type AnalysisResult = {
  id: string;
  resumeId: string;
  jobId: string;
  score: number;
  matchedSkills: string[];
  missingSkills: string[];
  summary: string;
  skillScore: number;
  experienceScore: number;
  educationScore: number;
  semanticScore: number;
  recommendations: string[];
};

export type AnalysisHistoryRow = AnalysisResult & {
  candidate: string;
  jobTitle: string;
};

export type ApiHealth = {
  status: string;
  services: Record<string, string>;
};

export type ApiClient = {
  getHealth: () => Promise<ApiHealth>;
  uploadResume: (input: UploadResumeRequest) => Promise<UploadResumeResponse>;
  uploadResumeFile: (file: File, jobDescription: string) => Promise<UploadResumeResponse>;
  getResume: (id: string) => Promise<ResumeRecord>;
  analyzeResume: (resumeId: string, jobId: string) => Promise<AnalysisResult>;
  listAnalyses: () => Promise<AnalysisHistoryRow[]>;
  getAnalysis: (id: string) => Promise<AnalysisResult>;
};
