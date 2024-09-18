from django.urls import resolve, reverse

from apps.sharings.api.v1.views import CollaboratorViewSet


def test_sharing_list_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("collaborator-list"))
    assert resolver_match.func.cls == CollaboratorViewSet
    assert resolver_match.view_name == "collaborator-list"


def test_sharing_detail_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("collaborator-detail", args=[1]))
    assert resolver_match.func.cls == CollaboratorViewSet
    assert resolver_match.view_name == "collaborator-detail"
