from ..interface.user_auth_service_interface import UserAuthServiceInterface
from ...dao.impl.user_auth_dao_impl import UserAuthDaoImpl
from ...exceptions import CustomException
import logging
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

class UserAuthServiceImpl(UserAuthServiceInterface):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserAuthServiceImpl, cls).__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, "initialized"):
            super().__init__(**kwargs)
            self.initialized = True
            self.user_auth_dao =UserAuthDaoImpl()

    def signup(self, email:str, password: str):
        """
        Handles User Signup process.
        """
        try:
            existing_user = self.user_auth_dao.get_user_by_email(email)

            if existing_user:
                raise CustomException(detail="User already exists", status_code=404)

            user = self.user_auth_dao.create_user(email, password)
            return user
        except Exception as e:
            logger.info(f"Exception occured while creating a new author : ", e)
            raise CustomException(detail=str(e))

    def login(self, email: str, password:str):
        try:
            user = self.user_auth_dao.validate_user(email, password)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return {
                "user": user,
                "access_token": access_token,
                "refresh_token": str(refresh),
            }
        except Exception as e:
            logger.info(f"Exception occured while Logging in : {str(e)}")
            raise CustomException(detail=str(e))
