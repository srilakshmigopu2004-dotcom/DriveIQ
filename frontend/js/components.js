// Small reusable UI helpers. ALL dynamic text goes through esc() to prevent XSS.
export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export const card = (inner, cls = "") => `<div class="card ${cls}">${inner}</div>`;
export const bar = (pct) => `<div class="bar"><i style="width:${Math.max(0, Math.min(100, Number(pct) || 0))}%"></i></div>`;
export const badge = (text, kind = "") => `<span class="badge ${kind}">${esc(text)}</span>`;
export const ul = (items) => (items?.length ? `<ul>${items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : "");
export const errBox = (m) => `<div class="err">${esc(m)}</div>`;
export const fmtDate = (d) => (d ? new Date(d).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" }) : "TBA");
export const statusKind = (s) => ({ registration_open: "ok", upcoming: "warn", cancelled: "bad" }[s] || "");

export function scoreCard(m) {
  return card(`<div class="muted">Match score (profile alignment)</div><div class="big">${esc(m.match_score)}%</div>${bar(m.match_score)}
    <p class="muted">${esc(m.disclaimer)}</p>
    <h2>Factors</h2>${m.factors.map((f) => `<div style="margin-bottom:8px"><b>${esc(f.label)}</b>: ${f.score === null ? "not scored" : esc(f.score) + "%"}${f.score === null ? "" : bar(f.score)}<div class="muted">${esc(f.explanation)}</div></div>`).join("")}
    <h2>Why this matches you</h2>${ul(m.strengths) || '<p class="muted">Nothing strongly aligned yet.</p>'}
    <h2>What you should improve</h2>${ul(m.improvements) || '<p class="muted">Nothing flagged.</p>'}`);
}

export function eligibilityCard(e) {
  return card(`<span class="badge ${e.eligible ? "ok" : "bad"}">${esc(e.verdict)}</span> <span class="muted">${esc(e.registration_note)}</span>
    ${ul(e.reasons)}<table><tbody>${e.checks.map((c) => `<tr><td>${c.passed ? "✅" : "❌"} ${esc(c.name)}</td><td>${esc(c.detail)}</td></tr>`).join("")}</tbody></table>
    ${e.skill_gaps.length ? `<p class="warn">Skill gaps: ${esc(e.skill_gaps.join(", "))}</p>` : ""}
    ${e.profile_incomplete ? '<p class="warn">Your profile is incomplete, so some checks cannot be verified.</p>' : ""}`);
}
