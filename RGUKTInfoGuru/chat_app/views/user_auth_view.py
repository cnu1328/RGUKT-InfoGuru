from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from ..serializers.user_authentication_serializer import SignupSerializer, UserDataSerializer, LoginSerializer
from ..services.impl.user_auth_service_impl import UserAuthServiceImpl
from ..utils.response import CustomResponse
from rest_framework.decorators import action
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

import logging

logger = logging.getLogger(__name__)

class AuthenticationView(ViewSet):
    """
    This view take care of Authentication process.
    """
    permission_classes = [AllowAny]
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AuthenticationView, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True
            self.Response = CustomResponse()
            self.auth_service = UserAuthServiceImpl()

            logger.info("AuthenticationView is initialized successfully")

    @action(methods=['post'], detail=False)
    def signup(self, request):
        """
        Handles User's signup
        """

        logger.info("Signup method is called and validating the request data")
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():

            logger.info("Request data is validated")


            try:

                logger.info("Signup serializer is valid")
                data = serializer.validated_data

                user = self.auth_service.signup(data["email"], data["password"])

                result = UserDataSerializer(instance=user)

                logger.info("User is created successfully")

                return self.Response(data=result.data,message="User is successfully created", success=True, status_code=201)

            except Exception as e:
                return self.Response(message=str(e), success=False,status_code=404)

        return self.Response(data=serializer.errors,message="Error occured", status_code=404)

    @action(methods=['post'], detail=False)
    def login(self, request):
        """
        Handles user's Login
        """
        logger.info("Signin method is called and validating the request data")
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            try:

                logger.info("Login serializer is valided")
                data = serializer.validated_data
                user_data = self.auth_service.login(data["email"], data["password"])

                result = UserDataSerializer(instance=user_data["user"]).data

                result["access_token"] = user_data["access_token"]
                result["refresh_token"] = user_data["refresh_token"]

                logger.info("User logged in successfully")


                return self.Response(result, message="Successfully Login", success=True, status_code=200)
            except Exception as e:
                print(f"The message is {str(e)}")
                return self.Response(message=str(e), success=False,status_code=404)

        return self.Response(data=serializer.errors,message="Error occured", status_code=404)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Handles User logout by blacklisting the refresh token
        """
        try:
            refresh_token = request.data.get("refresh_token")

            if not refresh_token:
                return self.Response(message="Refresh token is missing", status_code=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return self.Response(message="Logged out successfully", status_code=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            return self.Response(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def verify_token(self, request):
        """
        Verifies the token
        """

        token = request.data.get("token", None)
        if not token:
            return self.Response(message="Token is required", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            data = self.auth_service.verify_token(token)
            return self.Response(message="Token is valid", data=data, status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.info(f"Token is invalid {str(e)}")
            return self.Response(message=str(e), status_code=status.HTTP_401_UNAUTHORIZED)






