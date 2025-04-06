from ..interface.user_auth_dao_interface import UserAuthDaoInterface
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from django.contrib.auth import authenticate
from ...exceptions import CustomException
from ...models import User

class UserAuthDaoImpl(UserAuthDaoInterface):
    """
    Implementation of UserAuthDAOInterface.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Implements the Singleton pattern to ensure only one instance is created.
        """
        if cls._instance is None:
            cls._instance = super(UserAuthDaoImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        """
        Initializes the AuthenticationView instance if it hasn't been initialized yet.
        Ensures that initialization only happens once.
        """
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True

    def create_user(self, email: str, password: str, user_name:str = "", avatar:str = ""):
        """
        creates new user

        Args:
            email (str): The email of the user.
            password (str): The password of the user.
            user_name (str): The username of the user.
            avatar (str, optional): The avatar URL or path. Defaults to an empty string.

        Returns:
            User: The newly created user object.
        """
        try:
            hashed_password = make_password(password)

            user = User.objects.create(
                email=email,
                password=hashed_password,
                username=user_name,
                avatar=avatar
            )

            return user
        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)


    def get_user_by_email(self, email: str):
        """
        Retrieves user by email
        """

        return User.objects.filter(email__iexact=email).first()

    def validate_user(self, email: str, password: str):
        """
        Handles user login process
        """

        try:
            user = authenticate(email=email.strip(), password=password)

            if not user:
                raise CustomException(detail="Invalid email or password", status_code=status.HTTP_401_UNAUTHORIZED)

            return user

        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)
        
    def get_user_by_id(self, user_id):
        """
        Retrieves user by id
        """
        try:
            user = User.objects.get(id=user_id)
            return user
        
        except Exception as e:
            raise CustomException(detail=str(e), status_code=status.HTTP_404_NOT_FOUND)


