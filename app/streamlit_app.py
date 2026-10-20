import streamlit as st
import requests
from datetime import date
import os 

API_URL = os.getenv("API_URL","http://127.0.0.1:8000")
TIMEOUT = 10

st.set_page_config(
    page_title="Smart Food Demand Planner",
    page_icon="🍽️",
    layout="wide",
)

st.title("Smart Food Demand Planner")

# Simple top navigation: tabs appear across the top of the page.
food_tab, dashboard_tab, calibration_tab = st.tabs(
    ["Food Plan", " Dashboard", " Operational Calibration"]
)


def api_get(path, timeout=TIMEOUT):
    response = requests.get(f"{API_URL}{path}", timeout=timeout)
    response.raise_for_status()
    return response.json()


def api_post(path, payload, timeout=30):
    response = requests.post(f"{API_URL}{path}", json=payload, timeout=timeout)
    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(f"HTTP {response.status_code}: {detail}")
    return response.json()


def load_canteens():
    try:
        canteens = api_get("/canteens")
        if not canteens:
            st.error("No canteens were returned by the backend.")
            st.stop()
        return canteens
    except requests.RequestException as exc:
        st.error(
            f"Cannot connect to FastAPI at {API_URL}. "
            f"Start the backend and refresh this page. Details: {exc}"
        )
        st.stop()


def portion_text(value):
    if value is None:
        return "N/A"
    try:
        return f"{float(value):,.0f} portions"
    except (TypeError, ValueError):
        return str(value)


def completed_records(records):
    return [r for r in records if r.get("actual_portions") is not None]


def render_food_plan(canteens):
    st.subheader("Create today's food plan")

    names = [c["name"] for c in canteens]
    selected_name = st.selectbox("Canteen", names, key="food_canteen")
    canteen = next(c for c in canteens if c["name"] == selected_name)

    col_location, col_date = st.columns(2)
    with col_location:
        st.info(
            f"**Location:** {canteen.get('city', 'N/A')}, "
            f"{canteen.get('state', 'N/A')}"
        )
    with col_date:
        prediction_date = st.date_input(
            "Prediction date", value=date.today(), key="food_prediction_date"
        )

    st.markdown("**Day details**")
    c1, c2, c3 = st.columns(3)
    with c1:
        state_holiday = st.selectbox(
            "State holiday", ["Normal Day", "Holiday"], key="food_state_holiday"
        )
    with c2:
        school_holiday = st.selectbox(
            "School holiday", ["Normal Day", "Holiday"], key="food_school_holiday"
        )
    with c3:
        special_day = st.selectbox(
            "Special day", ["Normal Day", "Special Day"], key="food_special_day"
        )

    if st.button(
        "Generate Food Plan",
        type="primary",
        use_container_width=True,
        key="generate_food_plan",
    ):
        payload = {
            "store_id": canteen["store_id"],
            "prediction_date": prediction_date.isoformat(),
            "is_state_holiday": state_holiday == "Holiday",
            "is_school_holiday": school_holiday == "Holiday",
            "is_special_day": special_day == "Special Day",
        }
        try:
            with st.spinner("Getting weather and generating prediction..."):
                result = api_post("/predict", payload, timeout=30)
            st.session_state["prediction"] = result
            st.session_state["prediction_context"] = {
                "store_id": canteen["store_id"],
                "canteen_name": canteen["name"],
                "prediction_date": prediction_date.isoformat(),
            }
            st.session_state.pop("actual_saved", None)
            st.success("Food plan generated.")
        except (requests.RequestException, RuntimeError) as exc:
            st.error(f"Prediction failed: {exc}")

    result = st.session_state.get("prediction")
    if not result:
        return

    st.divider()
    st.markdown("**Weather forecast**")
    weather_items = [
        ("Max temperature", "temperature_max", "°C"),
        ("Min temperature", "temperature_min", "°C"),
        ("Average temperature", "temperature_mean", "°C"),
        ("Rainfall", "precipitation_sum", "mm"),
    ]
    cols = st.columns(4)
    for col, (label, key, unit) in zip(cols, weather_items):
        value = result.get(key)
        with col:
            st.metric(label, f"{float(value):.1f} {unit}" if value is not None else "N/A")
    sunshine = result.get("sunshine_sum")
    if sunshine is not None:
        st.caption(f"Sunshine: {float(sunshine):.2f} hours")

    st.markdown("**Recommended preparation**")
    plan_items = [
        ("Expected demand", "expected_portions"),
        ("Safety buffer", "safety_buffer"),
        ("Recommended portions", "recommended_portions"),
    ]
    cols = st.columns(3)
    for col, (label, key) in zip(cols, plan_items):
        with col:
            st.metric(label, portion_text(result.get(key)))

    if result.get("recommended_portions") is not None:
        st.success(f"Prepare approximately {result['recommended_portions']} portions.")

    st.divider()
    st.markdown("**Record actual portions after service**")
    record_id = result.get("record_id")
    if record_id is None:
        st.error("The prediction response is missing record_id. Check the FastAPI /predict response.")
        return

    saved = st.session_state.get("actual_saved")
    if saved and saved.get("record_id", record_id) == record_id:
        st.success("Actual portions saved.")
        actual_result = saved
    else:
        actual = st.number_input(
            "Actual portions sold / consumed",
            min_value=0,
            step=1,
            value=0,
            key=f"actual_portions_{record_id}",
        )
        if st.button("Save Actual Portions", key=f"save_actual_{record_id}"):
            try:
                actual_result = api_post(
                    f"/actual/{record_id}",
                    {"actual_portions": int(actual)},
                    timeout=15,
                )
                actual_result.setdefault("record_id", record_id)
                st.session_state["actual_saved"] = actual_result
                st.rerun()
            except (requests.RequestException, RuntimeError) as exc:
                st.error(f"Could not save actual portions: {exc}")
        return

    expected = actual_result.get("expected_portions", result.get("expected_portions"))
    actual_value = actual_result.get("actual_portions")
    error = actual_result.get("absolute_error")
    st.markdown("**Prediction result**")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Expected", portion_text(expected))
    with c2:
        st.metric("Actual", portion_text(actual_value))
    with c3:
        st.metric("Absolute error", portion_text(error))

    try:
        difference = float(actual_value) - float(expected)
        if difference > 0:
            st.info(f"Actual demand was {difference:.0f} portions higher than expected.")
        elif difference < 0:
            st.info(f"Actual demand was {abs(difference):.0f} portions lower than expected.")
        else:
            st.success("Expected demand matched actual demand.")
    except (TypeError, ValueError):
        pass


def render_dashboard():
    st.subheader("Prediction monitoring")
    try:
        metrics = api_get("/metrics")
        records = api_get("/records")
    except requests.RequestException as exc:
        st.error(f"Could not load dashboard data: {exc}")
        return

    done = completed_records(records)
    mae, rmse, mean_error = (
        metrics.get("mae"),
        metrics.get("rmse"),
        metrics.get("mean_error"),
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Completed records", metrics.get("records_with_actuals", len(done)))
    with c2:
        st.metric("MAE", f"{mae:.2f}" if mae is not None else "N/A")
    with c3:
        st.metric("RMSE", f"{rmse:.2f}" if rmse is not None else "N/A")
    with c4:
        st.metric("Mean error", f"{mean_error:+.2f}" if mean_error is not None else "N/A")
    st.caption("Error values are in portions. MAE measures average absolute error; RMSE gives more weight to larger errors.")

    if mean_error is not None:
        st.info(f"Mean error (backend convention): {mean_error:+.2f} portions.")

    st.divider()
    st.markdown("**Completed prediction history**")
    if not done:
        st.info("No actual results have been recorded yet.")
    else:
        rows = [{
            "Canteen": r.get("canteen_name", r.get("store_id")),
            "Date": r.get("prediction_date"),
            "Expected": r.get("expected_portions"),
            "Recommended": r.get("recommended_portions"),
            "Actual": r.get("actual_portions"),
            "Absolute error": r.get("absolute_error"),
            "Model version": r.get("model_version"),
        } for r in done]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        grouped = {}
        for r in done:
            name = r.get("canteen_name", r.get("store_id", "Unknown"))
            grouped.setdefault(name, []).append(r)

        rows = []
        for name, group in grouped.items():
            errors = [float(r["absolute_error"]) for r in group if r.get("absolute_error") is not None]
            expected_values = [float(r["expected_portions"]) for r in group if r.get("expected_portions") is not None]
            actual_values = [float(r["actual_portions"]) for r in group if r.get("actual_portions") is not None]
            rows.append({
                "Canteen": name,
                "Completed records": len(group),
                "MAE (portions)": round(sum(errors) / len(errors), 2) if errors else None,
                "Average expected": round(sum(expected_values) / len(expected_values), 2) if expected_values else None,
                "Average actual": round(sum(actual_values) / len(actual_values), 2) if actual_values else None,
            })
        st.divider()
        st.markdown("**Performance by canteen**")
        st.dataframe(rows, use_container_width=True, hide_index=True)


def render_calibration(canteens):
    st.subheader("Canteen calibration status")
    names = [c["name"] for c in canteens]
    selected_name = st.selectbox("Canteen", names, key="calibration_canteen")
    canteen = next(c for c in canteens if c["name"] == selected_name)

    try:
        status = api_get(f"/calibration/{canteen['store_id']}")
    except requests.RequestException as exc:
        st.error(f"Could not load calibration status: {exc}")
        status = None

    if status:
        observations = int(status.get("observations", 0) or 0)
        required = max(int(status.get("required_observations", 5) or 5), 1)
        state = status.get("status", "not_calibrated")
        method = status.get("method", "initial_baseline")
        st.progress(min(observations / required, 1.0))
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Observations", f"{observations} / {required}")
        with c2:
            st.metric("Status", "Calibrated" if state == "calibrated" else "Collecting data")
        with c3:
            st.metric("Method", method.replace("_", " ").title())

        if state == "calibrated":
            c1, c2, c3 = st.columns(3)
            coefficient, intercept, training_mae = (
                status.get("coefficient"),
                status.get("intercept"),
                status.get("training_mae"),
            )
            with c1:
                st.metric("Coefficient", f"{coefficient:.4f}" if coefficient is not None else "N/A")
            with c2:
                st.metric("Intercept", f"{intercept:.4f}" if intercept is not None else "N/A")
            with c3:
                st.metric("Calibration MAE", f"{training_mae:.2f} portions" if training_mae is not None else "N/A")
        else:
            st.info(
                f"Initial baseline is in use. Collect {max(required - observations, 0)} "
                "more completed observation(s) before calibration can be trained."
            )

    st.divider()
    st.markdown("**All canteens**")
    try:
        all_calibrations = api_get("/calibration")
        records = completed_records(api_get("/records"))
        rows = []
        for item in canteens:
            sid = item["store_id"]
            info = all_calibrations.get(sid)
            count = sum(1 for r in records if r.get("store_id") == sid)
            rows.append({
                "Canteen": item["name"],
                "Observations": f"{info.get('observations', count) if info else count} / 5",
                "Status": "Calibrated" if info else "Not calibrated",
                "Method": info.get("method", "linear_calibration") if info else "initial_baseline",
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)
    except requests.RequestException as exc:
        st.error(f"Could not load calibration summary: {exc}")


with food_tab:
    canteens = load_canteens()
    render_food_plan(canteens)

with dashboard_tab:
    render_dashboard()

with calibration_tab:
    canteens = load_canteens()
    render_calibration(canteens)

st.caption("Smart Food Demand Forecasting and Waste Reduction System")
