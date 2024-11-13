import uuid

from django.urls import resolve, reverse

from apps.diagrams.api.v1.views import DiagramViewSet, SharedWithMeDiagramViewSet


def test_diagram_list_resolve() -> None:
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


def test_diagram_detail_resolve() -> None:
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


def test_diagram_copy_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    uuid_pk = uuid.uuid4()
    resolver_match = resolve(reverse("diagram-copy-diagram", args=[uuid_pk]))
    assert resolver_match.func.cls == DiagramViewSet
    assert resolver_match.view_name == "diagram-copy-diagram"


def test_diagram_invite_collaborator_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    uuid_pk = uuid.uuid4()
    resolver_match = resolve(reverse("diagram-invite-collaborator", args=[uuid_pk]))
    assert resolver_match.func.cls == DiagramViewSet
    assert resolver_match.view_name == "diagram-invite-collaborator"


def test_diagram_remove_all_collaborators_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    uuid_pk = uuid.uuid4()
    resolver_match = resolve(
        reverse("diagram-remove-all-collaborators", args=[uuid_pk])
    )
    assert resolver_match.func.cls == DiagramViewSet
    assert resolver_match.view_name == "diagram-remove-all-collaborators"


def test_shared_diagram_list_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    resolver_match = resolve(reverse("shared-diagram-list"))
    assert resolver_match.func.cls == SharedWithMeDiagramViewSet
    assert resolver_match.view_name == "shared-diagram-list"


def test_shared_diagram_copy_shared_diagram_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    uuid_pk = uuid.uuid4()
    resolver_match = resolve(
        reverse("shared-diagram-copy-shared-diagram", args=[uuid_pk])
    )
    assert resolver_match.func.cls == SharedWithMeDiagramViewSet
    assert resolver_match.view_name == "shared-diagram-copy-shared-diagram"


def test_shared_diagram_save_shared_diagram_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    uuid_pk = uuid.uuid4()
    resolver_match = resolve(
        reverse("shared-diagram-save-shared-diagram", args=[uuid_pk])
    )
    assert resolver_match.func.cls == SharedWithMeDiagramViewSet
    assert resolver_match.view_name == "shared-diagram-save-shared-diagram"


def test_shared_diagram_unshare_me_from_diagram_resolve() -> None:
    """
    GIVEN a URL pattern name
    WHEN the `resolve()` function is called with the URL associated with the pattern
    THEN:
        - the appropriate view is returned;
        - resolver points to the view with the correct URL pattern name.
    """
    uuid_pk = uuid.uuid4()
    resolver_match = resolve(
        reverse("shared-diagram-unshare-me-from-diagram", args=[uuid_pk])
    )
    assert resolver_match.func.cls == SharedWithMeDiagramViewSet
    assert resolver_match.view_name == "shared-diagram-unshare-me-from-diagram"
