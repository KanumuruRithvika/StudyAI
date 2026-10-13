
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const TOKEN_KEY = "access_token";
const USER_KEY = "auth_user";
const SESSION_KEY = "learning_session_id";
const STATE_KEY = "learning_session_state";

// Authentication token helpers
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || "null");
  } catch {
    return null;
  }
}

// Learning session helpers
export function saveSessionId(id) {
  if (id) {
    sessionStorage.setItem(SESSION_KEY, id);
  }
}

export function getSessionId() {
  return sessionStorage.getItem(SESSION_KEY);
}

export function clearSessionId() {
  sessionStorage.removeItem(SESSION_KEY);
  sessionStorage.removeItem(STATE_KEY);
}

export function saveSessionState(state) {
  if (state && typeof state === "object") {
    sessionStorage.setItem(STATE_KEY, JSON.stringify(state));
  }
}

export function getSessionState() {
  try {
    return JSON.parse(sessionStorage.getItem(STATE_KEY) || "null");
  } catch {
    return null;
  }
}

export function mergeSessionState(serverState) {
  const cached = getSessionState() || {};
  const merged = { ...cached, ...(serverState || {}) };

  saveSessionState(merged);
  return merged;
}

// Common API request handler
async function request(path, options = {}) {
  const token = getToken();
  const headers = new Headers(options.headers || {});

  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const responseText = await response.text();
  let data = null;

  if (responseText) {
    try {
      data = JSON.parse(responseText);
    } catch {
      data = { detail: responseText };
    }
  }

  if (!response.ok) {
    const detail =
      data?.detail ||
      data?.message ||
      `Request failed with status ${response.status}.`;

    const errorMessage = Array.isArray(detail)
      ? detail
          .map((item) => item.msg || "Invalid input")
          .join(", ")
      : detail;

    throw new Error(errorMessage);
  }

  return data;
}

// API endpoints
export const api = {
  signup: (payload) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  login: (payload) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  startLearning: (payload) =>
    request("/learning/start", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  approvePlan: (sessionId, approved, feedback = "") =>
    request(`/learning/${sessionId}/approve`, {
      method: "POST",
      body: JSON.stringify({ approved, feedback }),
    }),

  completeTask: (sessionId, taskId, completed = true) =>
    request(`/learning/${sessionId}/tasks/complete`, {
      method: "POST",
      body: JSON.stringify({
        task_id: taskId,
        completed,
      }),
    }),

  submitDay: (sessionId, tasks) =>
    request(`/learning/${sessionId}/day/submit`, {
      method: "POST",
      body: JSON.stringify({
        tasks: tasks.map((task) => ({
          task_id: task.task_id,
          status: task.status,
          notes: task.notes ?? null,
        })),
      }),
    }),

  submitQuiz: (sessionId, answers) =>
    request(`/learning/${sessionId}/quiz/submit`, {
      method: "POST",
      body: JSON.stringify({
        answers: answers.map((answer) => ({
          question_id: answer.question_id,
          answer: answer.answer,
        })),
      }),
    }),

  getProgress: (sessionId) =>
    request(`/learning/${sessionId}/progress`, {
      method: "GET",
    }),

  getPerformance: (sessionId) =>
    request(`/learning/${sessionId}/performance`, {
      method: "GET",
    }),

  submitAdaptation: (sessionId, action) =>
    request(`/learning/${sessionId}/adapt`, {
      method: "POST",
      body: JSON.stringify({ action }),
    }),

  getTaskDetail: (sessionId, taskId) =>
    request(`/learning/${sessionId}/tasks/${taskId}/detail`, {
      method: "GET",
    }),
};
