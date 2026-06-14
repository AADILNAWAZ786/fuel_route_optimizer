import math
import polyline

from routing.models import FuelStation
from routing.services.ors_service import geocode_location, get_route

MPG = 10
MAX_RANGE_MILES = 500

def _haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi    = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def optimize_route(start_location, end_location):
    start_coords = geocode_location(start_location)
    end_coords   = geocode_location(end_location)

    if not start_coords: raise ValueError("Invalid start location")
    if not end_coords: raise ValueError("Invalid end location")

    route = get_route(start_coords, end_coords)

    distance_meters  = route["routes"][0]["summary"]["distance"]
    distance_miles   = distance_meters / 1609.34
    fuel_needed      = round(distance_miles / MPG, 2)

    route_points = polyline.decode(route["routes"][0]["geometry"])

    lats = [p[0] for p in route_points]
    lons = [p[1] for p in route_points]
    min_lat, max_lat = min(lats) - 1.0, max(lats) + 1.0
    min_lon, max_lon = min(lons) - 1.0, max(lons) + 1.0

    stations = list(
        FuelStation.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lon,
            longitude__lte=max_lon,
        ).values("truckstop_name", "city", "state", "retail_price", "latitude", "longitude",)
    )

    sampled_points = route_points[::200] or route_points

    def _is_near_route(station, max_miles=10):
        slat = float(station["latitude"])
        slon = float(station["longitude"])
        for rlat, rlon in sampled_points:
            if _haversine_miles(slat, slon, rlat, rlon) <= max_miles: return True
        return False

    stations_on_route = [s for s in stations if _is_near_route(s)]

    stops_needed = max(0, math.ceil(distance_miles / MAX_RANGE_MILES) - 1)

    recommended_stops = []
    used_names        = set()
    route_len         = len(route_points)

    for stop_index in range(stops_needed):
        target_miles     = (stop_index + 1) * MAX_RANGE_MILES
        segment_fraction = target_miles / distance_miles
        route_idx        = min(int(segment_fraction * route_len), route_len - 1)
        target_lat, target_lon = route_points[route_idx]

        candidate = None
        for search_radius in (50, 100, 200):
            segment_candidates = [
                s for s in stations_on_route
                if s["truckstop_name"] not in used_names
                and _haversine_miles(
                    float(s["latitude"]), float(s["longitude"]),
                    target_lat, target_lon,
                ) <= search_radius
            ]
            if segment_candidates:
                candidate = min(segment_candidates, key=lambda s: float(s["retail_price"]))
                break

        if candidate:
            recommended_stops.append({
                "stop_number":    stop_index + 1,
                "truckstop_name": candidate["truckstop_name"],
                "city":           (candidate["city"] or "").strip(),
                "state":          candidate["state"],
                "retail_price":   float(candidate["retail_price"]),
            })
            used_names.add(candidate["truckstop_name"])
    estimated_cost = _calculate_actual_cost(distance_miles, recommended_stops)

    return {
        "distance_miles":  round(distance_miles, 2),
        "fuel_needed":     fuel_needed,
        "estimated_cost":  estimated_cost,
        "route_summary": {
            "distance_meters":  route["routes"][0]["summary"]["distance"],
            "duration_seconds": route["routes"][0]["summary"]["duration"],
        },
        "route_map": {
            "geometry": route["routes"][0]["geometry"],
        },
        "recommended_stops": recommended_stops,
    }

def _calculate_actual_cost(distance_miles, recommended_stops):

    if not recommended_stops:
        from django.db.models import Avg
        avg = FuelStation.objects.aggregate(avg=Avg("retail_price"))["avg"] or 3.50
        return round((distance_miles / MPG) * float(avg), 2)

    total_cost    = 0.0
    miles_covered = 0.0

    for stop in recommended_stops:
        miles_at_stop  = stop["stop_number"] * MAX_RANGE_MILES
        miles_this_leg = min(miles_at_stop, distance_miles) - miles_covered
        miles_covered  = miles_at_stop
        total_cost    += (miles_this_leg / MPG) * float(stop["retail_price"])

    remaining = distance_miles - miles_covered
    if remaining > 0:
        total_cost += (remaining / MPG) * float(recommended_stops[-1]["retail_price"])

    return round(total_cost, 2)