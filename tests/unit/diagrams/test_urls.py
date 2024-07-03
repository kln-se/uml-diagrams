from django.urls import resolve, reverse

from apps.diagrams.api.v1.views import DiagramCopyAPIView, DiagramViewSet


def test_diagram_list_resolve():
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("diagram-list"))
    assert resolver_match.func.cls == DiagramViewSet
    assert resolver_match.view_name == "diagram-list"


def test_diagram_detail_resolve():
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("diagram-detail", args=[1]))
    assert resolver_match.func.cls == DiagramViewSet
    assert resolver_match.view_name == "diagram-detail"


def test_diagram_copy_resolve():
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("diagram-copy", args=[1]))
    assert resolver_match.func.cls == DiagramCopyAPIView
    assert resolver_match.view_name == "diagram-copy"
