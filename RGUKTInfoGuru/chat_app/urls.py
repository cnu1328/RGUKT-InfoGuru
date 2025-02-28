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
    path('ask', ChatViewSet.as_view({'post': 'chat'}), name="ask"),
    path('chats/<uuid:user_id>', ChatViewSet.as_view({'get': 'get_chats_by_user_id'}), name="chats"),
    path('chats/<uuid:user_id>/<uuid:chat_id>/messages', ChatViewSet.as_view({'get': 'get_messages_by_chat_id'}), name="messages"),
]