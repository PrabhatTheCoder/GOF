(function () {
  "use strict";
  var form = document.getElementById("login-form");
  var role = form.dataset.role; // "student" or "admin"
  var path = role === "admin" ? GOF.PATHS.staffLogin : GOF.PATHS.studentLogin;
  var home = role === "admin" ? GOF.PAGES.staff : GOF.PAGES.student;

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    GOF.clearErrors(form);
    var unlock = GOF.lockButton(form.querySelector("button[type=submit]"), "Logging in...");

    GOF.call(path, {
      method: "POST",
      auth: false,
      body: { email: form.elements.email.value.trim(), password: form.elements.password.value }
    }).then(function (res) {
      if (res.ok) {
        GOF.saveSession(res.data);
        window.location.href = GOF.safeNext(home);
        return;
      }
      unlock();
      GOF.showErrors(form, GOF.readErrors(res.data, res.status));
    }).catch(function () {
      unlock();
      GOF.showErrors(form, { fields: {}, general: "Could not reach the server. Check your connection and try again." });
    });
  });
})();
