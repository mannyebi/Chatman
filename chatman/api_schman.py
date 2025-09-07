from rest_framework import status
from rest_framework.response import Response


def api_response(Status, success=True, data=None, message="", error=""):
    """a unified JSON schema
    """
    return Response({
        "success": success,
        "data": data,
        "message": message,
        "error": error,
    }, status=Status)