const NAV_MENU_COOKIE_NAME = "nav_menu_state";
const NAV_MENU_COOKIE_OPEN = "open";
const NAV_MENU_COOKIE_CLOSED = "closed";

const toggler = document.body.querySelector("#navbar-toggler");
const expander = document.body.querySelector("#navbar-toggler-target");

toggler?.addEventListener("click", () => {
  // expanding if the height is 0
  // @ts-ignore
  const open = expander?.offsetHeight === 0;
  sessionStorage.setItem("navbarExpanded", open.toString());

  const cookie = `${NAV_MENU_COOKIE_NAME}=${
    open ? NAV_MENU_COOKIE_OPEN : NAV_MENU_COOKIE_CLOSED
  }; path=/`;
  document.cookie = cookie;
});
