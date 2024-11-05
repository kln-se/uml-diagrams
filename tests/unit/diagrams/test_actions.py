from rest_framework import status
from rest_framework.test import APIRequestFactory

from apps.diagrams.api.v1.views import SharedWithMeDiagramViewSet
from apps.diagrams.models import Diagram
from apps.sharings.constants import PermissionLevels
from tests.factories import CollaboratorFactory, DiagramFactory


class TestActionCopyDiagram:
    """Test @action copy_diagram() inside DiagramViewSet."""

    pass


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
        with not appropriate "view-only" permission
        WHEN action invite_collaborator() inside SharedWithMeDiagramViewSet is called
        THEN check that the copy of the diagram is not created.
        """
        pass
