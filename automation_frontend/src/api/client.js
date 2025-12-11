 // PUBLIC_INTERFACE
 /**
  * Lightweight API client for the Automation Frontend (PUBLIC_INTERFACE).
  * Reads base URL from REACT_APP_API_BASE, defaulting to http://localhost:3001.
  */
const API_BASE =
  (process && process.env && process.env.REACT_APP_API_BASE) ||
  (typeof process !== "undefined" && process.env && process.env.REACT_APP_API_BASE) ||
  "http://localhost:3001";

export { API_BASE };

/**
 * PUBLIC_INTERFACE
 * Upload a requirements file (CSV/XLS/XLSX).
 * @param {File} file - selected file object
 * @returns {Promise<Object>} created job object
 */
export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    throw new Error(`Upload failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

/**
 * PUBLIC_INTERFACE
 * Trigger parse for a job id.
 * @param {number} jobId
 * @returns {Promise<Object>} job object after parse
 */
export async function parseJob(jobId) {
  const res = await fetch(`${API_BASE}/api/parse/${jobId}`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Parse failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

/**
 * PUBLIC_INTERFACE
 * Trigger generation for a job id.
 * @param {number} jobId
 * @returns {Promise<Object>} job object after generation
 */
export async function generateJob(jobId) {
  const res = await fetch(`${API_BASE}/api/generate/${jobId}`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Generate failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

/**
 * PUBLIC_INTERFACE
 * Trigger execution for a job id.
 * @param {number} jobId
 * @returns {Promise<Object>} run object
 */
export async function executeJob(jobId) {
  const res = await fetch(`${API_BASE}/api/execute/${jobId}`, { method: "POST" });
  if (!res.ok) {
    throw new Error(`Execute failed: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

/**
 * PUBLIC_INTERFACE
 * Get Allure index URL for latest run for a job.
 * @param {number} jobId
 * @returns {string} URL to open Allure report index
 */
export function getAllureIndexUrl(jobId) {
  return `${API_BASE}/api/jobs/${jobId}/allure/index.html`;
}
