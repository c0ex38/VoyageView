from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'full_name', 'date_of_birth', 'is_email_verified', 'is_staff', 'is_active')
    list_filter = ('is_email_verified', 'is_staff', 'is_active', 'date_of_birth')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'date_of_birth', 'profile_picture')}),
        ('Permissions', {'fields': ('is_email_verified', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'full_name', 'date_of_birth', 'profile_picture', 'is_email_verified'),
        }),
    )

    actions = ['import_users_from_csv']

    def import_users_from_csv(self, request, queryset):
        if 'csv_file' not in request.FILES:
            self.message_user(request, "Lütfen bir CSV dosyası yükleyin.", level=messages.ERROR)
            return

        csv_file = request.FILES['csv_file']
        try:
            csv_reader = csv.DictReader(TextIOWrapper(csv_file, encoding='utf-8'))
            success_count = 0
            error_count = 0

            for row in csv_reader:
                try:
                    # Zorunlu alanları kontrol et
                    username = row.get('username')
                    email = row.get('email')
                    password = row.get('password')

                    if not username or not email or not password:
                        raise ValueError("Kullanıcı adı, e-posta ve şifre zorunludur.")

                    # Opsiyonel alanları al
                    full_name = row.get('full_name', '')
                    date_of_birth = row.get('date_of_birth', None)
                    profile_picture = row.get('profile_picture', None)
                    is_staff = row.get('is_staff', 'False').lower() == 'true'
                    is_superuser = row.get('is_superuser', 'False').lower() == 'true'
                    is_active = row.get('is_active', 'True').lower() == 'true'
                    is_email_verified = row.get('is_email_verified', 'False').lower() == 'true'

                    # Kullanıcı oluştur
                    user = CustomUser.objects.create_user(
                        username=username,
                        email=email,
                        full_name=full_name,
                        date_of_birth=date_of_birth,
                        password=password,
                        profile_picture=profile_picture,
                        is_staff=is_staff,
                        is_superuser=is_superuser,
                        is_active=is_active
                    )
                    user.is_email_verified = is_email_verified
                    user.save()

                    # Grupları ekle
                    groups = row.get('groups', '').split(',')
                    for group_name in groups:
                        if group_name.strip():
                            group, created = Group.objects.get_or_create(name=group_name.strip())
                            user.groups.add(group)

                    # İzinleri ekle
                    permissions = row.get('user_permissions', '').split(',')
                    for perm_codename in permissions:
                        if perm_codename.strip():
                            try:
                                perm = Permission.objects.get(codename=perm_codename.strip())
                                user.user_permissions.add(perm)
                            except Permission.DoesNotExist:
                                raise ValueError(f"İzin bulunamadı: {perm_codename.strip()}")

                    success_count += 1
                except Exception as e:
                    error_count += 1
                    self.message_user(request, f"Hata: {row.get('username', 'Bilinmiyor')} kullanıcı eklenemedi. {str(e)}", level=messages.ERROR)

            self.message_user(request, f"{success_count} kullanıcı başarıyla eklendi. {error_count} hata oluştu.", level=messages.SUCCESS)

        except Exception as e:
            self.message_user(request, f"CSV işlenirken bir hata oluştu: {str(e)}", level=messages.ERROR)

    import_users_from_csv.short_description = _("CSV'den kullanıcı ekle")
