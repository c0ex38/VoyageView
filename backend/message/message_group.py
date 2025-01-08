from rest_framework import serializers, generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from backend.models import GroupChat, User, GroupInvitation
from backend.serializers import GroupChatSerializer, GroupInvitationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class GroupChatCreateView(generics.CreateAPIView):
    """
    Grup oluşturma işlemi gerçekleştiren API.
    - Kullanıcı yalnızca giriş yaptıysa grup oluşturabilir.
    """
    serializer_class = GroupChatSerializer
    permission_classes = [permissions.IsAuthenticated]  # Yalnızca giriş yapmış kullanıcılar grup oluşturabilir

class GroupInviteView(generics.CreateAPIView):
    """
    Grup davetleri gönderen API.
    - Davet, sadece grup yöneticisi tarafından yapılabilir.
    """
    serializer_class = GroupInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]  # Yalnızca giriş yapmış kullanıcılar davet gönderebilir

    def post(self, request, *args, **kwargs):
        """
        Kullanıcıları gruba davet eder.
        - Davet edilen kullanıcı daha önce davet edilmemiş olmalı.
        - Yalnızca grup yöneticileri davet gönderebilir.
        """
        group = get_object_or_404(GroupChat, id=kwargs['group_id'])  # Grup ID'sine göre grup buluyoruz
        invited_user_id = request.data.get('invited_user_id')  # Davet edilen kullanıcının ID'si

        if not invited_user_id:
            return Response({"hata": "Davet edilen kullanıcı ID'si gereklidir."}, status=400)

        invited_user = get_object_or_404(User, id=invited_user_id)  # Kullanıcıyı ID ile buluyoruz

        # Yalnızca grup yöneticileri davet gönderebilir
        if request.user not in group.admins.all():
            return Response({"hata": "Yalnızca grup yöneticileri kullanıcı davet edebilir."}, status=403)

        # Kullanıcıya zaten davet gönderilip gönderilmediğini kontrol ediyoruz
        if GroupInvitation.objects.filter(group=group, invited_user=invited_user, is_accepted=False, is_rejected=False).exists():
            return Response({"hata": "Bu kullanıcı zaten davet edilmiş."}, status=400)

        # Davet oluşturuluyor
        GroupInvitation.objects.create(
            group=group,
            invited_user=invited_user,
            invited_by=request.user
        )

        return Response({"mesaj": "Davet başarıyla gönderildi."}, status=201)

class GroupInvitationResponseView(APIView):
    """
    Kullanıcıların grup davetlerine cevap vermesini sağlayan API.
    - Kullanıcı daveti kabul edebilir veya reddedebilir.
    """
    permission_classes = [IsAuthenticated]  # Sadece giriş yapmış kullanıcılar davet yanıtı verebilir

    def post(self, request, *args, **kwargs):
        """
        Davet yanıtı gönderir.
        - Kullanıcı daveti kabul edebilir veya reddedebilir.
        """
        invitation = get_object_or_404(GroupInvitation, id=kwargs['invitation_id'], invited_user=request.user)  # Daveti buluyoruz

        action = request.data.get('action')  # Kullanıcının eylemi (accept veya reject)
        if action == "accept":
            invitation.is_accepted = True  # Davet kabul edildi
            invitation.save()

            # Kullanıcıyı gruba ekle
            invitation.group.members.add(request.user)
            return Response({"mesaj": "Davet kabul edildi."}, status=200)
        elif action == "reject":
            invitation.is_rejected = True  # Davet reddedildi
            invitation.save()
            return Response({"mesaj": "Davet reddedildi."}, status=200)

        return Response({"hata": "Geçersiz işlem. Lütfen 'accept' veya 'reject' kullanın."}, status=400)
