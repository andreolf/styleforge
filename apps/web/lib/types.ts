/**
 * API Types for DressLike
 */

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface StylePreset {
  id: string;
  name: string;
  description: string;
  prompt: string;
  thumbnail: string | null;
}

export interface StyleListResponse {
  styles: StylePreset[];
  count: number;
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  result_url: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
  style_id: string;
}

export interface CreateJobResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  result_url: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
  style_id: string;
}

export interface ApiError {
  error: string;
  detail?: string;
  request_id?: string;
}

