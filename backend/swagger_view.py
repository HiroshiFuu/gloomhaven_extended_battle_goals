from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger import renderers
from rest_framework.schemas import SchemaGenerator

from urllib.parse import urljoin
import yaml
import coreapi


class SwaggerSchemaView(APIView):
    schema = None
    permission_classes = [AllowAny]
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer
    ]

    def get(self, request, version=None):
        generator = SchemaGenerator()
        schema = generator.get_schema(request=request)
        return Response(schema)
