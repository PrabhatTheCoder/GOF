(function () {
  "use strict";
  if (!GOF.requireRole("admin")) return;

  var PAGE_SIZE = 20;
  var el = GOF.el;
  var form = document.getElementById("filters");
  var tbody = document.getElementById("rows");
  var summary = document.getElementById("summary");
  var pager = document.getElementById("pager");
  var alertBox = document.getElementById("form-alert");
  var STATUSES = [["pending", "Pending review"], ["confirmed", "Confirmed"], ["rejected", "Rejected"]];

  var rows = [];   // the API returns every matching row; we page them here
  var page = 1;

  function params() {
    var p = new URLSearchParams();
    ["search", "class", "subject", "status"].forEach(function (name) {
      var value = form.elements[name].value.trim();
      if (value) p.set(name, value);
    });
    return p;
  }

  function showAlert(text, kind) { alertBox.textContent = text; alertBox.className = "notice notice-" + kind; }
  function hideAlert() { alertBox.textContent = ""; alertBox.className = "notice hidden"; }

  function statusCell(r) {
    var select = el("select", { id: "status-" + r.id, "aria-label": "Status for " + r.reg_number },
      STATUSES.map(function (s) {
        var o = el("option", { value: s[0], text: s[1] });
        if (r.status === s[0]) o.selected = true;
        return o;
      }));
    var save = el("button", { type: "button", class: "btn btn-small", text: "Save" });
    save.addEventListener("click", function () {
      save.disabled = true;
      GOF.call(GOF.PATHS.adminStatus(r.id), { method: "PATCH", body: { status: select.value } }).then(function (res) {
        save.disabled = false;
        if (res.ok) {
          r.status = select.value;
          showAlert(r.reg_number + " is now " + select.options[select.selectedIndex].text.toLowerCase() + ".", "success");
          loadStats();
        } else {
          showAlert(GOF.readErrors(res.data, res.status).general, "error");
        }
      });
    });
    return el("div", { class: "status-form" }, [select, save]);
  }

  function render() {
    var total = rows.length;
    var pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    if (page > pages) page = pages;
    var start = (page - 1) * PAGE_SIZE;
    var slice = rows.slice(start, start + PAGE_SIZE);

    tbody.textContent = "";
    if (!slice.length) {
      tbody.appendChild(el("tr", {}, el("td", { colspan: "7", text: "No registrations match these filters. Try clearing them." })));
    }
    slice.forEach(function (r) {
      tbody.appendChild(el("tr", {}, [
        el("td", { text: r.reg_number }),
        el("td", {}, [r.student_name, el("br"), el("span", { class: "meta", text: r.email })]),
        el("td", { text: String(r.student_class) }),
        el("td", { text: r.school + ", " + r.city }),
        el("td", {}, [r.parent_name, el("br"), el("span", { class: "meta", text: r.parent_mobile })]),
        el("td", { text: r.olympiad_subject }),
        el("td", {}, statusCell(r))
      ]));
    });

    summary.textContent = "Showing " + (total ? start + 1 : 0) + " to " + Math.min(total, start + PAGE_SIZE) + " of " + total + " matching registrations.";

    pager.textContent = "";
    if (pages > 1) {
      var prev = el("button", { type: "button", class: "btn btn-small btn-ghost", text: "Previous" });
      var next = el("button", { type: "button", class: "btn btn-small btn-ghost", text: "Next" });
      prev.disabled = page <= 1;
      next.disabled = page >= pages;
      prev.addEventListener("click", function () { page -= 1; render(); });
      next.addEventListener("click", function () { page += 1; render(); });
      pager.appendChild(prev);
      pager.appendChild(el("span", { text: "Page " + page + " of " + pages }));
      pager.appendChild(next);
    }
  }

  function load() {
    var q = params().toString();
    GOF.call(GOF.PATHS.adminList + (q ? "?" + q : "")).then(function (res) {
      if (res.status === 401 || res.status === 403) { GOF.clearSession(); GOF.requireRole("admin"); return; }
      if (!res.ok) { showAlert(GOF.readErrors(res.data, res.status).general, "error"); return; }
      hideAlert();
      rows = res.data.results || [];
      page = 1;
      render();
    }).catch(function () { showAlert("Could not reach the server.", "error"); });
  }

  function loadStats() {
    GOF.call(GOF.PATHS.adminStats).then(function (res) {
      if (!res.ok) return;
      var s = res.data.statistics || {};
      ["total", "pending", "confirmed", "rejected"].forEach(function (k) {
        document.getElementById("stat-" + k).textContent = String(s[k] === undefined ? "-" : s[k]);
      });
    });
  }

  form.addEventListener("submit", function (event) { event.preventDefault(); load(); });
  document.getElementById("clear").addEventListener("click", function () { form.reset(); load(); });

  document.getElementById("export").addEventListener("click", function () {
    var button = this;
    button.disabled = true;
    GOF.call(GOF.PATHS.adminExport, { raw: true }).then(function (response) {
      button.disabled = false;
      if (!response.ok) { showAlert("Could not export the CSV.", "error"); return; }
      return response.blob().then(function (blob) {
        var url = URL.createObjectURL(blob);
        var a = el("a", { href: url, download: "gof_registrations.csv" });
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      });
    });
  });

  loadStats();
  load();
})();
