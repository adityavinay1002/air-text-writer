export const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  HEALTH: `${BACKEND_BASE_URL}/health`,
  CAMERA_START: `${BACKEND_BASE_URL}/api/camera/start`,
  CAMERA_STOP: `${BACKEND_BASE_URL}/api/camera/stop`,
  CAMERA_STREAM: `${BACKEND_BASE_URL}/api/camera/stream`,
  SESSION_CLEAR: `${BACKEND_BASE_URL}/api/session/clear`,
  SEARCH: (query: string) => `${BACKEND_BASE_URL}/api/search?q=${encodeURIComponent(query)}`,
  WEBSOCKET: `${BACKEND_BASE_URL.replace(/^http/, 'ws')}/ws`,
};
