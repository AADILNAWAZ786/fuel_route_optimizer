from django.http import JsonResponse
from routing.services.fuel_service import optimize_route

def route_optimizer(request):
    start = request.GET.get("start")
    end = request.GET.get("end")

    if not start or not end:
        return JsonResponse({"error": "start and end are required"}, status=400)

    try:
        result = optimize_route(start, end)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)