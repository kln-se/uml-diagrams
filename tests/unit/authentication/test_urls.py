from django.urls import resolve, reverse

from apps.authentication.api.v1.views import CustomObtainAuthToken, LogoutAPIView


def test_login_user_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("login"))
    assert resolver_match.func.cls == CustomObtainAuthToken
    assert resolver_match.view_name == "login"


def test_logout_user_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("logout"))
    assert resolver_match.func.cls == LogoutAPIView
    assert resolver_match.view_name == "logout"
