import client from "./client.js";

export const authApi = {
  register: (email, password, fullName) =>
    client.post("/auth/register", { email, password, full_name: fullName || null }),

  login: async (email, password) => {
    const form = new URLSearchParams();
    form.append("username", email);
    form.append("password", password);
    const { data } = await client.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return data;
  },

  verifyEmail: (token) => client.get("/auth/verify-email", { params: { token } }).then((r) => r.data),

  resendVerification: (email) =>
    client.post("/auth/resend-verification", { email }).then((r) => r.data),
};

export const resumesApi = {
  list: () => client.get("/resumes").then((r) => r.data),
  get: (id) => client.get(`/resumes/${id}`).then((r) => r.data),
  versions: (id) => client.get(`/resumes/${id}/versions`).then((r) => r.data),
  upload: (file, label, parentId) => {
    const form = new FormData();
    form.append("file", file);
    if (label) form.append("label", label);
    if (parentId) form.append("parent_id", parentId);
    return client
      .post("/resumes/upload", form, { headers: { "Content-Type": "multipart/form-data" } })
      .then((r) => r.data);
  },
  remove: (id) => client.delete(`/resumes/${id}`),
  fileBlob: (id) => client.get(`/resumes/${id}/file`, { responseType: "blob" }).then((r) => r.data),
};

export const jobsApi = {
  list: () => client.get("/jobs").then((r) => r.data),
  get: (id) => client.get(`/jobs/${id}`).then((r) => r.data),
  createFromText: (title, rawText) => client.post("/jobs", { title, raw_text: rawText }).then((r) => r.data),
  createFromUrl: (url) => client.post("/jobs/from-url", { url }).then((r) => r.data),
  remove: (id) => client.delete(`/jobs/${id}`),
};

export const analysesApi = {
  list: () => client.get("/analyses").then((r) => r.data),
  get: (id) => client.get(`/analyses/${id}`).then((r) => r.data),
  create: (resumeId, jobId, useAi) =>
    client.post("/analyses", { resume_id: resumeId, job_id: jobId, use_ai: useAi }).then((r) => r.data),
  interviewTips: (id) => client.get(`/analyses/${id}/interview-tips`).then((r) => r.data),
};
