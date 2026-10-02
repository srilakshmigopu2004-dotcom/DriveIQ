import { api, auth } from "./api.js";
import { errBox, esc } from "./components.js";
import { loginPage } from "./pages/authPages.js";
import { companiesPage, companyDetailPage } from "./pages/companyPages.js";
import { dashboardPage } from "./pages/dashboardPage.js";
import { comparePage, driveDetailPage, drivesPage } from "./pages/drivePages.js";
import { experiencesPage, notificationsPage, offerPage } from "./pages/miscPages.js";
import { profilePage } from "./pages/profilePage.js";

const routes = [
  [/^#\/login$/, loginPage, false], [/^#\/dashboard$/, dashboardPage], [/^#\/profile$/, profilePage],
  [/^#\/companies$/, companiesPage], [/^#\/companies\/(\d+)$/, companyDetailPage],
  [/^#\/drives$/, drivesPage], [/^#\/drives\/(\d+)$/, driveDetailPage], [/^#\/compare$/, comparePage],
  [/^#\/experiences$/, experiencesPage], [/^#\/offer$/, offerPage], [/^#\/notifications$/, notificationsPage],
];
const links = [["dashboard", "Dashboard"], ["drives", "Drives"], ["companies", "Companies"], ["compare", "Compare"],
  ["experiences", "Experiences"], ["offer", "Offer decoder"], ["profile", "Profile"], ["notifications", "Notifications"]];

async function renderNav(active) {
  const nav = document.getElementById("nav");
  if (!auth.token) { nav.innerHTML = '<span class="logo">DriveIQ</span>'; return; }
  let unread = 0;
  try { unread = (await api("/notifications/unread-count/")).unread; } catch {}
  nav.innerHTML = `<span class="logo">DriveIQ</span>${links.map(([h, l]) => `<a href="#/${h}" class="${active === h ? "on" : ""}">${esc(l)}${h === "notifications" && unread ? ` (${unread})` : ""}</a>`).join("")}<span class="sp"></span><a href="#" id="out">Logout</a>`;
  nav.querySelector("#out").onclick = (e) => { e.preventDefault(); auth.clear(); location.hash = "#/login"; };
}

async function router() {
  const hash = location.hash || "#/login";
  const el = document.getElementById("app");
  if (!auth.token && hash !== "#/login") { location.hash = "#/login"; return; }
  for (const [re, page, needsAuth = true] of routes) {
    const m = hash.match(re);
    if (!m) continue;
    renderNav(hash.split("/")[1]);
    try { await page(el, m[1]); } catch (e) { el.innerHTML = errBox(e.message); }
    return;
  }
  location.hash = auth.token ? "#/dashboard" : "#/login";
}
window.addEventListener("hashchange", router);
router();
