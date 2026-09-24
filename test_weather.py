from datetime import date

from app.config import get_canteen
from app.weather import get_weather


canteen = get_canteen("store_0")

weather = get_weather(
    latitude=canteen.latitude,
    longitude=canteen.longitude,
    target_date=date.today(),
)

print("=" * 60)
print("WEATHER TEST")
print("=" * 60)

print(f"Canteen : {canteen.name}")
print(f"Location: {canteen.city}, {canteen.state}")
print()

for key, value in weather.items():
    print(f"{key}: {value}")