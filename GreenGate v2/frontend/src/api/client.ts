import axios from 'axios';

let accessToken: string | null = null;
let refreshTokenValue: string | null = null;

export const setTokens = (access: string, refresh: string) => {
  accessToken = access;
  refreshTokenValue = refresh;
};

export const clearTokens = () => {
  accessToken = null;
  refreshTokenValue = null;
};

export const getAccessToken = () => accessToken;
export const getRefreshToken = () => refreshTokenValue;

// Read once at module load. Empty string → use Vite's dev proxy via relative paths.
// In production (Vercel), set VITE_API_BASE_URL to the Railway backend URL.
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '');

const client = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

client.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      refreshTokenValue
    ) {
      originalRequest._retry = true;
      try {
        const res = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
          token: refreshTokenValue,
        });
        const { access_token, refresh_token } = res.data;
        setTokens(access_token, refresh_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return client(originalRequest);
      } catch {
        clearTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export default client;
