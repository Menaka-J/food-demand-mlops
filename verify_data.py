import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. Define dataset paths
# --------------------------------------------------

DATA_DIR = Path("data/raw")

train_path = DATA_DIR / "train.csv"
test_path = DATA_DIR / "test.csv"
truth_path = DATA_DIR / "truth.csv"


# --------------------------------------------------
# 2. Check that files exist
# --------------------------------------------------

print("=" * 60)
print("FILE EXISTENCE CHECK")
print("=" * 60)

print(f"train.csv : {train_path.exists()}")
print(f"test.csv  : {test_path.exists()}")
print(f"truth.csv : {truth_path.exists()}")


# --------------------------------------------------
# 3. Load datasets
# --------------------------------------------------

train = pd.read_csv(train_path)
test = pd.read_csv(test_path)
truth = pd.read_csv(truth_path)


# --------------------------------------------------
# 4. Display shapes
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATASET SHAPES")
print("=" * 60)

print(f"Train  : {train.shape}")
print(f"Test   : {test.shape}")
print(f"Truth  : {truth.shape}")


# --------------------------------------------------
# 5. Display columns
# --------------------------------------------------

print("\n" + "=" * 60)
print("TRAIN COLUMNS")
print("=" * 60)

for i, column in enumerate(train.columns, start=1):
    print(f"{i}. {column}")


print("\n" + "=" * 60)
print("TEST COLUMNS")
print("=" * 60)

for i, column in enumerate(test.columns, start=1):
    print(f"{i}. {column}")


print("\n" + "=" * 60)
print("TRUTH COLUMNS")
print("=" * 60)

for i, column in enumerate(truth.columns, start=1):
    print(f"{i}. {column}")


# --------------------------------------------------
# 6. Check target availability
# --------------------------------------------------

print("\n" + "=" * 60)
print("TARGET CHECK")
print("=" * 60)

print(f"'sales' in train : {'sales' in train.columns}")
print(f"'sales' in test  : {'sales' in test.columns}")
print(f"'sales' in truth : {'sales' in truth.columns}")


# --------------------------------------------------
# 7. Display first five rows
# --------------------------------------------------

print("\n" + "=" * 60)
print("TRAIN SAMPLE")
print("=" * 60)

print(train.head())


# --------------------------------------------------
# 8. Display date information
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATE INFORMATION")
print("=" * 60)

if "date" in train.columns:
    train["date"] = pd.to_datetime(train["date"])

    print(f"Minimum date : {train['date'].min()}")
    print(f"Maximum date : {train['date'].max()}")


# --------------------------------------------------
# 9. Missing values
# --------------------------------------------------

print("\n" + "=" * 60)
print("MISSING VALUES — TRAIN")
print("=" * 60)

print(train.isnull().sum())


print("\n" + "=" * 60)
print("PHASE 1 DATA VERIFICATION COMPLETE")
print("=" * 60)