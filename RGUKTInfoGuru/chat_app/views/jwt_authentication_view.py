from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import User
from ..serializers.user_authentication_serializer import UserDataSerializer
from ..utils.response import CustomResponse
from rest_framework import status

class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users
    authentication_classes = [JWTAuthentication]

    def list(self, request):
        """
        Fetch all user details (Only for authenticated users)
        """

        users = User.objects.all()
        serializer = UserDataSerializer(users, many=True)
        return CustomResponse()(serializer.data, status_code=status.HTTP_200_OK)