from dataclasses import dataclass


@dataclass(frozen=True)
class CanteenConfig:
    store_id: str
    name: str
    city: str
    state: str
    latitude: float
    longitude: float
    initial_baseline_portions: int
    safety_buffer_percent: float


CANTEENS = {
    "store_0": CanteenConfig(
        store_id="store_0",
        name="Chennai Central Canteen",
        city="Chennai",
        state="Tamil Nadu",
        latitude=13.0827,
        longitude=80.2707,
        initial_baseline_portions=250,
        safety_buffer_percent=5.0,
    ),

    "store_1": CanteenConfig(
        store_id="store_1",
        name="Coimbatore Tech Canteen",
        city="Coimbatore",
        state="Tamil Nadu",
        latitude=11.0168,
        longitude=76.9558,
        initial_baseline_portions=220,
        safety_buffer_percent=5.0,
    ),

    "store_2": CanteenConfig(
        store_id="store_2",
        name="Madurai Campus Canteen",
        city="Madurai",
        state="Tamil Nadu",
        latitude=9.9252,
        longitude=78.1198,
        initial_baseline_portions=180,
        safety_buffer_percent=5.0,
    ),

    "store_3": CanteenConfig(
        store_id="store_3",
        name="Tiruchirappalli Campus Canteen",
        city="Tiruchirappalli",
        state="Tamil Nadu",
        latitude=10.7905,
        longitude=78.7047,
        initial_baseline_portions=200,
        safety_buffer_percent=5.0,
    ),

    "store_4": CanteenConfig(
        store_id="store_4",
        name="Salem City Canteen",
        city="Salem",
        state="Tamil Nadu",
        latitude=11.6643,
        longitude=78.1460,
        initial_baseline_portions=230,
        safety_buffer_percent=5.0,
    ),

    "store_5": CanteenConfig(
        store_id="store_5",
        name="Tiruppur Industrial Canteen",
        city="Tiruppur",
        state="Tamil Nadu",
        latitude=11.1085,
        longitude=77.3411,
        initial_baseline_portions=240,
        safety_buffer_percent=5.0,
    ),

    "store_6": CanteenConfig(
        store_id="store_6",
        name="Erode Campus Canteen",
        city="Erode",
        state="Tamil Nadu",
        latitude=11.3410,
        longitude=77.7172,
        initial_baseline_portions=190,
        safety_buffer_percent=5.0,
    ),

    "store_7": CanteenConfig(
        store_id="store_7",
        name="Vellore Institute Canteen",
        city="Vellore",
        state="Tamil Nadu",
        latitude=12.9165,
        longitude=79.1325,
        initial_baseline_portions=260,
        safety_buffer_percent=5.0,
    ),

    "store_8": CanteenConfig(
        store_id="store_8",
        name="Thoothukudi Port Canteen",
        city="Thoothukudi",
        state="Tamil Nadu",
        latitude=8.7642,
        longitude=78.1348,
        initial_baseline_portions=210,
        safety_buffer_percent=5.0,
    ),
}


def get_canteen(store_id: str) -> CanteenConfig:
    if store_id not in CANTEENS:
        raise ValueError(f"Unknown canteen: {store_id}")

    return CANTEENS[store_id]


def get_all_canteens():
    return list(CANTEENS.values())