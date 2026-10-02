import { api, list } from "../api.js";
import { badge, card, esc, fmtDate, statusKind } from "../components.js";

export async function companiesPage(el) {
  const cs = await list("/companies/");
  el.innerHTML = `<h1>Companies</h1><div class="grid">${cs.map((c) => card(`<a href="#/companies/${c.id}"><b>${esc(c.name)}</b></a>
    <div class="muted">${esc(c.industry)} ${c.category ? "· " + esc(c.category) : ""}</div>${c.is_saved ? badge("Saved", "ok") : ""}`)).join("") || '<p class="muted">No companies yet. Ask your placement admin to add some.</p>'}</div>`;
}

export async function companyDetailPage(el, id) {
  const [c, drives, exps] = await Promise.all([api(`/companies/${id}/`), list(`/drives/?company=${id}`), list(`/experiences/?company=${id}`)]);
  const f = (label, v) => (v ? `<p><b>${label}</b><br>${esc(v)}</p>` : "");
  el.innerHTML = `<h1>${esc(c.name)}</h1><button id="sv" class="sec">${c.is_saved ? "Remove from saved" : "Save company"}</button>
  ${card(`${f("Industry", c.industry)}${f("Category", c.category)}${f("Products / services", c.products_services)}${f("Size (approx.)", c.company_size)}${f("Locations", c.locations)}
    ${f("Technologies", c.technologies.join(", "))}${f("Common roles", c.roles.map((r) => r.title).join(", "))}${f("Campus hiring", c.campus_hiring_info)}
    ${f("Typical selection process", c.typical_selection_process)}${f("CTC information", c.ctc_information)}${f("Important requirements", c.important_requirements)}
    ${c.careers_url ? `<p><a href="${esc(c.careers_url)}" target="_blank" rel="noopener noreferrer">Careers page</a></p>` : ""}`)}
  <h2>Drives</h2>${drives.map((d) => card(`<a href="#/drives/${d.id}">${esc(d.title)}</a> ${badge(d.status_display, statusKind(d.status))} <span class="muted">${fmtDate(d.drive_date)}</span>`)).join("") || '<p class="muted">No drives listed.</p>'}
  <h2>Previous student experiences (admin-approved)</h2>${exps.filter((x) => x.status === "approved").map(expCard).join("") || '<p class="muted">No approved experiences yet.</p>'}`;
  el.querySelector("#sv").onclick = async () => { await api(`/companies/${id}/save/`, { method: c.is_saved ? "DELETE" : "POST" }); companyDetailPage(el, id); };
}

export function expCard(x) {
  return card(`<b>${esc(x.year)}</b> · difficulty ${esc(x.difficulty)}/5 · ${esc(x.rounds_count)} round(s) ${x.duration_minutes ? "· ~" + esc(x.duration_minutes) + " min" : ""}
    <p>${esc(x.summary)}</p>${x.questions.length ? "<b>Questions asked</b><ul>" + x.questions.map((q) => `<li>${esc(q.text)} <span class="muted">${esc(q.round_name)} ${esc(q.topic)}</span></li>`).join("") + "</ul>" : ""}`);
}
