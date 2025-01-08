from django.db.models import F
from django.db.models.functions import ACos, Cos, Sin, Radians
from math import radians

def filter_by_distance(queryset, lat, lng, radius_km):
    """
    PostgreSQL'in earthdistance modülünü kullanarak mesafe bazlı filtreleme yapar
    """
    # Derece cinsinden koordinatları radyana çevir
    lat_rad = radians(lat)
    lng_rad = radians(lng)
    
    # Mesafe hesaplama formülü
    queryset = queryset.annotate(
        distance=ACos(
            Cos(lat_rad) * Cos(F('latitude')) * 
            Cos(F('longitude') - lng_rad) +
            Sin(lat_rad) * Sin(F('latitude'))
        ) * 6371  # Dünya'nın yarıçapı (km)
    ).filter(
        distance__lte=radius_km
    ).order_by('distance')
    
    return queryset 