from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter

required_header_auth_parameter = OpenApiParameter(
    name="Authorization",
    required=True,
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    description="Authentication token in the following format: "
    "**Token <token-value>**",
    examples=[
        OpenApiExample(
            name="Token example", value="Token 528335a282e5af0da453ff583b1a7c5e292a30a3"
        ),
    ],
)
