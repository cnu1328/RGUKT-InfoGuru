from django.urls import path

from .views.jwt_authentication_view import UserViewSet
from .views.user_auth_view import AuthenticationView
from .views.chat_view import ChatViewSet


urlpatterns = [
    # path('test', TestView.as_view(), name='test'),
    path('auth/signup', AuthenticationView.as_view({'post': 'signup'}), name="signup"),
    path('auth/login', AuthenticationView.as_view({'post': 'login'}), name="login"),
    path('auth/check-login', AuthenticationView.as_view({'post': 'verify_token'}), name="verify_token"),
    path('auth/logout', AuthenticationView.as_view({'post': 'logout'}), name="logout"),
    path('list', UserViewSet.as_view({'get': 'list'}), name="list"),
    path('ask', ChatViewSet.as_view({'post': 'chat'}), name="ask"),
    path('messages/<uuid:user_id>/<uuid:chat_id>', ChatViewSet.as_view({'get': 'get_messages_by_chat_id'}), name="messages"),
    path('chats/chat/<uuid:user_id>', ChatViewSet.as_view({'get': 'get_chats_by_user_id'}), name="chats"),
    path('chat/rename/<uuid:chat_id>', ChatViewSet.as_view({'put': 'rename_chat'}), name="rename_chat"),
    path('chat/delete/<uuid:chat_id>', ChatViewSet.as_view({'delete': 'delete_chat'}), name="delete_chat")
]