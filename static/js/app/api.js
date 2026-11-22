/* Shared API client for the JWT pages. If your URL names change, edit PATHS only. */
(function () {
  "use strict";

  var BASE = ((window.GOF_API && window.GOF_API.base) || "/api/v1").replace(/\/$/, "");

  var PATHS = {
    studentLogin: "/auth/student/login/",
    staffLogin: "/auth/staff/login/",
    logout: "/auth/logout/",
    refresh: "/auth/token/refresh/",
    register: "/registration/student-registration/",
    olympiads: "/olympiads/",
    studentDashboard: "/registration/student/dashboard/",
    adminStats: "/registration/admin/dashboard/",
    adminList: "/registration/admin/registrations/",
    adminExport: "/registration/admin/registrations/export/",
    adminStatus: function (id) { return "/registration/admin/registrations/" + id + "/status/"; }
  };

  var PAGES = { studentLogin: "/login/", staffLogin: "/staff/login/", student: "/student/", staff: "/staff/", register: "/register/" };

  // sessionStorage is cleared when the tab closes. Tokens never go in a URL or into the page.
  function get(key) { try { return sessionStorage.getItem(key); } catch (e) { return null; } }
  function set(key, value) { try { sessionStorage.setItem(key, value); } catch (e) { /* storage blocked */ } }
  function del(key) { try { sessionStorage.removeItem(key); } catch (e) { /* ignore */ } }

  function saveSession(data) {
    if (data.access) set("gof_access", data.access);
    if (data.refresh) set("gof_refresh", data.refresh);
    if (data.user && data.user.role) set("gof_role", data.user.role);
  }
  function clearSession() { ["gof_access", "gof_refresh", "gof_role"].forEach(del); }

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") node.textContent = attrs[k];
      else if (k === "class") node.className = attrs[k];
      else node.setAttribute(k, attrs[k]);
    });
    [].concat(children || []).forEach(function (c) {
      node.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    return node;
  }

  function parse(response) {
    return response.text().then(function (text) {
      try { return text ? JSON.parse(text) : {}; } catch (e) { return {}; }
    });
  }

  var refreshing = null;
  function refreshTokens() {
    if (refreshing) return refreshing;
    var refresh = get("gof_refresh");
    if (!refresh) return Promise.resolve(false);
    refreshing = fetch(BASE + PATHS.refresh, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refresh })
    }).then(function (r) {
      return parse(r).then(function (data) {
        if (!r.ok || !data.access) return false;
        saveSession({ access: data.access, refresh: data.refresh }); // refresh tokens rotate
        return true;
      });
    }).catch(function () { return false; }).then(function (ok) { refreshing = null; return ok; });
    return refreshing;
  }

  function finish(response, opts) {
    if (opts.raw) return response;
    return parse(response).then(function (data) {
      return { ok: response.ok, status: response.status, data: data };
    });
  }

  /* call(path, {method, body, auth, raw}) -> {ok, status, data}, or the raw Response. */
  function call(path, opts, retried) {
    opts = opts || {};
    var useAuth = opts.auth !== false;
    var headers = { Accept: "application/json" };
    if (opts.body !== undefined) headers["Content-Type"] = "application/json";
    if (useAuth && get("gof_access")) headers.Authorization = "Bearer " + get("gof_access");

    return fetch(BASE + path, {
      method: opts.method || "GET",
      headers: headers,
      body: opts.body !== undefined ? JSON.stringify(opts.body) : undefined
    }).then(function (response) {
      if (response.status === 401 && useAuth && !retried) {
        return refreshTokens().then(function (ok) {
          return ok ? call(path, opts, true) : finish(response, opts);
        });
      }
      return finish(response, opts);
    });
  }

  /* Page guard. The server still enforces access; this just sends people to the right login. */
  function requireRole(role) {
    if (get("gof_access") && get("gof_role") === role) return true;
    var login = role === "admin" ? PAGES.staffLogin : PAGES.studentLogin;
    window.location.replace(login + "?next=" + encodeURIComponent(window.location.pathname));
    return false;
  }

  function logout() {
    var refresh = get("gof_refresh");
    var role = get("gof_role");
    var done = function () {
      clearSession();
      window.location.href = role === "admin" ? PAGES.staffLogin : PAGES.studentLogin;
    };
    if (!refresh) return done();
    return call(PATHS.logout, { method: "POST", body: { refresh: refresh } }).then(done, done);
  }

  /* API error body -> {fields: {name: message}, general: message}. */
  function readErrors(data, status) {
    var out = { fields: {}, general: "" };
    if (status === 429) { out.general = "Too many attempts. Please wait a minute and try again."; return out; }
    if (!data || typeof data !== "object") { out.general = "Something went wrong. Please try again."; return out; }
    Object.keys(data).forEach(function (key) {
      var value = [].concat(data[key]).join(" ");
      if (["error", "detail", "message", "non_field_errors"].indexOf(key) >= 0) out.general = (out.general + " " + value).trim();
      else out.fields[key] = value;
    });
    if (!out.general && !Object.keys(out.fields).length) out.general = "Something went wrong. Please try again.";
    return out;
  }

  function clearErrors(form) {
    form.querySelectorAll("[data-error]").forEach(function (p) { p.textContent = ""; });
    form.querySelectorAll("[aria-invalid]").forEach(function (i) { i.removeAttribute("aria-invalid"); });
    var alert = document.getElementById("form-alert");
    if (alert) { alert.textContent = ""; alert.classList.add("hidden"); }
  }

  function showErrors(form, errors) {
    var first = null;
    Object.keys(errors.fields).forEach(function (name) {
      var slot = form.querySelector('[data-error="' + name + '"]');
      var input = form.elements[name];
      if (slot) slot.textContent = errors.fields[name];
      else errors.general = (errors.general + " " + errors.fields[name]).trim();
      if (input && input.setAttribute) { input.setAttribute("aria-invalid", "true"); first = first || input; }
    });
    var alert = document.getElementById("form-alert");
    if (alert && errors.general) { alert.textContent = errors.general; alert.classList.remove("hidden"); }
    if (first) first.focus(); else if (alert && errors.general) alert.focus();
  }

  function safeNext(fallback) {
    var next = new URLSearchParams(window.location.search).get("next") || "";
    return next === PAGES.student || next === PAGES.staff ? next : fallback;
  }

  function renderNav() {
    var list = document.getElementById("nav-links");
    if (!list) return;
    var role = get("gof_role");
    if (!(get("gof_access") && role)) return; // guests keep the server-rendered links
    list.querySelectorAll("[data-guest]").forEach(function (n) { n.remove(); });
    var home = role === "admin" ? PAGES.staff : PAGES.student;
    list.appendChild(el("li", {}, el("a", { href: home, text: role === "admin" ? "Staff dashboard" : "My registration" })));
    var btn = el("button", { type: "button", class: "link", text: "Log out" });
    btn.addEventListener("click", logout);
    list.appendChild(el("li", {}, btn));
  }

  function lockButton(button, busyText) {
    var original = button.textContent;
    button.disabled = true;
    button.textContent = busyText;
    return function () { button.disabled = false; button.textContent = original; };
  }

  window.GOF = {
    PATHS: PATHS, PAGES: PAGES, call: call, el: el, requireRole: requireRole, logout: logout,
    saveSession: saveSession, clearSession: clearSession, readErrors: readErrors,
    clearErrors: clearErrors, showErrors: showErrors, safeNext: safeNext, renderNav: renderNav,
    lockButton: lockButton, get: get, set: set, del: del
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", renderNav);
  else renderNav();
})();
