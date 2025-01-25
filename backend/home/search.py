from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.db.models import Q
import json

class SearchUserAPI(View):
    def post(self, request):
        try:
            # Body'den gelen veriyi al
            body = json.loads(request.body)
            username_query = body.get('username', '')

            if not username_query:
                return JsonResponse({"error": "'username' alanı gereklidir."}, status=400)

            # Kullanıcıyı ve benzerlerini ara
            users = User.objects.filter(Q(username__icontains=username_query))

            # Kullanıcı bilgilerini JSON formatında döndür
            results = [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
                for user in users
            ]

            return JsonResponse({"results": results}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Geçersiz JSON formatı."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)