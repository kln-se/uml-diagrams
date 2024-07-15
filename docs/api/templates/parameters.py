from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

required_header_auth_parameter = OpenApiParameter(
    name="Authorization",
    required=True,
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    description="Authentication token in the following format: "
    "**Token <token-value>**",
    default="Token <token-value>",
)
