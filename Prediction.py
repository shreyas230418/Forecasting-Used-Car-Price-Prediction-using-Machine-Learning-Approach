import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import os
import base64

def app():
    # ===== Hero Section =====
    st.markdown(
        """
        <div style="text-align:center; padding: 30px; margin-bottom: 20px;">
            <h1 style="
                font-size:48px;
                font-weight:900;
                background: linear-gradient(90deg,#00d2ff,#3a7bd5,#00ffae,#ff007f);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin: 0;
            ">🚗 Car Price Prediction</h1>
            <p style="color:#ccc; font-size:18px; margin-top:6px;">
                Enter car details and let AI estimate its resale value
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===== Load model & encoders =====
    try:
        model = joblib.load("GradientBoost_model.pkl")
        encoders = joblib.load("label_encoders.pkl")
    except Exception as e:
        st.error(f"❌ Failed to load model/encoders: {e}")
        return

    # ===== Load dataset =====
    try:
        df = pd.read_csv("car_dataset.csv")
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        st.error(f"❌ Could not load 'car_dataset.csv': {e}")
        return

    # ===== Hardcoded launch years =====
    launch_data = [
        ("Maruti","Ciaz",2014),("Maruti","Baleno",2015),("Maruti","Celerio",2014),
        ("Hyundai","i20",2008),("Honda","City",2003),("Tata","Nexon",2017),
        # ...(keep the rest of your list here as before)
    ]
    inferred_launch = {
        (b.strip().lower(), m.strip().lower()): int(y)
        for b, m, y in launch_data
        if b and m and y is not None
    }

    # ===== Input Form =====
    st.markdown(
        """
        <div style="
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        ">
        """,
        unsafe_allow_html=True,
    )

    # Brand & Model
    brands = sorted(df['brand'].dropna().unique())
    all_models = sorted(df['model'].dropna().unique())
    brand = st.selectbox("🚘 Select Brand", ["None"] + brands)
    models = sorted(df[df['brand'] == brand]['model'].dropna().unique()) if brand != "None" else all_models
    car_model = st.selectbox("🚗 Select Model", ["None"] + models)

    # Year
    MAX_YEAR = 2025
    years = [f"🚫 {MAX_YEAR} (Not Available)"] + list(range(MAX_YEAR-1, 1999, -1))
    manufacture_year = st.selectbox("📅 Car Manufactured Year", years, index=1)

    if isinstance(manufacture_year, str) and "🚫" in manufacture_year:
        st.warning("⚠️ Cars from 2025 are not available. Defaulting to 2024.")
        manufacture_year = 2024
    else:
        manufacture_year = int(manufacture_year)

    # Car age calculation
    current_year = MAX_YEAR
    vehicle_age = min(max(0, current_year - manufacture_year), 15)
    st.markdown(f"🧮 **Car Age:** `{vehicle_age}` years")

    # ===== Check launch year =====
    try:
        if brand != "None" and car_model != "None":
            key = (brand.strip().lower(), car_model.strip().lower())
            launch_year = inferred_launch.get(key, None)
            if launch_year is not None and manufacture_year < launch_year:
                st.error(f"⚠️ {brand} {car_model} was first manufactured in {launch_year}. You selected {manufacture_year}.")
    except Exception:
        pass

    # ===== Auto-fill Engine & Mileage from dataset =====
    default_engine = 1200
    default_mileage = 18.0
    if brand != "None" and car_model != "None":
        subset = df[(df['brand'].str.lower() == brand.lower()) & (df['model'].str.lower() == car_model.lower())]
        if not subset.empty:
            if "engine" in subset.columns:
                default_engine = int(subset['engine'].mean(skipna=True)) if not subset['engine'].isna().all() else default_engine
            if "mileage" in subset.columns:
                default_mileage = round(subset['mileage'].mean(skipna=True), 1) if not subset['mileage'].isna().all() else default_mileage

    # Fuel & Transmission
    fuel = st.selectbox("⛽ Fuel Type", ["Petrol","Diesel","CNG","Electric"])
    trans = st.selectbox("⚙️ Transmission", ["Manual","Automatic"])

    # Engine & Mileage (auto-filled but editable)
    engine = st.number_input("🧠 Engine (CC)", min_value=600, max_value=5000, value=default_engine, step=100)
    mileage = st.number_input("⛽ Mileage (kmpl)", min_value=5.0, max_value=40.0, value=default_mileage, step=0.5)

    # Kms & Seats
    km_driven = st.number_input("📏 Kilometers Driven", min_value=0.0, max_value=500000.0, value=30000.0, step=500.0)
    seats = st.number_input("🪑 Seats", min_value=2, max_value=10, value=5)

    submit = st.button("💰 Predict Price", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ========== PREDICTION ==========
    if submit:
        if "None" in [brand, car_model, fuel, trans]:
            st.warning("⚠️ Please select all required fields.")
            return
        try:
            X_input = [
                km_driven,
                encoders['transmission'].transform([trans])[0] if trans in encoders['transmission'].classes_ else -1,
                encoders['model'].transform([car_model])[0] if car_model in encoders['model'].classes_ else -1,
                vehicle_age,
                engine,
                mileage,
                encoders['fuel_type'].transform([fuel])[0] if fuel in encoders['fuel_type'].classes_ else -1,
                seats,
                encoders['brand'].transform([brand])[0] if brand in encoders['brand'].classes_ else -1
            ]

            log_price = model.predict([X_input])[0]

            if vehicle_age == 0: log_price += 0.02
            elif vehicle_age == 1: log_price += 0.01

            final_price = np.exp(log_price)
            lower_range = final_price * 0.95
            upper_range = final_price * 1.05

            # Predicted Price Card
            st.markdown(
                f"""
                <div style="
                    background: rgba(0,255,180,0.15);
                    backdrop-filter: blur(10px);
                    padding: 25px;
                    border-radius: 14px;
                    text-align: center;
                    margin-top: 25px;
                    box-shadow: 0 4px 14px rgba(0,0,0,0.4);
                ">
                    <h2 style="color:#00ffaa; margin:0;">💰 Predicted Price</h2>
                    <h1 style="color:white; font-size:46px; margin:10px 0;">₹ {final_price:,.0f}</h1>
                    <p style="color:#ccc; font-size:16px; margin:5px 0;">
                        📊 Market Range: <b>₹ {lower_range:,.0f} – ₹ {upper_range:,.0f}</b>
                    </p>
                    <p style="color:#aaa; font-size:13px; margin:0;">AI-powered estimate (Gradient Boosting)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Text Output
            st.write(
                f"📝 Based on current market trends, your **{brand} {car_model} ({manufacture_year})** "
                f"is expected to sell between **₹ {lower_range:,.0f} – ₹ {upper_range:,.0f}**."
            )

            # Car Summary
            img_html = ""
            model_filename = f"{brand.strip().lower()}_{car_model.strip().lower().replace(' ', '_')}"
            for ext in [".jpg", ".png", ".webp"]:
                path = f"car_images/{model_filename}{ext}"
                if os.path.exists(path):
                    img_html = f'<img src="data:image/{ext[1:]};base64,{base64.b64encode(open(path,"rb").read()).decode()}" style="max-width:250px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.5);"/>'
                    break

            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    gap:30px;
                    background: rgba(255,255,255,0.08);
                    backdrop-filter: blur(8px);
                    padding: 25px;
                    border-radius: 14px;
                    margin-top: 30px;
                ">
                    <div>{img_html}</div>
                    <div style="color:#ddd; font-size:16px;">
                        <h3 style="color:white; margin-top:0;">📋 Car Summary</h3>
                        🚘 <b>Brand:</b> {brand}<br>
                        🚗 <b>Model:</b> {car_model}<br>
                        📅 <b>Manufacture Year:</b> {manufacture_year}<br>
                        🧮 <b>Age:</b> {vehicle_age} years<br>
                        ⛽ <b>Fuel Type:</b> {fuel}<br>
                        ⚙️ <b>Transmission:</b> {trans}<br>
                        🧠 <b>Engine:</b> {engine} CC<br>
                        ⛽ <b>Mileage:</b> {mileage} kmpl<br>
                        📏 <b>Kilometers Driven:</b> {km_driven:,.0f} km<br>
                        🪑 <b>Seats:</b> {seats}<br>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")


if __name__ == "__main__":
    app()
