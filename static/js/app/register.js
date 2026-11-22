(function () {
  "use strict";
  var form = document.getElementById("register-form");
  var subjectSelect = form.elements.olympiad_id;

  // Fill the subject list from the API; preselect from ?subject=<slug>.
  GOF.call(GOF.PATHS.olympiads, { auth: false }).then(function (res) {
    if (!res.ok) return;
    var wanted = new URLSearchParams(window.location.search).get("subject");
    var list = Array.isArray(res.data) ? res.data : (res.data.results || []); // plain or paginated
    list.forEach(function (o) {
      var option = GOF.el("option", { value: String(o.id), text: o.subject + " (Classes " + o.class_min + " to " + o.class_max + ")" });
      option.dataset.min = o.class_min;
      option.dataset.max = o.class_max;
      if (o.slug === wanted) option.selected = true;
      subjectSelect.appendChild(option);
    });
  });

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    GOF.clearErrors(form);

    var f = form.elements;
    var body = {
      student_name: f.student_name.value.trim().replace(/\s+/g, " "),
      student_class: f.student_class.value ? Number(f.student_class.value) : "",
      school: f.school.value.trim(),
      city: f.city.value.trim(),
      parent_name: f.parent_name.value.trim(),
      parent_mobile: f.parent_mobile.value.trim(),
      email: f.email.value.trim().toLowerCase(),
      olympiad_id: f.olympiad_id.value ? Number(f.olympiad_id.value) : "",
      password: f.password.value,
      consent_given: f.consent_given.checked
    };

    // Quick checks for instant feedback; the server repeats every rule.
    var problems = {};
    ["student_name", "student_class", "school", "city", "parent_name", "parent_mobile", "email", "olympiad_id", "password"]
      .forEach(function (k) { if (body[k] === "") problems[k] = "This field is required."; });
    if (body.password && body.password.length < 8) problems.password = "Use at least 8 characters.";
    if (body.password && body.password !== f.password_confirm.value) problems.password_confirm = "The two passwords do not match.";
    if (body.parent_mobile && !/^[6-9]\d{9}$/.test(body.parent_mobile)) problems.parent_mobile = "Enter a 10-digit mobile number starting with 6, 7, 8 or 9.";
    var chosen = f.olympiad_id.selectedOptions[0];
    if (body.student_class && chosen && chosen.dataset.min && (body.student_class < Number(chosen.dataset.min) || body.student_class > Number(chosen.dataset.max))) {
      problems.student_class = "This Olympiad is open to classes " + chosen.dataset.min + " to " + chosen.dataset.max + ".";
    }
    if (!body.consent_given) problems.consent_given = "Parent or guardian consent is required to register.";
    if (Object.keys(problems).length) { GOF.showErrors(form, { fields: problems, general: "Please fix the highlighted fields." }); return; }

    var unlock = GOF.lockButton(form.querySelector("button[type=submit]"), "Registering...");

    GOF.call(GOF.PATHS.register, { method: "POST", auth: false, body: body }).then(function (res) {
      if (!res.ok) {
        unlock();
        var errors = GOF.readErrors(res.data, res.status);
        if (Object.keys(errors.fields).length && !errors.general) errors.general = "Please fix the highlighted fields.";
        GOF.showErrors(form, errors);
        return;
      }
      var reg = res.data.registration || {};
      GOF.set("gof_flash", "Registration complete. Your registration number is " + (reg.reg_number || "shown below") + ". Keep it for your records.");
      // Sign the new student in so they land on their dashboard.
      return GOF.call(GOF.PATHS.studentLogin, { method: "POST", auth: false, body: { email: body.email, password: body.password } })
        .then(function (login) {
          if (login.ok) GOF.saveSession(login.data);
          window.location.href = login.ok ? GOF.PAGES.student : GOF.PAGES.studentLogin;
        });
    }).catch(function () {
      unlock();
      GOF.showErrors(form, { fields: {}, general: "Could not reach the server. Check your connection and try again." });
    });
  });
})();
