import client from './client';
import type { Framework, Rule } from '../types';

export const getFrameworks = async (): Promise<Framework[]> => {
  const res = await client.get<Framework[]>('/frameworks');
  return res.data;
};

export const getFrameworkRules = async (frameworkId: string): Promise<Rule[]> => {
  const res = await client.get<Rule[]>(`/frameworks/${frameworkId}/rules`);
  return res.data;
};
