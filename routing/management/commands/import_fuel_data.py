from django.core.management.base import BaseCommand
from routing.models import FuelStation
import pandas as pd


class Command(BaseCommand):
    help = "Import fuel station data"

    def handle(self, *args, **kwargs):
        df = pd.read_csv("data/fuel-prices-for-be-assessment.csv")

        stations = []

        for _, row in df.iterrows():
            stations.append(
                FuelStation(
                    opis_id=row["OPIS Truckstop ID"],
                    truckstop_name=row["Truckstop Name"],
                    address=row["Address"],
                    city=row["City"],
                    state=row["State"],
                    retail_price=row["Retail Price"],
                )
            )

        FuelStation.objects.bulk_create(stations, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f"Imported {len(stations)} fuel stations"))