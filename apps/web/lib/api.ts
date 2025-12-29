/**
 * API client for StyleForge backend
 */

import { ApiError, CreateJobResponse, JobResponse, StyleListResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: 'Unknown error',
        detail: response.statusText,
      }));
      throw new Error(error.detail || error.error);
    }
    return response.json();
  }

  /**
   * Get all available style presets
   */
  async getStyles(): Promise<StyleListResponse> {
    const response = await fetch(`${this.baseUrl}/api/styles`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    return this.handleResponse<StyleListResponse>(response);
  }

  /**
   * Create a new transformation job
   */
  async createJob(image: File, styleId: string): Promise<CreateJobResponse> {
    const formData = new FormData();
    formData.append('image', image);
    formData.append('style_id', styleId);

    const response = await fetch(`${this.baseUrl}/api/jobs`, {
      method: 'POST',
      body: formData,
    });
    return this.handleResponse<CreateJobResponse>(response);
  }

  /**
   * Get job status and result
   */
  async getJob(jobId: string): Promise<JobResponse> {
    const response = await fetch(`${this.baseUrl}/api/jobs/${jobId}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });
    return this.handleResponse<JobResponse>(response);
  }

  /**
   * Poll job until completion or failure
   */
  async pollJob(
    jobId: string,
    onProgress?: (job: JobResponse) => void,
    intervalMs: number = 1000,
    timeoutMs: number = 300000
  ): Promise<JobResponse> {
    const startTime = Date.now();

    while (true) {
      const job = await this.getJob(jobId);

      if (onProgress) {
        onProgress(job);
      }

      if (job.status === 'completed' || job.status === 'failed') {
        return job;
      }

      if (Date.now() - startTime > timeoutMs) {
        throw new Error('Job timed out');
      }

      await new Promise(resolve => setTimeout(resolve, intervalMs));
    }
  }

  /**
   * Get full URL for result image
   */
  getResultUrl(resultPath: string): string {
    if (resultPath.startsWith('http')) {
      return resultPath;
    }
    return `${this.baseUrl}${resultPath}`;
  }
}

export const api = new ApiClient();
export default api;

