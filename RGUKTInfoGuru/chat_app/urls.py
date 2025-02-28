from django.urls import path

from .views.jwt_authentication_view import UserViewSet
from .views.user_auth_view import AuthenticationView
from .views.chat_view import ChatViewSet


urlpatterns = [
    # path('test', TestView.as_view(), name='test'),
    path('signup', AuthenticationView.as_view({'post': 'signup'}), name="signup"),
    path('login', AuthenticationView.as_view({'post': 'login'}), name="login"),
    path('logout', AuthenticationView.as_view({'post': 'logout'}), name="logout"),
    path('list', UserViewSet.as_view({'get': 'list'}), name="list"),
    path('chat', ChatViewSet.as_view({'post': 'chat'}), name="chat"),
]