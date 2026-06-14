# Fuel Route Optimizer API

A Django REST API that calculates the optimal fuel stops for a road trip within the USA.

## Features

- Accepts start and destination locations within the USA
- Uses OpenRouteService for geocoding and route generation
- Calculates total trip distance
- Assumes vehicle mileage of 10 MPG
- Assumes maximum vehicle range of 500 miles per tank
- Finds cost-effective fuel stops along the route
- Returns estimated fuel cost
- Returns route geometry for map visualization
- Minimizes external API calls (single route request)

---

## Tech Stack

- Python 3.14
- Django 6
- OpenRouteService API
- PostgreSQL
- Pandas
- Polyline

---

## Installation

### Clone Repository

```bash
git clone <repository_url>
cd fuel_route_optimizer
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
ORS_API_KEY=YOUR_OPENROUTESERVICE_API_KEY
```

---

## Import Fuel Price Data

```bash
python manage.py import_fuel_data
```

---

## Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Start Server

```bash
python manage.py runserver
```

---

## API Endpoint

### GET

```http
GET /optimize-route/
```

### Parameters

| Parameter | Type | Required |
|-----------|--------|----------|
| start | string | Yes |
| end | string | Yes |

Example:

```http
http://127.0.0.1:8000/optimize-route/?start=Dallas,TX&end=Phoenix,AZ
```

---

## Sample Response

```json
{
  "distance_miles": 1085.48,
  "fuel_needed": 108.55,
  "estimated_cost": 381.05,
  "route_summary": {
    "distance_meters": 1746917,
    "duration_seconds": 57061
  },
  "route_map": {
    "geometry": "encoded_polyline"
  },
  "recommended_stops": [
    {
      "stop_number": 1,
      "truckstop_name": "LOVES TRAVEL STOPS #256",
      "city": "Amarillo",
      "state": "TX",
      "retail_price": 3.29
    }
  ]
}
```

---

## Assumptions

- Vehicle fuel efficiency: 10 MPG
- Vehicle maximum range: 500 miles
- Fuel stop recommendations are selected from stations near the route
- Fuel prices are sourced from the provided CSV dataset
- Route data is obtained from OpenRouteService

---

## Performance

- Uses a single routing API call
- Uses local database fuel data
- Optimized station filtering
- Suitable for long-distance routes

---

## Author

Aadil Nawaz