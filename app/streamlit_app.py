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

    request_data = {

        "store_id": (
            selected_canteen["store_id"]
        ),

        "prediction_date": (
            prediction_date.isoformat()
        ),

        "is_state_holiday": (
            is_state_holiday
        ),

        "is_school_holiday": (
            is_school_holiday
        ),

        "is_special_day": (
            is_special_day
        )
    }


    try:

        response = requests.post(
            f"{API_URL}/predict",
            json=request_data,
            timeout=30
        )


        if response.status_code == 200:

            result = response.json()

            st.session_state[
                "prediction"
            ] = result

            # Clear previous actual result
            st.session_state.pop(
                "actual_saved",
                None
            )

        else:

            st.error(
                f"Prediction failed: "
                f"{response.text}"
            )


    except requests.RequestException as e:

        st.error(
            f"Unable to connect to FastAPI: {e}"
        )


# =========================================================
# DISPLAY PREDICTION
# =========================================================

if "prediction" in st.session_state:

    result = st.session_state[
        "prediction"
    ]


    # =====================================================
    # WEATHER INFORMATION
    # =====================================================

    st.divider()

    st.subheader(
        "🌦️ Weather Information"
    )

    weather_col1, weather_col2, weather_col3, weather_col4 = (
        st.columns(4)
    )


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

    st.subheader(
        "🍱 Today's Food Plan"
    )

    plan_col1, plan_col2, plan_col3 = (
        st.columns(3)
    )


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


    # =====================================================
    # END-OF-DAY ACTUAL PORTIONS
    # =====================================================

    st.divider()

    st.subheader(
        "📊 End-of-Day Record"
    )

    st.write(
        "After the meal service ends, enter the actual "
        "number of portions sold or consumed."
    )


    actual_portions = st.number_input(
        "Actual Portions Sold / Consumed",
        min_value=0,
        step=1,
        value=0
    )


    if st.button(
        "💾 SAVE ACTUAL",
        use_container_width=True
    ):

        actual_data = {
            "actual_portions": actual_portions
        }


        try:

            response = requests.post(
                f"{API_URL}/actual/"
                f"{result['record_id']}",
                json=actual_data,
                timeout=10
            )


            if response.status_code == 200:

                actual_result = (
                    response.json()
                )

                st.session_state[
                    "actual_saved"
                ] = actual_result

                st.success(
                    "Actual portions saved successfully!"
                )

            else:

                st.error(
                    "Unable to save actual portions: "
                    f"{response.text}"
                )


        except requests.RequestException as e:

            st.error(
                "Unable to connect to FastAPI: "
                f"{e}"
            )


    # =====================================================
    # DISPLAY ACTUAL VS PREDICTED
    # =====================================================

    if "actual_saved" in st.session_state:

        actual_result = (
            st.session_state[
                "actual_saved"
            ]
        )


        st.divider()

        st.subheader(
            "📈 Prediction vs Actual"
        )


        comparison_col1, comparison_col2, comparison_col3 = (
            st.columns(3)
        )


        with comparison_col1:

            st.metric(
                "Expected Demand",
                f"{actual_result['expected_portions']:.0f} portions"
            )


        with comparison_col2:

            st.metric(
                "Actual Sold",
                f"{actual_result['actual_portions']} portions"
            )


        with comparison_col3:

            st.metric(
                "Absolute Error",
                f"{actual_result['absolute_error']:.0f} portions"
            )


        difference = (
            actual_result["actual_portions"]
            - actual_result["expected_portions"]
        )


        if difference > 0:

            st.info(
                f"Actual demand was "
                f"{abs(difference):.0f} portions "
                f"higher than expected."
            )

        elif difference < 0:

            st.info(
                f"Actual demand was "
                f"{abs(difference):.0f} portions "
                f"lower than expected."
            )

        else:

            st.success(
                "Prediction exactly matched "
                "the actual demand."
            )


# =========================================================
# MLOPS MONITORING DASHBOARD
# =========================================================

st.divider()

st.header(
    "📊 MLOps Monitoring Dashboard"
)

st.caption(
    "Monitor prediction accuracy using completed "
    "operational records."
)


# =========================================================
# LOAD MONITORING DATA
# =========================================================

try:

    metrics_response = requests.get(
        f"{API_URL}/metrics",
        timeout=10
    )

    records_response = requests.get(
        f"{API_URL}/records",
        timeout=10
    )

    metrics_response.raise_for_status()
    records_response.raise_for_status()

    metrics = metrics_response.json()
    records = records_response.json()


except requests.RequestException as e:

    st.error(
        f"Unable to load monitoring data: {e}"
    )


else:

    # =====================================================
    # OVERALL PERFORMANCE
    # =====================================================

    st.subheader(
        "📈 Overall Model Performance"
    )


    metric_col1, metric_col2, metric_col3, metric_col4 = (
        st.columns(4)
    )


    with metric_col1:

        st.metric(
            "Completed Records",
            metrics.get(
                "records_with_actuals",
                0
            )
        )


    with metric_col2:

        mae = metrics.get("mae")

        st.metric(
            "MAE",
            (
                f"{mae:.2f} portions"
                if mae is not None
                else "N/A"
            )
        )


    with metric_col3:

        rmse = metrics.get("rmse")

        st.metric(
            "RMSE",
            (
                f"{rmse:.2f} portions"
                if rmse is not None
                else "N/A"
            )
        )


    with metric_col4:

        mean_error = metrics.get(
            "mean_error"
        )

        st.metric(
            "Mean Error",
            (
                f"{mean_error:+.2f} portions"
                if mean_error is not None
                else "N/A"
            )
        )


    # =====================================================
    # ERROR INTERPRETATION
    # =====================================================

    if mean_error is not None:

        if mean_error > 0:

            st.info(
                "Predictions are currently higher "
                "than actual demand by an average of "
                f"{mean_error:.2f} portions."
            )

        elif mean_error < 0:

            st.info(
                "Predictions are currently lower "
                "than actual demand by an average of "
                f"{abs(mean_error):.2f} portions."
            )

        else:

            st.success(
                "Average prediction error is "
                "currently zero."
            )


    # =====================================================
    # PREDICTION HISTORY
    # =====================================================

    st.subheader(
        "📋 Prediction History"
    )


    completed_records = [

        record

        for record in records

        if record.get(
            "actual_portions"
        ) is not None

    ]


    if completed_records:

        history_rows = []


        for record in completed_records:

            history_rows.append({

                "Canteen": record.get(
                    "canteen_name"
                ),

                "Date": record.get(
                    "prediction_date"
                ),

                "Expected": record.get(
                    "expected_portions"
                ),

                "Recommended": record.get(
                    "recommended_portions"
                ),

                "Actual": record.get(
                    "actual_portions"
                ),

                "Absolute Error": record.get(
                    "absolute_error"
                ),

            })


        st.dataframe(
            history_rows,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "No completed operational "
            "records available yet."
        )


    # =====================================================
    # PERFORMANCE BY CANTEEN
    # =====================================================

    st.subheader(
        "🏢 Performance by Canteen"
    )


    if completed_records:

        canteen_stats = {}


        for record in completed_records:

            canteen = record.get(
                "canteen_name",
                record.get(
                    "store_id"
                )
            )

            error = record.get(
                "absolute_error"
            )

            expected = record.get(
                "expected_portions"
            )

            actual = record.get(
                "actual_portions"
            )


            if canteen not in canteen_stats:

                canteen_stats[canteen] = {

                    "errors": [],

                    "expected": [],

                    "actual": []

                }


            if error is not None:

                canteen_stats[
                    canteen
                ]["errors"].append(
                    float(error)
                )


            if expected is not None:

                canteen_stats[
                    canteen
                ]["expected"].append(
                    float(expected)
                )


            if actual is not None:

                canteen_stats[
                    canteen
                ]["actual"].append(
                    float(actual)
                )


        canteen_rows = []


        for canteen, values in canteen_stats.items():

            errors = values["errors"]


            if errors:

                canteen_mae = (
                    sum(errors)
                    / len(errors)
                )


                canteen_rows.append({

                    "Canteen": canteen,

                    "Records": len(errors),

                    "MAE": round(
                        canteen_mae,
                        2
                    ),

                    "Average Expected": round(

                        sum(
                            values["expected"]
                        )
                        / len(
                            values["expected"]
                        ),

                        2

                    ),

                    "Average Actual": round(

                        sum(
                            values["actual"]
                        )
                        / len(
                            values["actual"]
                        ),

                        2

                    )

                })


        st.dataframe(
            canteen_rows,
            use_container_width=True,
            hide_index=True
        )


    else:

        st.info(
            "Canteen-level monitoring will appear "
            "after actual operational records "
            "are collected."
        )


    # =====================================================
    # OPERATIONAL CALIBRATION
    # =====================================================

    st.divider()

    st.header(
        "🔧 Operational Calibration"
    )

    st.caption(
        "Calibration learns the relationship between "
        "the public-data model prediction and actual "
        "portion demand at each canteen."
    )


    # =====================================================
    # SELECTED CANTEEN CALIBRATION STATUS
    # =====================================================

    st.subheader(
        "📍 Selected Canteen Calibration"
    )


    selected_store_id = (
        selected_canteen["store_id"]
    )


    try:

        calibration_response = requests.get(
            f"{API_URL}/calibration/"
            f"{selected_store_id}",
            timeout=10
        )

        calibration_response.raise_for_status()

        calibration_status = (
            calibration_response.json()
        )


        observations = calibration_status.get(
            "observations",
            0
        )

        required = calibration_status.get(
            "required_observations",
            5
        )

        calibration_state = (
            calibration_status.get(
                "status"
            )
        )

        calibration_method = (
            calibration_status.get(
                "method"
            )
        )


        st.write(
            f"**Canteen:** "
            f"{selected_canteen['name']}"
        )


        st.progress(
            min(
                observations / required,
                1.0
            )
        )


        calibration_col1, calibration_col2 = (
            st.columns(2)
        )


        with calibration_col1:

            st.metric(
                "Completed Observations",
                f"{observations} / {required}"
            )


        with calibration_col2:

            if calibration_state == "calibrated":

                st.metric(
                    "Status",
                    "✅ Calibrated"
                )

            else:

                st.metric(
                    "Status",
                    "⏳ Collecting Data"
                )


        if calibration_state == "calibrated":

            st.success(
                "This canteen has a learned "
                "operational calibration."
            )


            if calibration_method:

                st.write(
                    f"**Method:** "
                    f"{calibration_method}"
                )


            coefficient = (
                calibration_status.get(
                    "coefficient"
                )
            )

            intercept = (
                calibration_status.get(
                    "intercept"
                )
            )

            training_mae = (
                calibration_status.get(
                    "training_mae"
                )
            )


            if coefficient is not None:

                st.write(
                    f"**Coefficient:** "
                    f"{coefficient:.4f}"
                )


            if intercept is not None:

                st.write(
                    f"**Intercept:** "
                    f"{intercept:.4f}"
                )


            if training_mae is not None:

                st.write(
                    f"**Calibration MAE:** "
                    f"{training_mae:.2f} portions"
                )


        else:

            remaining = max(
                required - observations,
                0
            )


            if remaining > 0:

                st.info(
                    f"Collect {remaining} more "
                    f"completed operational "
                    f"observation(s) before "
                    f"calibration can be trained."
                )


            st.write(
                "**Current method:** "
                "Initial baseline"
            )


    except requests.RequestException as e:

        st.error(
            "Unable to load calibration status: "
            f"{e}"
        )


    # =====================================================
    # ALL CANTEEN CALIBRATION STATUS
    # =====================================================

    st.subheader(
        "🏢 Calibration Status by Canteen"
    )


    try:

        all_calibration_response = requests.get(
            f"{API_URL}/calibration",
            timeout=10
        )

        all_calibration_response.raise_for_status()

        all_calibrations = (
            all_calibration_response.json()
        )


        calibration_rows = []


        for canteen in canteens:

            store_id = canteen[
                "store_id"
            ]

            canteen_name = canteen[
                "name"
            ]


            calibration_info = (
                all_calibrations.get(
                    store_id
                )
            )


            # ---------------------------------------------
            # Count completed operational records
            # ---------------------------------------------

            completed_count = sum(

                1

                for record in completed_records

                if record.get(
                    "store_id"
                ) == store_id

            )


            if calibration_info:

                observations = (
                    calibration_info.get(
                        "observations",
                        completed_count
                    )
                )

                status = "Calibrated"

                method = calibration_info.get(
                    "method",
                    "linear_calibration"
                )

            else:

                observations = (
                    completed_count
                )

                status = "Not Calibrated"

                method = "initial_baseline"


            calibration_rows.append({

                "Canteen": canteen_name,

                "Observations": (
                    f"{observations} / 5"
                ),

                "Status": status,

                "Method": method

            })


        st.dataframe(
            calibration_rows,
            use_container_width=True,
            hide_index=True
        )


    except requests.RequestException as e:

        st.error(
            "Unable to load all calibration "
            f"statuses: {e}"
        )