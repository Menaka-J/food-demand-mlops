from app.config import get_all_canteens


print("=" * 60)
print("CANTEEN CONFIGURATION")
print("=" * 60)

canteens = get_all_canteens()

print(f"Number of canteens: {len(canteens)}")
print()

for canteen in canteens:
    print(
        f"{canteen.store_id} | "
        f"{canteen.name} | "
        f"{canteen.city}, {canteen.state} | "
        f"Baseline={canteen.initial_baseline_portions} | "
        f"Buffer={canteen.safety_buffer_percent}%"
    )