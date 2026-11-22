// Prevent accidental double submits: lock the form after the first submit.
document.querySelectorAll("form[data-once]").forEach(function (form) {
  form.addEventListener("submit", function (event) {
    if (form.dataset.submitted) {
      event.preventDefault();
      return;
    }
    form.dataset.submitted = "1";
    var button = form.querySelector("button[type=submit]");
    if (button) {
      button.disabled = true;
      if (button.dataset.busyLabel) button.textContent = button.dataset.busyLabel;
    }
  });
});
// Re-enable when the page is restored from the back/forward cache.
window.addEventListener("pageshow", function (e) {
  if (!e.persisted) return;
  document.querySelectorAll("form[data-once]").forEach(function (form) {
    delete form.dataset.submitted;
    var b = form.querySelector("button[type=submit]");
    if (b) b.disabled = false;
  });
});
