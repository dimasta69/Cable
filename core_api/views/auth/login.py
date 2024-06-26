from djoser.views import TokenCreateView
from drf_yasg.utils import swagger_auto_schema


class TokenCreateView(TokenCreateView):
    @swagger_auto_schema(tags=['core-api/auth'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
