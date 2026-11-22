(function () {
  "use strict";
  if (!GOF.requireRole("student")) return;

  var root = document.getElementById("dashboard");
  var el = GOF.el;
  var LABEL = { pending: "Pending review", confirmed: "Confirmed", rejected: "Rejected" };
  var NOTE = {
    pending: "Your registration is waiting for review. Check back here for updates.",
    confirmed: "Your registration is confirmed. Keep your registration number for the exam.",
    rejected: "This registration could not be accepted. Please contact the organisers."
  };

  function row(label, value) {
    return el("div", {}, [el("dt", { text: label }), el("dd", { text: value || "-" })]);
  }

  function message(text, kind) {
    root.textContent = "";
    root.appendChild(el("p", { class: "notice notice-" + kind, role: kind === "error" ? "alert" : "status", text: text }));
  }

  function render(p, email) {
    var key = (p.status || "pending").toLowerCase();
    root.textContent = "";

    root.appendChild(el("div", { class: "card" }, [
      el("p", { class: "meta", text: "Registration number" }),
      el("p", { class: "regnum", text: p.reg_number }),
      el("p", {}, el("span", { class: "badge badge-" + key, text: LABEL[key] || key })),
      el("p", { text: NOTE[key] || "" })
    ]));

    root.appendChild(el("h2", { text: "Selected Olympiad" }));
    root.appendChild(el("p", { text: p.olympiad_subject || "-" }));

    root.appendChild(el("h2", { text: "Student profile" }));
    root.appendChild(el("dl", { class: "facts" }, [
      row("Name", p.student_name),
      row("Class", String(p.student_class)),
      row("School", p.school),
      row("City", p.city),
      row("Email", p.email || email),
      row("Parent or guardian", p.parent_name),
      row("Parent mobile", p.parent_mobile),
      row("Registered on", p.created_at ? new Date(p.created_at).toLocaleString("en-IN") : "-")
    ]));
  }

  var flash = GOF.get("gof_flash");
  if (flash) {
    GOF.del("gof_flash");
    var box = document.getElementById("flash");
    box.textContent = flash;
    box.classList.remove("hidden");
  }

  GOF.call(GOF.PATHS.studentDashboard).then(function (res) {
    if (res.status === 401 || res.status === 403) { GOF.clearSession(); GOF.requireRole("student"); return; }
    if (res.status === 404) { message("No registration is linked to this account yet.", "error"); return; }
    if (!res.ok) { message(GOF.readErrors(res.data, res.status).general, "error"); return; }
    var student = res.data.student || {};
    render(student.profile || {}, student.email);
  }).catch(function () { message("Could not load your registration. Please refresh the page.", "error"); });
})();
