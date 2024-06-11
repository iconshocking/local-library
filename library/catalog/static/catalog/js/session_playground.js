// strip query params from URL
window.history.replaceState(null, "", "//" + window.location.host + window.location.pathname);

// reset button reloads page with reset query param
document.querySelector(".reset-session")?.addEventListener("click", (e) => {
  window.location.href = "//" + window.location.host + window.location.pathname + "?reset=1";
});
