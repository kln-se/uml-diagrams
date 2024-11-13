import pytest
from django.http import Http404
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.diagrams.api.v1.views import DiagramViewSet, SharedWithMeDiagramViewSet
from apps.diagrams.models import Diagram
from apps.sharings.constants import PermissionLevels
from apps.sharings.models import Collaborator
from apps.users.constants import UserRoles
from tests.factories import CollaboratorFactory, DiagramFactory, UserFactory


class TestActionCopyDiagram:
    """Test @action copy_diagram() inside DiagramViewSet."""

    def test_copy_existing_diagram(self) -> None:
        """
        GIVEN a diagram
        WHEN action copy_diagram() inside DiagramViewSet is called
        THEN check that the copy of the diagram is created.
        """
        original_diagram = DiagramFactory()
        data_to_set = {
            "description": "Copied.",
        }
        request = APIRequestFactory()
        request.user = original_diagram.owner
        request.query_params = {}
        request.data = data_to_set
        viewset = DiagramViewSet(
            request=request,
            kwargs={"pk": original_diagram.id},
            format_kwarg=None,
            action="copy_diagram",
        )
        assert viewset.get_object() == original_diagram
        response = viewset.copy_diagram(request=request)
        assert response.status_code == status.HTTP_201_CREATED
        copied_diagram = Diagram.objects.get(id=response.data["diagram_id"])
        assert copied_diagram.description == data_to_set["description"]
        assert copied_diagram.owner == original_diagram.owner
        assert copied_diagram.title == f"Copy of {original_diagram.title}"

    def test_copy_non_existing_diagram(self) -> None:
        """
        GIVEN user who tries to copy a non-existing diagram (invalid diagram id)
        WHEN action copy_diagram() inside DiagramViewSet is called
        THEN check that the status code is 404 NOT FOUND is returned.
        """
        diagram_owned_by_some_user = DiagramFactory()
        user_without_diagrams = UserFactory(role=UserRoles.USER)
        data_to_set = {
            "description": "Copied.",
        }
        request = APIRequestFactory().post("/", data=data_to_set)
        viewset = DiagramViewSet.as_view(actions={"post": "copy_diagram"})
        force_authenticate(request, user=user_without_diagrams)
        response = viewset(request, pk=diagram_owned_by_some_user.id)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestActionCopySharedDiagram:
    """Test @action copy_shared_diagram() inside SharedWithMeDiagramViewSet."""

    def test_copy_shared_diagram_for_collaborator_with_valid_permission_granted(self):
        """
        GIVEN the diagram which is shared to user (i.e. collaborator)
        with appropriate "view-copy" permission
        WHEN action invite_collaborator() inside SharedWithMeDiagramViewSet is called
        THEN check that the copy of the diagram is created.
        """
        original_diagram = DiagramFactory()
        collaborator = CollaboratorFactory(
            diagram=original_diagram, permission_level=PermissionLevels.VIEWCOPY
        )
        data_to_set = {
            "description": "Copied.",
        }
        request = APIRequestFactory()
        request.user = collaborator.shared_to
        request.query_params = {}
        request.data = data_to_set
        viewset = SharedWithMeDiagramViewSet(
            request=request,
            kwargs={"pk": original_diagram.id},
            format_kwarg=None,
            action="copy_shared_diagram",
        )
        assert viewset.get_object() == original_diagram
        response = viewset.copy_shared_diagram(request=request)
        assert response.status_code == status.HTTP_201_CREATED
        copied_diagram = Diagram.objects.get(id=response.data["diagram_id"])
        assert copied_diagram.description == data_to_set["description"]
        assert copied_diagram.owner == collaborator.shared_to
        assert copied_diagram.title == f"Copy of {original_diagram.title}"

    def test_copy_shared_diagram_for_collaborator_with_invalid_permission_granted(self):
        """
        GIVEN the diagram which is shared to user (i.e. collaborator)
        with not appropriate ("view-only") permission
        WHEN action invite_collaborator() inside SharedWithMeDiagramViewSet is called
        THEN check that the copy of the diagram is not created.
        """
        original_diagram = DiagramFactory()
        collaborator = CollaboratorFactory(
            diagram=original_diagram, permission_level=PermissionLevels.VIEWONLY
        )
        data_to_set = {
            "description": "Copied.",
        }
        request = APIRequestFactory().post("/", data=data_to_set)
        viewset = SharedWithMeDiagramViewSet.as_view(
            actions={"post": "copy_shared_diagram"}
        )
        force_authenticate(request, user=collaborator.shared_to)
        response = viewset(request, pk=original_diagram.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Diagram.objects.count() == 1


class TestActionSaveSharedDiagram:
    """Test @action save_shared_diagram() inside SharedWithMeDiagramViewSet."""

    @pytest.mark.parametrize(
        ("field_to_patch", "was_modified"),
        [
            ("title", False),
            ("description", True),
            ("json", True),
            ("updated_at", False),
        ],
    )
    def test_save_shared_diagram_for_collaborator_with_valid_permission_granted(
        self, field_to_patch: str, was_modified: bool
    ):
        """
        GIVEN the diagram which is shared to user (i.e. collaborator)
        with appropriate "view-edit" permission
        WHEN action save_shared_diagram() inside SharedWithMeDiagramViewSet is called
        THEN check that certain diagram fields was modified.
        """
        original_diagram = DiagramFactory()
        collaborator = CollaboratorFactory(
            diagram=original_diagram, permission_level=PermissionLevels.VIEWEDIT
        )
        data_to_set = {field_to_patch: getattr(DiagramFactory.build(), field_to_patch)}
        request = APIRequestFactory()
        request.user = collaborator.shared_to
        request.query_params = {}
        request.data = data_to_set
        viewset = SharedWithMeDiagramViewSet(
            request=request,
            kwargs={"pk": original_diagram.id},
            format_kwarg=None,
            action="save_shared_diagram",
        )
        assert viewset.get_object() == original_diagram
        response = viewset.save_shared_diagram(request=request)
        assert response.status_code == status.HTTP_200_OK
        edited_diagram = Diagram.objects.get(id=response.data["diagram_id"])
        assert (
            getattr(edited_diagram, field_to_patch) == data_to_set[field_to_patch]
        ) == was_modified
        assert edited_diagram.owner == original_diagram.owner

    def test_save_shared_diagram_for_collaborator_with_invalid_permission_granted(self):
        """
        GIVEN the diagram which is shared to user (i.e. collaborator)
        with not appropriate ("view-only") permission
        WHEN action save_shared_diagram() inside SharedWithMeDiagramViewSet is called
        THEN check that the copy of the diagram is not created.
        """
        original_diagram = DiagramFactory()
        collaborator = CollaboratorFactory(
            diagram=original_diagram, permission_level=PermissionLevels.VIEWONLY
        )
        data_to_set = {
            "json": DiagramFactory.build().json,
        }
        request = APIRequestFactory().post("/", data=data_to_set)
        viewset = SharedWithMeDiagramViewSet.as_view(
            actions={"post": "save_shared_diagram"}
        )
        force_authenticate(request, user=collaborator.shared_to)
        response = viewset(request, pk=original_diagram.id)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Diagram.objects.get(id=original_diagram.id).json != data_to_set["json"]


class TestActionUnshareMeFromSharedDiagram:
    """Test @action unshare_me_from_diagram() inside SharedWithMeDiagramViewSet."""

    def test_unshare_me_from_diagram_by_collaborator(self):
        """
        GIVEN the diagram which is shared to user (i.e. collaborator).
        WHEN action unshare_me_from_diagram() inside SharedWithMeDiagramViewSet
        is called
        THEN check that the collaborator is deleted.
        """
        original_diagram = DiagramFactory()
        collaborator = CollaboratorFactory(diagram=original_diagram)
        request = APIRequestFactory()
        request.user = collaborator.shared_to
        request.query_params = {}
        viewset = SharedWithMeDiagramViewSet(
            request=request,
            kwargs={"pk": original_diagram.id},
            format_kwarg=None,
            action="unshare_me_from_diagram",
        )
        assert viewset.get_object() == original_diagram
        response = viewset.unshare_me_from_diagram(request=request)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Diagram.objects.filter(id=original_diagram.id).exists()
        assert not Collaborator.objects.filter(
            diagram=original_diagram, shared_to=collaborator.id
        ).exists()

    def test_unshare_me_from_diagram_by_not_collaborator(self):
        """
        GIVEN the diagram which was not shared to user.
        WHEN action unshare_me_from_diagram() inside SharedWithMeDiagramViewSet
        is called
        THEN check that diagram is not found (404).
        """
        original_diagram = DiagramFactory()
        some_collaborator = CollaboratorFactory(diagram=original_diagram)
        not_collaborator = UserFactory()
        request = APIRequestFactory()
        request.user = not_collaborator
        request.query_params = {}
        viewset = SharedWithMeDiagramViewSet(
            request=request,
            kwargs={"pk": original_diagram.id},
            format_kwarg=None,
            action="unshare_me_from_diagram",
        )
        with pytest.raises(Http404):
            _ = viewset.unshare_me_from_diagram(request=request)
        assert Diagram.objects.filter(id=original_diagram.id).exists()
        assert Collaborator.objects.filter(id=some_collaborator.id).exists()

    def test_unshare_me_from_diagram_for_invalid_diagram_id(self):
        """
        GIVEN the user who tries to unshare himself from
        not existent diagram (invalid id).
        WHEN action unshare_me_from_diagram() inside SharedWithMeDiagramViewSet
        is called
        THEN check that diagram is not found (404).
        """
        not_existent_diagram = DiagramFactory.build()
        request = APIRequestFactory()
        request.user = UserFactory()
        request.query_params = {}
        viewset = SharedWithMeDiagramViewSet(
            request=request,
            kwargs={"pk": not_existent_diagram.id},
            format_kwarg=None,
            action="unshare_me_from_diagram",
        )
        with pytest.raises(Http404):
            _ = viewset.unshare_me_from_diagram(request=request)
