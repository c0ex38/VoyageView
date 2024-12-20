from rest_framework import generics, permissions
from backend.models import GroupChat, GroupInvitation
from backend.serializers import GroupInvitationSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class GroupInviteView(generics.CreateAPIView):
    serializer_class = GroupInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        group = get_object_or_404(GroupChat, id=kwargs['group_id'])
        invited_user_id = request.data.get('invited_user_id')

        if not invited_user_id:
            return Response({"error": "Invited user ID is required."}, status=400)

        invited_user = get_object_or_404(User, id=invited_user_id)

        # Yalnızca grup yöneticileri davet gönderebilir
        if request.user not in group.admins.all():
            return Response({"error": "Only group admins can invite users."}, status=403)

        # Zaten davet edilmişse kontrol et
        if GroupInvitation.objects.filter(group=group, invited_user=invited_user, is_accepted=False, is_rejected=False).exists():
            return Response({"error": "This user has already been invited."}, status=400)

        # Davet oluştur
        GroupInvitation.objects.create(
            group=group,
            invited_user=invited_user,
            invited_by=request.user
        )

        return Response({"message": "Invitation sent successfully."}, status=201)

class GroupInvitationResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(GroupInvitation, id=kwargs['invitation_id'], invited_user=request.user)

        action = request.data.get('action')
        if action == "accept":
            invitation.is_accepted = True
            invitation.save()

            # Kullanıcıyı gruba ekle
            invitation.group.members.add(request.user)
            return Response({"message": "Invitation accepted."}, status=200)
        elif action == "reject":
            invitation.is_rejected = True
            invitation.save()
            return Response({"message": "Invitation rejected."}, status=200)

        return Response({"error": "Invalid action. Use 'accept' or 'reject'."}, status=400)
