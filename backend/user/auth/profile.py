from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
import json

@csrf_exempt
def get_profile(request):
    if request.method == "GET":
        user = request.user
        if user.is_authenticated:
            profile = user.profile
            return JsonResponse({
                "username": user.username,
                "email": user.email,
                "bio": profile.bio,
                "location": profile.location,
                "birth_date": profile.birth_date,
            }, status=200)
        return JsonResponse({"error": "Not authenticated"}, status=403)

@csrf_exempt
def update_profile(request):
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            data = json.loads(request.body)
            profile = user.profile

            profile.bio = data.get("bio", profile.bio)
            profile.location = data.get("location", profile.location)
            profile.birth_date = data.get("birth_date", profile.birth_date)
            profile.save()

            return JsonResponse({"message": "Profile updated successfully"}, status=200)
        return JsonResponse({"error": "Not authenticated"}, status=403)
