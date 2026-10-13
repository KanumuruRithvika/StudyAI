import axios from "axios"

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
})

export async function startLearning(data) {
  const response = await api.post(
    "/learning/start",
    {
      user_id: "demo-user",
      learning_mode: data.learning_mode,
      goal: data.goal,
      current_level: data.current_level,
      available_time_minutes:
        Number(data.available_time_minutes),
      duration_days:
        Number(data.duration_days),

      role: data.role || null,
      project_name:
        data.project_name || null,
      project_description:
        data.project_description || null,

      current_skills:
        data.current_skills || [],
      required_skills:
        data.required_skills || [],
      required_technologies:
        data.required_technologies || [],
    }
  )

  return response.data
}

export async function approvePlan(
  sessionId,
  approved,
  feedback = ""
) {
  const response = await api.post(
    `/learning/${sessionId}/approve`,
    {
      approved,
      feedback,
    }
  )

  return response.data
}

export async function submitDay(
  sessionId,
  tasks
) {
  const response = await api.post(
    `/learning/${sessionId}/day/submit`,
    {
      tasks,
    }
  )

  return response.data
}

export async function submitQuiz(
  sessionId,
  answers
) {
  const response = await api.post(
    `/learning/${sessionId}/quiz/submit`,
    {
      answers,
    }
  )

  return response.data
}

export async function submitAdaptation(
  sessionId,
  action,
  availableTimeMinutes,
  durationDays,
  description
) {
  const response = await api.post(
    `/learning/${sessionId}/adapt`,
    {
      action,
      available_time_minutes:
        Number(availableTimeMinutes),
      duration_days:
        Number(durationDays),
      description:
        description || "",
    }
  )

  return response.data
}

export async function getProgress(
  sessionId
) {
  const response = await api.get(
    `/learning/${sessionId}/progress`
  )

  return response.data
}

export default api