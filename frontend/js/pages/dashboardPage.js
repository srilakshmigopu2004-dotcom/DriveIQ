import { api } from "../api.js";
import { badge, bar, card, esc, fmtDate, ul } from "../components.js";

export async function dashboardPage(el) {
  const d = await api("/students/dashboard/");
  const r = d.readiness;
  el.innerHTML = `<h1>Dashboard</h1>
  ${d.profile_complete ? "" : card('<b class="warn">Your profile is incomplete.</b> <a href="#/profile">Complete it</a> to get accurate eligibility and matches.')}
  <div class="grid">
   ${card(`<div class="muted">Preparation readiness</div><div class="big">${esc(r.overall)}%</div>${bar(r.overall)}<p>${badge(r.classification)}</p>
     <div class="muted">Strongest: ${esc(r.strengths.join(", ") || "none yet")}</div><div class="muted">Focus on: ${esc(r.recommended_focus.join(", ") || "all good")}</div>`)}
   ${card(`<div class="muted">Eligible drives</div><div class="big">${esc(d.eligible_count)} / ${esc(d.upcoming_drives.length)}</div>`)}
   ${card(`<h2 style="margin-top:0">Saved companies</h2>${d.saved_companies.map((c) => `<div><a href="#/companies/${c.id}">${esc(c.name)}</a></div>`).join("") || '<span class="muted">None saved.</span>'}`)}
  </div>
  <h2>Upcoming drives</h2>
  ${d.upcoming_drives.map((u) => card(`<a href="#/drives/${u.drive_id}"><b>${esc(u.company)}</b> - ${esc(u.title)}</a> ${badge(u.eligible ? "Eligible" : "Not eligible", u.eligible ? "ok" : "bad")}
     <span class="muted">${fmtDate(u.drive_date)}</span><div>Match ${esc(u.match_score)}%${bar(u.match_score)}</div>`)).join("") || '<p class="muted">No drives for your college yet.</p>'}
  <h2>Recommended for you</h2>
  ${d.recommended.map((x) => card(`<a href="#/drives/${x.drive_id}"><b>${esc(x.company)}</b> - ${esc(x.title)}</a> · ${esc(x.match_score)}%${ul(x.why)}`)).join("") || '<p class="muted">Recommendations appear once you are eligible for a drive.</p>'}
  <div class="grid"><div><h2>Preparation tasks</h2>${card(d.preparation_tasks.map((t) => `<div>• ${esc(t.title)} <span class="muted">(week ${esc(t.week)})</span></div>`).join("") || '<span class="muted">Generate a roadmap from a drive page.</span>')}</div>
  <div><h2>Applications</h2>${card(d.applications.map((a) => `<div>${esc(a.company)} - ${esc(a.title)} ${badge(a.status)}</div>`).join("") || '<span class="muted">No applications yet.</span>')}</div>
  <div><h2>Recent activity</h2>${card(d.recent_activity.map((a) => `<div>${esc(a.title)}</div>`).join("") || '<span class="muted">Nothing yet.</span>')}</div></div>`;
}
