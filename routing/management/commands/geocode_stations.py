import time

from django.core.management.base import BaseCommand

from routing.models import FuelStation
from routing.services.ors_service import geocode_location


class Command(BaseCommand):
    help = "Geocode fuel stations and save latitude/longitude"

    def handle(self, *args, **kwargs):

        stations = FuelStation.objects.filter(latitude__isnull=True, longitude__isnull=True)[:100]

        self.stdout.write(self.style.WARNING(f"Found {len(stations)} stations to geocode"))

        for station in stations:
            try:
                full_address = (
                    f"{station.address}, "
                    f"{station.city}, "
                    f"{station.state}"
                )

                coords = geocode_location(full_address)

                if coords:
                    station.longitude = coords[0]
                    station.latitude = coords[1]
                    station.save()

                    self.stdout.write(self.style.SUCCESS(f"Geocoded: {station.truckstop_name} " f"({station.latitude}, {station.longitude})"))
                else:
                    self.stdout.write(self.style.ERROR(f"No coordinates found for: {station.truckstop_name}"))

                time.sleep(1)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed: {station.truckstop_name} - {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Geocoding completed."))