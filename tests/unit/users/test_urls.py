from django.urls import resolve, reverse

from apps.users.api.v1.views import SignupUserAPIView, UserViewSet


def test_signup_user_resolve():
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("signup"))
    assert resolver_match.func.cls == SignupUserAPIView
    assert resolver_match.view_name == "signup"


def test_user_detail_resolve():
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("user-detail"))
    assert resolver_match.func.cls == UserViewSet
    assert resolver_match.view_name == "user-detail"
