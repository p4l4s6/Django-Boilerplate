from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        if status_code == 204:
            status_code = 200
        response = {
            "status": "success",
            "code": status_code,
            "data": data,
            "message": None
        }
        if data is not None and "detail" in data:
            response["message"] = data["detail"]
            del data['detail']
        if not str(status_code).startswith('2'):
            response["status"] = "error"
            response["data"] = None
            try:
                response["message"] = data["detail"]
            except KeyError:
                response["errors"] = data
        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)
