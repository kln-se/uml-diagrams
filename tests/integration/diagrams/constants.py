from django.urls import reverse

DIAGRAMS_URL = reverse("diagram-list")
DIAGRAM_COPY_URL_NAME = "diagram-copy-diagram"
SHARED_DIAGRAMS_URL = reverse("shared-diagram-list")
SHARED_DIAGRAM_COPY_URL_NAME = "shared-diagram-copy-shared-diagram"
SHARED_DIAGRAM_SAVE_URL_NAME = "shared-diagram-save-shared-diagram"
SHARED_DIAGRAM_UNSHARE_ME_URL_NAME = "shared-diagram-unshare-me-from-diagram"
PUBLIC_DIAGRAMS_URL_NAME = "public-diagram-detail"
DIAGRAM_SET_DIAGRAM_PUBLIC_URL_NAME = "diagram-set-diagram-public"
DIAGRAM_SET_DIAGRAM_PRIVATE_URL_NAME = "diagram-set-diagram-private"
