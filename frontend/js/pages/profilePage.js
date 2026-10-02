import { api, list } from "../api.js";
import { card, errBox, esc } from "../components.js";

const LEVELS = ["", "Beginner", "Intermediate", "Strong"];
const lvlSelect = (id, v) => `<select id="${id}">${[1, 2, 3].map((n) => `<option value="${n}" ${n === v ? "selected" : ""}>${LEVELS[n]}</option>`).join("")}</select>`;

export async function profilePage(el) {
  const [p, colleges, skills] = await Promise.all([api("/students/profile/"), list("/students/colleges/"), list("/companies/skills/")]);
  const v = (x) => esc(x ?? "");
  el.innerHTML = `<h1>My placement profile</h1><div id="msg"></div>
  ${card(`<div class="row">
    <div><label>Full name</label><input id="full_name" value="${v(p.full_name)}"/></div>
    <div><label>College</label><select id="college"><option value="">-- select --</option>${colleges.map((c) => `<option value="${c.id}" ${c.id === p.college ? "selected" : ""}>${esc(c.name)}</option>`).join("")}</select></div>
    <div><label>Degree</label><input id="degree" value="${v(p.degree)}"/></div>
    <div><label>Branch (e.g. CSE)</label><input id="branch" value="${v(p.branch)}"/></div>
    <div><label>Graduation year</label><input id="graduation_year" type="number" value="${v(p.graduation_year)}"/></div>
    <div><label>CGPA</label><input id="cgpa" type="number" step="0.01" min="0" max="10" value="${v(p.cgpa)}"/></div>
    <div><label>Backlogs</label><input id="backlogs" type="number" min="0" value="${v(p.backlogs)}"/></div>
    <div><label>DSA level</label>${lvlSelect("dsa_level", p.dsa_level)}</div>
    <div><label>Aptitude level</label>${lvlSelect("aptitude_level", p.aptitude_level)}</div>
    <div><label>Communication level</label>${lvlSelect("communication_level", p.communication_level)}</div>
    <div><label>Preferred roles (comma separated)</label><input id="preferred_roles" value="${v(p.preferred_roles)}"/></div>
    <div><label>Preferred locations (comma separated)</label><input id="preferred_locations" value="${v(p.preferred_locations)}"/></div></div>
    <button id="save">Save profile</button>`)}
  <h2>Skills</h2>${card(`<div id="sk">${p.skills_detail.map((s) => `<span class="badge">${esc(s.skill_name)} · ${LEVELS[s.level]} <a href="#" data-del-skill="${s.id}">✕</a></span> `).join("") || '<span class="muted">No skills added yet.</span>'}</div>
    <div class="row" style="margin-top:10px"><select id="ns">${skills.map((s) => `<option value="${s.id}">${esc(s.name)}</option>`).join("")}</select>${lvlSelect("nl", 2)}<div><button id="adds">Add skill</button></div></div>`)}
  <h2>Projects</h2>${card(`${p.projects.map((x) => `<div><b>${esc(x.title)}</b> <span class="muted">${esc(x.technologies)}</span> <a href="#" data-del-proj="${x.id}">✕</a></div>`).join("") || '<span class="muted">No projects yet.</span>'}
    <div class="row" style="margin-top:10px"><input id="pt" placeholder="Project title"/><input id="ptech" placeholder="Technologies"/><div><button id="addp">Add project</button></div></div>`)}
  <h2>Internships</h2>${card(`${p.internships.map((x) => `<div><b>${esc(x.company_name)}</b> ${esc(x.role)} (${esc(x.duration_months)} mo) <a href="#" data-del-int="${x.id}">✕</a></div>`).join("") || '<span class="muted">No internships yet.</span>'}
    <div class="row" style="margin-top:10px"><input id="ic" placeholder="Company"/><input id="ir" placeholder="Role"/><input id="im" type="number" min="1" value="2"/><div><button id="addi">Add internship</button></div></div>`)}`;
  const $ = (s) => el.querySelector(s);
  const msg = (h) => ($("#msg").innerHTML = h);
  const reload = () => profilePage(el);
  $("#save").onclick = async () => {
    const num = (id) => ($(id).value === "" ? null : Number($(id).value));
    try {
      await api("/students/profile/", { method: "PATCH", body: {
        full_name: $("#full_name").value, college: $("#college").value || null, degree: $("#degree").value, branch: $("#branch").value,
        graduation_year: num("#graduation_year"), cgpa: $("#cgpa").value || null, backlogs: num("#backlogs") ?? 0,
        dsa_level: +$("#dsa_level").value, aptitude_level: +$("#aptitude_level").value, communication_level: +$("#communication_level").value,
        preferred_roles: $("#preferred_roles").value, preferred_locations: $("#preferred_locations").value } });
      msg('<div class="card ok">Profile saved ✔</div>');
    } catch (e) { msg(errBox(e.message)); }
  };
  const act = (fn) => async (e) => { e.preventDefault?.(); try { await fn(e); reload(); } catch (x) { msg(errBox(x.message)); } };
  $("#adds").onclick = act(() => api("/students/skills/", { method: "POST", body: { skill: +$("#ns").value, level: +$("#nl").value } }));
  $("#addp").onclick = act(() => api("/students/projects/", { method: "POST", body: { title: $("#pt").value, technologies: $("#ptech").value } }));
  $("#addi").onclick = act(() => api("/students/internships/", { method: "POST", body: { company_name: $("#ic").value, role: $("#ir").value, duration_months: +$("#im").value } }));
  el.querySelectorAll("[data-del-skill]").forEach((a) => (a.onclick = act(() => api(`/students/skills/${a.dataset.delSkill}/`, { method: "DELETE" }))));
  el.querySelectorAll("[data-del-proj]").forEach((a) => (a.onclick = act(() => api(`/students/projects/${a.dataset.delProj}/`, { method: "DELETE" }))));
  el.querySelectorAll("[data-del-int]").forEach((a) => (a.onclick = act(() => api(`/students/internships/${a.dataset.delInt}/`, { method: "DELETE" }))));
}
