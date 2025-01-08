import tempfile
import cv2
import re
from django.core.exceptions import ValidationError

def validate_video_duration(media_file):
    """Video süresini kontrol eden validator"""
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(media_file.read())
        temp_file.flush()
        file_path = temp_file.name

    video = cv2.VideoCapture(file_path)
    if not video.isOpened():
        raise ValidationError("Video file could not be opened.")
    
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps if fps > 0 else 0
    
    video.release()
    temp_file.close()

    if duration > 15:
        raise ValidationError("Video duration exceeds the limit of 15 seconds.")

def validate_password_strength(password):
    """Şifre karmaşıklığını kontrol eden validator"""
    
    validations = [
        (len(password) >= 8, "Şifre en az 8 karakter olmalıdır."),
        (re.search(r'[A-Z]', password), "Şifre en az bir büyük harf içermelidir."),
        (re.search(r'[a-z]', password), "Şifre en az bir küçük harf içermelidir."),
        (re.search(r'\d', password), "Şifre en az bir rakam içermelidir."),
        (re.search(r'[!@#$%^&*(),.?":{}|<>]', password), "Şifre en az bir özel karakter içermelidir.")
    ]

    for condition, message in validations:
        if not condition:
            raise ValidationError(message)