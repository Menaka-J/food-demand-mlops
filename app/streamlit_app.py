import streamlit as st
import requests
from datetime import date


# =========================================================
# CONFIGURATION
# =========================================================

API_URL = "http://127.0.0.1:8000"


# =========================================================
# STREAMLIT PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Food Demand Planner",
    page_icon="🍽️",
    layout="wide"
)


# =========================================================
# PAGE HEADER
# =========================================================

st.title("🍽️ Smart Food Demand Planner")
st.caption("Food demand prediction and waste reduction system")

st.divider()


# =========================================================
# LOAD CANTEENS FROM FASTAPI
# =========================================================

try:
    response = requests.get(
        f"{API_URL}/canteens",
        timeout=5
    )

    response.raise_for_status()

    canteens = response.json()

except requests.RequestException as e:
    st.error(
        f"Unable to connect to the FastAPI backend: {e}"
    )
    st.stop()


# =========================================================
# CANTEEN SELECTION
# =========================================================

st.subheader("📍 Canteen Details")

canteen_names = [
    canteen["name"]
    for canteen in canteens
]

selected_name = st.selectbox(
    "Canteen",
    canteen_names
)

selected_canteen = next(
    canteen
    for canteen in canteens
    if canteen["name"] == selected_name
)

st.info(
    f"**Location:** "
    f"{selected_canteen['city']}, "
    f"{selected_canteen['state']}"
)


# =========================================================
# PREDICTION DATE
# =========================================================

prediction_date = st.date_input(
    "Prediction Date",
    value=date.today()
)


# =========================================================
# CALENDAR INFORMATION
# =========================================================

st.subheader("📅 Calendar Information")

col1, col2, col3 = st.columns(3)


with col1:

    state_holiday = st.selectbox(
        "State Holiday",
        ["Normal Day", "Holiday"]
    )


with col2:

    school_holiday = st.selectbox(
        "School Holiday",
        ["Normal Day", "Holiday"]
    )


with col3:

    special_day = st.selectbox(
        "Special Day",
        ["Normal Day", "Special Day"]
    )


# Convert UI selections to Boolean values

is_state_holiday = (
    state_holiday == "Holiday"
)

is_school_holiday = (
    school_holiday == "Holiday"
)

is_special_day = (
    special_day == "Special Day"
)


st.divider()


# =========================================================
# GENERATE FOOD PLAN
# =========================================================

if st.button(
    "🍽️ GENERATE FOOD PLAN",
    type="primary",
    use_container_width=True
):

    # -----------------------------------------------------
    # Prepare request for FastAPI
    # -----------------------------------------------------

    request_data = {
        "store_id": selected_canteen["store_id"],
        "prediction_date": prediction_date.isoformat(),
        "is_state_holiday": is_state_holiday,
        "is_school_holiday": is_school_holiday,
        "is_special_day": is_special_day
    }


    # -----------------------------------------------------
    # Send prediction request
    # -----------------------------------------------------

    try:

        response = requests.post(
            f"{API_URL}/predict",
            json=request_data,
            timeout=30
        )


        # -------------------------------------------------
        # Successful prediction
        # -------------------------------------------------

        if response.status_code == 200:

            result = response.json()

            # Store prediction in Streamlit session
            st.session_state["prediction"] = result

        else:

            st.error(
                f"Prediction failed: {response.text}"
            )


    except requests.RequestException as e:

        st.error(
            f"Unable to connect to FastAPI: {e}"
        )


# =========================================================
# DISPLAY PREDICTION
# =========================================================

if "prediction" in st.session_state:

    result = st.session_state["prediction"]


    # =====================================================
    # WEATHER INFORMATION
    # =====================================================

    st.divider()

    st.subheader("🌦️ Weather Information")

    weather_col1, weather_col2, weather_col3, weather_col4 = st.columns(4)


    with weather_col1:

        st.metric(
            "Maximum Temperature",
            f"{result['temperature_max']:.1f} °C"
        )


    with weather_col2:

        st.metric(
            "Minimum Temperature",
            f"{result['temperature_min']:.1f} °C"
        )


    with weather_col3:

        st.metric(
            "Average Temperature",
            f"{result['temperature_mean']:.1f} °C"
        )


    with weather_col4:

        st.metric(
            "Rainfall",
            f"{result['precipitation_sum']:.1f} mm"
        )


    st.caption(
        f"☀️ Sunshine: "
        f"{result['sunshine_sum']:.2f} hours"
    )


    # =====================================================
    # FOOD PLAN
    # =====================================================

    st.divider()

    st.subheader("🍱 Today's Food Plan")

    plan_col1, plan_col2, plan_col3 = st.columns(3)


    with plan_col1:

        st.metric(
            "Expected Demand",
            f"{result['expected_portions']:.0f} portions"
        )


    with plan_col2:

        st.metric(
            "Safety Buffer",
            f"{result['safety_buffer']} portions"
        )


    with plan_col3:

        st.metric(
            "Recommended Preparation",
            f"{result['recommended_portions']} portions"
        )


    # =====================================================
    # FINAL RECOMMENDATION
    # =====================================================

    st.success(
        f"### 🍱 Prepare "
        f"{result['recommended_portions']} portions"
    )