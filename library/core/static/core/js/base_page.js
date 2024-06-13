const toggler = document.body.querySelector("#navbar-toggler");
let simulatedClick = false;
toggler?.addEventListener("click", () => {
  if (!simulatedClick) {
      localStorage.setItem(
        "navbarExpanded",
        localStorage.getItem("navbarExpanded") === "true" ? "false" : "true"
      );
  }
  simulatedClick = false;
});

// default is collapsed, so if it was expanded, we need to simulate a click
if (localStorage.getItem("navbarExpanded") === "true") {
  const expander = document.body.querySelector("#navbar-toggler-target");
  expander?.classList.add("transition-negator");
  expander?.addEventListener(
    "transitionend",
    () => {
      expander?.classList.remove("transition-negator");
    },
    { once: true }
  );
  simulatedClick = true;
  // @ts-ignore
  document.body.querySelector("#navbar-toggler")?.click();
}
