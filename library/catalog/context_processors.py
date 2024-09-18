NAV_MENU_COOKIE_NAME = "nav_menu_state"
NAV_MENU_COOKIE_OPEN = "open"
NAV_MENU_COOKIE_CLOSED = "closed"


def nav_menu_state(request):
    return {
        "nav_menu_open": request.COOKIES.get(NAV_MENU_COOKIE_NAME)
        == NAV_MENU_COOKIE_OPEN
    }
