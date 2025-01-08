from django.urls import path
from backend.message.message import MessageListCreateView, MessageMarkAsReadView
from backend.message.message_group import GroupChatCreateView, GroupInviteView, GroupInvitationResponseView
from backend.message.share_post import SharePostView

urlpatterns = [
    path('', MessageListCreateView.as_view(), name='message-list-create'),
    path('<int:pk>/mark-read/', MessageMarkAsReadView.as_view(), name='message-mark-as-read'),
    path('group-chats/', GroupChatCreateView.as_view(), name='group-create'),
    path('group-chats/<int:group_id>/invite/', GroupInviteView.as_view(), name='group-invite'),
    path('group-invitations/<int:invitation_id>/respond/', GroupInvitationResponseView.as_view(), name='group-invitation-respond'),
    path('share-post/', SharePostView.as_view(), name='share-post'),
]
