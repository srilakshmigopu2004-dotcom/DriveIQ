import { login, register } from "../api.js";
import { card, errBox } from "../components.js";

export function loginPage(el) {
  el.innerHTML = `<h1>Welcome to DriveIQ</h1><p class="muted">Know your eligibility, match, preparation needs and offer terms before a campus drive.</p>
  <div class="grid"><div>${card(`<h2>Login</h2><div id="e"></div>
    <label>Username</label><input id="u" autocomplete="username"/><label>Password</label><input id="p" type="password" autocomplete="current-password"/>
    <button id="go">Login</button>`)}</div>
  <div>${card(`<h2>Register</h2><div id="e2"></div>
    <label>Full name</label><input id="rn"/><label>Username</label><input id="ru"/><label>Email</label><input id="re" type="email"/>
    <label>Password</label><input id="rp" type="password" autocomplete="new-password"/><button id="reg">Create account</button>`)}</div></div>`;
  el.querySelector("#go").onclick = async () => {
    try { await login(el.querySelector("#u").value, el.querySelector("#p").value); location.hash = "#/dashboard"; }
    catch (e) { el.querySelector("#e").innerHTML = errBox(e.message); }
  };
  el.querySelector("#reg").onclick = async () => {
    try {
      const v = (id) => el.querySelector(id).value;
      await register({ full_name: v("#rn"), username: v("#ru"), email: v("#re"), password: v("#rp") });
      await login(v("#ru"), v("#rp")); location.hash = "#/profile";
    } catch (e) { el.querySelector("#e2").innerHTML = errBox(e.message); }
  };
}
