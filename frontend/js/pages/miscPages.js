import { api, list } from "../api.js";
import { badge, card, errBox, esc, ul } from "../components.js";
import { expCard } from "./companyPages.js";

export async function notificationsPage(el) {
  const ns = await list("/notifications/");
  el.innerHTML = `<h1>Notifications</h1><button id="all" class="sec">Mark all read</button>${ns.map((n) => card(`${n.is_read ? "" : badge("new", "warn")} <b>${esc(n.title)}</b><div class="muted">${esc(n.message)}</div>${n.related_drive ? `<a href="#/drives/${n.related_drive}">Open drive</a>` : ""}`)).join("") || '<p class="muted">No notifications.</p>'}`;
  el.querySelector("#all").onclick = async () => { await api("/notifications/read-all/", { method: "POST" }); notificationsPage(el); };
}

export async function experiencesPage(el) {
  const [cs, exps] = await Promise.all([list("/companies/"), list("/experiences/")]);
  el.innerHTML = `<h1>Previous drive experiences</h1><div id="msg"></div>
  ${card(`<h2 style="margin-top:0">Share your experience</h2><p class="muted">Only share what really happened. Submissions are reviewed by an admin before others see them.</p>
   <div class="row"><div><label>Company</label><select id="c">${cs.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join("")}</select></div>
   <div><label>Year</label><input id="y" type="number" value="${new Date().getFullYear() - 1}"/></div>
   <div><label>Difficulty (1-5)</label><input id="df" type="number" min="1" max="5" value="3"/></div>
   <div><label>Number of rounds</label><input id="rc" type="number" min="1" value="3"/></div></div>
   <label>Summary</label><textarea id="s" rows="4"></textarea><label>A question asked (optional)</label><input id="q"/>
   <button id="sub">Submit for review</button>`)}
  <h2>Approved & your submissions</h2>${exps.map((x) => `${x.status !== "approved" ? badge(x.status, "warn") : ""}${expCard(x)}`).join("") || '<p class="muted">Nothing yet.</p>'}`;
  el.querySelector("#sub").onclick = async () => {
    const v = (id) => el.querySelector(id).value;
    try {
      await api("/experiences/", { method: "POST", body: { company: +v("#c"), year: +v("#y"), difficulty: +v("#df"), rounds_count: +v("#rc"), summary: v("#s"),
        questions: v("#q") ? [{ text: v("#q") }] : [] } });
      experiencesPage(el);
    } catch (e) { el.querySelector("#msg").innerHTML = errBox(e.message); }
  };
}

export async function offerPage(el) {
  el.innerHTML = `<h1>Offer decoder</h1>${card(`<p class="muted">Enter only what your offer letter states. Leave unknown fields blank; DriveIQ will not invent them.</p><div id="msg"></div>
   <div class="row"><div><label>Total CTC (₹ per year)</label><input id="t" type="number"/></div><div><label>Fixed (₹)</label><input id="f" type="number"/></div>
   <div><label>Variable (₹)</label><input id="v" type="number"/></div><div><label>Joining bonus (₹)</label><input id="j" type="number"/></div>
   <div><label>Optional: assume variable % (creates a labelled ESTIMATE)</label><input id="a" type="number" min="0" max="100"/></div></div><button id="go">Decode</button>`)}<div id="out"></div>`;
  el.querySelector("#go").onclick = async () => {
    const v = (id) => el.querySelector(id).value;
    try {
      const r = await api("/offers/decode/", { method: "POST", body: { ctc_total: v("#t"), fixed: v("#f"), variable: v("#v"), joining_bonus: v("#j"), assumed_variable_percent: v("#a") } });
      el.querySelector("#out").innerHTML = card(`<b>Total CTC: ${esc(r.total_formatted || "Not provided")}</b><table><tbody>${r.components.map((c) => `<tr><td>${esc(c.name)}</td><td>${esc(c.formatted)}</td><td>${badge(c.kind, c.kind === "actual" ? "ok" : "warn")}</td></tr>`).join("")}</tbody></table>${ul(r.notes)}<p class="muted">${esc(r.disclaimer)}</p>`);
    } catch (e) { el.querySelector("#msg").innerHTML = errBox(e.message); }
  };
}
