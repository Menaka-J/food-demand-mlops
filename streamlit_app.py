import requests
import streamlit as st
import pandas as pd


API_URL = "http://127.0.0.1:8000"

#page configuration

st.set_page_config(
    page_title="Smart Food Demand Forecasting",
    page_icon="🍽️",
    layout="wide"
)

st.title("Smart Food Demand Forecasting")
st.write(
    "Predict expected food demand using historical sales, "
    "weather and calendar information."
)

#Prediction input section
st.header("Daily Demand Prediction")

col1, col2 = st.columns(2)

with col1:

    prediction_date = st.date_input(
        "Date"
    )

    store = st.selectbox(
        "Store",
        [
            "store_0",
            "store_1",
            "store_2",
            "store_3",
            "store_4",
            "store_5",
            "store_6",
            "store_7",
            "store_8"
        ]
    )

    is_state_holiday = st.selectbox(
        "State Holiday",
        [
            "normal_day",
            "state_holiday",
            "day_after",
            "day_before"
        ]
    )

    is_school_holiday = st.selectbox(
        "School Holiday",
        [
            "normal_day",
            "school_holiday"
        ]
    )

    is_special_day = st.selectbox(
        "Special Day",
        [
            "normal_day",
            "special_day",
            "day_before"
        ]
    )
    
#Weather inputs
with col2:

    temperature_max = st.number_input(
        "Maximum Temperature",
        value=20.0
    )

    temperature_min = st.number_input(
        "Minimum Temperature",
        value=10.0
    )

    temperature_mean = st.number_input(
        "Mean Temperature",
        value=15.0
    )

    sunshine_sum = st.number_input(
        "Sunshine",
        min_value=0.0,
        value=5.0
    )

    precipitation_sum = st.number_input(
        "Precipitation",
        min_value=0.0,
        value=0.0
    )
    
#Prediction button
if st.button(
    "Generate Demand Prediction",
    type="primary"
):

    payload = {

        "date": str(prediction_date),

        "store": store,

        "is_state_holiday": is_state_holiday,
        "is_school_holiday": is_school_holiday,
        "is_special_day": is_special_day,

        "temperature_max": temperature_max,
        "temperature_min": temperature_min,
        "temperature_mean": temperature_mean,

        "sunshine_sum": sunshine_sum,
        "precipitation_sum": precipitation_sum
    }

    response = requests.post(
        f"{API_URL}/predict",
        json=payload
    )

    if response.status_code == 200:

        result = response.json()

        st.success("Prediction generated successfully.")

        st.metric(
            "Predicted Demand",
            f"{result['prediction']:.3f}"
        )

    else:

        st.error(
            response.json().get(
                "detail",
                "Prediction failed."
            )
        )

#Add actual-sales section
st.header("Record Actual Sales")

actual_date = st.date_input(
    "Actual Sales Date"
)

actual_store = st.selectbox(
    "Actual Sales Store",
    [
        "store_0",
        "store_1",
        "store_2",
        "store_3",
        "store_4",
        "store_5",
        "store_6",
        "store_7",
        "store_8"
    ],
    key="actual_store"
)

actual_sales = st.number_input(
    "Actual Sales",
    value=0.0
)

#Add actual-sales button
if st.button("Save Actual Sales"):

    payload = {
        "date": str(actual_date),
        "store": actual_store,
        "actual_sales": actual_sales
    }

    response = requests.post(
        f"{API_URL}/actual",
        json=payload
    )

    if response.status_code == 200:

        st.success(
            "Actual sales recorded successfully."
        )

    else:

        st.error(
            response.json().get(
                "detail",
                "Unable to save actual sales."
            )
        )
        
#Add records display
st.header("Prediction History")

if st.button("Refresh Records"):

    response = requests.get(
        f"{API_URL}/records"
    )

    if response.status_code == 200:

        records = response.json()

        if records:

            df = pd.DataFrame(records)

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.info("No records available.")
            
