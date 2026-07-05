from django.http import JsonResponse

from .models import ProjectPage


def projects_geojson(request):
    """Список объектов с координатами для 3D-карты (MapLibre)."""
    features = [
        p.map_feature()
        for p in ProjectPage.objects.live().order_by("category", "title").specific()
    ]
    return JsonResponse({"projects": features})
