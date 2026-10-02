import { API } from "./config.js";

export const auth = {
  get token() { return localStorage.getItem("access"); },
  set(tokens) { localStorage.setItem("access", tokens.access); localStorage.setItem("refresh", tokens.refresh); },
  clear() { localStorage.removeItem("access"); localStorage.removeItem("refresh"); },
};

async function refresh() {
  const r = localStorage.getItem("refresh");
  if (!r) return false;
  const res = await fetch(`${API}/auth/refresh/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ refresh: r }) });
  if (!res.ok) return false;
  localStorage.setItem("access", (await res.json()).access);
  return true;
}

export async function api(path, { method = "GET", body, retry = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`;
  const res = await fetch(`${API}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  if (res.status === 401 && retry && (await refresh())) return api(path, { method, body, retry: false });
  if (res.status === 401) { auth.clear(); location.hash = "#/login"; throw new Error("Please log in again."); }
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) throw new Error(formatErr(data) || `Request failed (${res.status})`);
  return data;
}

function formatErr(d) {
  if (!d) return "";
  if (typeof d === "string") return d;
  if (d.detail) return d.detail + (d.reasons ? " " + d.reasons.join(" ") : "");
  return Object.entries(d).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(" ") : v}`).join(" | ");
}

export const list = async (path) => { const d = await api(path); return d.results ?? d; };

export async function login(username, password) {
  const res = await fetch(`${API}/auth/login/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) });
  if (!res.ok) throw new Error("Invalid username or password.");
  auth.set(await res.json());
}

export async function register(body) {
  const res = await fetch(`${API}/auth/register/`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!res.ok) throw new Error(formatErr(await res.json().catch(() => null)) || "Registration failed.");
}
