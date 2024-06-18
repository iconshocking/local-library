const toggler = document.body.querySelector("#navbar-toggler");
const expander = document.body.querySelector("#navbar-toggler-target");

toggler?.addEventListener("click", () => {
  sessionStorage.setItem(
    "navbarExpanded",
    // expanding if the height is 0
    // @ts-ignore
    expander?.offsetHeight === 0 ? "true" : "false"
  );
});

// default is collapsed, so we need to set some bootstrap classes if it was expanded last
if (sessionStorage.getItem("navbarExpanded") === "true") {
  expander?.classList.add("show");

  toggler?.classList.remove("collapsed");
  toggler?.setAttribute("aria-expanded", "true");
}
