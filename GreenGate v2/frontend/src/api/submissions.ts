import client from './client';
import type { Submission } from '../types';

export const getSubmissions = async (orgId: string): Promise<Submission[]> => {
  const res = await client.get<Submission[]>(`/organisations/${orgId}/submissions`);
  return res.data;
};

export const createSubmission = async (
  orgId: string,
  data: Omit<Submission, 'id' | 'org_id' | 'created_at' | 'updated_at'>
): Promise<Submission> => {
  const res = await client.post<Submission>(`/organisations/${orgId}/submissions`, data);
  return res.data;
};

export const updateSubmissionStatus = async (
  orgId: string,
  submissionId: string,
  status: Submission['status']
): Promise<Submission> => {
  const res = await client.patch<Submission>(
    `/organisations/${orgId}/submissions/${submissionId}`,
    { status }
  );
  return res.data;
};
