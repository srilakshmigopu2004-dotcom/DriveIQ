import { api, list } from "../api.js";
import { badge, card, eligibilityCard, errBox, esc, fmtDate, scoreCard, statusKind, ul } from "../components.js";
import { expCard } from "./companyPages.js";

export async function drivesPage(el) {
  const ds = await list("/drives/");
  el.innerHTML = `<h1>Placement drives</h1><div class="grid">${ds.map((d) => card(`<a href="#/drives/${d.id}"><b>${esc(d.company_name)}</b></a><div>${esc(d.title)}</div>
    ${badge(d.status_display, statusKind(d.status))} <span class="muted">${fmtDate(d.drive_date)}</span><div class="muted">${esc(d.college_name)}</div>`)).join("") || '<p class="muted">No drives yet.</p>'}</div>`;
}

export async function driveDetailPage(el, id) {
  el.innerHTML = "<p>Loading…</p>";
  const [d, elig, match, diff, offer, road, exps] = await Promise.all([
    api(`/drives/${id}/`), api(`/eligibility/${id}/`), api(`/matching/${id}/`), api(`/drives/${id}/difficulty/`),
    api(`/offers/drive/${id}/`), api(`/preparation/roadmap/${id}/`), list(`/experiences/?drive=${id}`)]);
  const dec = offer.decoder;
  el.innerHTML = `<h1>${esc(d.company_name)} - ${esc(d.title)}</h1><div id="msg"></div>
  <p>${badge(d.status_display, statusKind(d.status))} <span class="muted">Drive ${fmtDate(d.drive_date)} · Deadline ${fmtDate(d.application_deadline)} · ${esc(d.location || "Location not specified")} · ${esc(d.openings ?? "?")} openings</span></p>
  <p>${esc(d.description)}</p>
  ${d.has_applied ? badge("You have applied", "ok") : '<button id="apply">Apply / Register</button>'}
  <h2>Eligibility</h2>${eligibilityCard(elig)}
  <h2>Match analysis</h2>${scoreCard(match)}
  <h2>Drive difficulty: ${esc(diff.label)}</h2>${card(`<p class="muted">${esc(diff.note)}</p><ul>${diff.factors.map((f) => `<li><b>${esc(f.name)}</b> (${esc(f.level_label)}): ${esc(f.detail)}</li>`).join("")}</ul>`)}
  <h2>Selection rounds</h2>${card(d.rounds.map((r) => `<div>${esc(r.order)}. <b>${esc(r.name)}</b> <span class="muted">${esc(r.round_type)}</span></div>`).join("") || '<span class="muted">Rounds not listed.</span>')}
  <h2>Offer decoder</h2>${card(`<div><b>Total CTC:</b> ${esc(dec.total_formatted || "Not specified")}</div>
    <table><tbody>${dec.components.map((c) => `<tr><td>${esc(c.name)}</td><td>${esc(c.formatted)}</td><td>${badge(c.kind, c.kind === "actual" ? "ok" : "warn")}</td></tr>`).join("")}</tbody></table>${ul(dec.notes)}`)}
  <h2>Offer terms to review</h2>${card(`${offer.red_flags.flags.map((f) => `<div class="${f.severity === "warning" ? "warn" : ""}">${f.severity === "warning" ? "⚠ " : "ℹ "}<b>${esc(f.title)}</b>: ${esc(f.detail)}</div>`).join("") || '<span class="muted">No notable terms listed.</span>'}
    ${offer.red_flags.not_specified.length ? `<p class="muted">Not specified in data: ${esc(offer.red_flags.not_specified.join(", "))}</p>` : ""}<p class="muted">${esc(offer.red_flags.disclaimer)}</p>`)}
  <h2>Preparation roadmap</h2><div id="road"></div>
  <h2>Previous experiences</h2>${exps.filter((x) => x.status === "approved").map(expCard).join("") || '<p class="muted">No approved experiences yet.</p>'}`;
  const showRoad = (r) => (el.querySelector("#road").innerHTML = r.saved_plan
    ? card(Object.entries(groupBy(r.saved_plan.tasks, "week")).map(([w, ts]) => `<b>Week ${esc(w)}: ${esc(ts[0].focus)}</b>${ts.map((t) => `<div><label><input type="checkbox" data-task="${t.id}" ${t.is_done ? "checked" : ""} style="width:auto"/> ${esc(t.title)}</label></div>`).join("")}`).join("<br>"))
    : card(`<p class="muted">${esc(r.note)}</p>${r.weeks.map((w) => `<b>Week ${esc(w.week)}: ${esc(w.focus)}</b>${ul(w.tasks.map((t) => t.title))}`).join("")}<button id="saveRoad">Save as my plan</button>`));
  showRoad(road);
  el.addEventListener("change", (e) => { const t = e.target.dataset?.task; if (t) api(`/preparation/tasks/${t}/`, { method: "PATCH", body: { is_done: e.target.checked } }); });
  el.addEventListener("click", async (e) => {
    if (e.target.id === "saveRoad") { await api(`/preparation/roadmap/${id}/`, { method: "POST" }); showRoad(await api(`/preparation/roadmap/${id}/`)); }
    if (e.target.id === "apply") { try { await api(`/drives/${id}/apply/`, { method: "POST" }); driveDetailPage(el, id); } catch (x) { el.querySelector("#msg").innerHTML = errBox(x.message); } }
  });
}

const groupBy = (arr, k) => arr.reduce((a, x) => ((a[x[k]] ||= []).push(x), a), {});

export async function comparePage(el) {
  const ds = await list("/drives/");
  el.innerHTML = `<h1>Compare drives</h1>${card(`<p class="muted">Pick 2 to 4 drives. DriveIQ shows facts side by side and does not declare a best company.</p>
    ${ds.map((d) => `<label style="display:block"><input type="checkbox" class="cmp" value="${d.id}" style="width:auto"/> ${esc(d.company_name)} - ${esc(d.title)}</label>`).join("")}<button id="go">Compare</button>`)}<div id="out"></div>`;
  el.querySelector("#go").onclick = async () => {
    const ids = [...el.querySelectorAll(".cmp:checked")].map((c) => c.value).join(",");
    try {
      const r = await api(`/matching/compare/?drives=${ids}`);
      const rows = [["CTC", "ctc"], ["Eligibility", "eligible"], ["Min CGPA", "min_cgpa"], ["Role", "role"], ["Match", "match_score"], ["Difficulty", "difficulty"], ["Rounds", "rounds"], ["Location", "location"], ["Service bond", "bond"]];
      el.querySelector("#out").innerHTML = card(`<div class="scroll"><table><thead><tr><th>Factor</th>${r.drives.map((d) => `<th>${esc(d.company)}</th>`).join("")}</tr></thead><tbody>
        ${rows.map(([l, k]) => `<tr><td>${l}</td>${r.drives.map((d) => `<td>${esc(d[k])}${k === "match_score" ? "%" : ""}</td>`).join("")}</tr>`).join("")}</tbody></table></div><p class="muted">${esc(r.note)}</p>`);
    } catch (e) { el.querySelector("#out").innerHTML = errBox(e.message); }
  };
}
