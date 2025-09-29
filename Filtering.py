import streamlit as st
import pandas as pd
import os
import plotly.express as px

def app():
    @st.cache_data
    def load_data():
        df = pd.read_csv("car_dataset.csv")
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        df.drop(columns=[col for col in df.columns if col.lower().startswith("unnamed")], inplace=True, errors="ignore")
        df.columns = df.columns.str.strip().str.lower()
        return df

    df = load_data()

    # ===== Hero Header =====
    st.markdown(
        """
        <div style="text-align:center; padding:25px; margin-bottom:20px;
                    background:rgba(255,255,255,0.08); backdrop-filter:blur(10px);
                    border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.4);">
            <h2 style="margin:0; font-size:36px;
                       background:linear-gradient(90deg,#00d2ff,#3a7bd5,#00ffae,#ff007f);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🎛️ Car Filter Explorer
            </h2>
            <p style="color:#ccc; margin:5px 0 0 0;">
                Explore cars by brand, model, fuel, transmission, and year range
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    # ===== Filters =====
    with st.expander("🔎 Filter Options", expanded=True):
        # Brand filter
        selected_brands = st.multiselect("1️⃣ Select Car Name (Brand)", sorted(df["brand"].dropna().unique()))

        # Model filter (dependent on brand)
        if selected_brands:
            available_models = sorted(df[df["brand"].isin(selected_brands)]["model"].dropna().unique())
            selected_models = st.multiselect("2️⃣ Select Car Model", available_models)
        else:
            st.info("ℹ️ Please select at least one brand to view models.")
            selected_models = []

        # Fuel filter
        fuel = st.multiselect("3️⃣ Select Fuel Type", sorted(df["fuel_type"].dropna().unique())) if "fuel_type" in df else []

        # Transmission filter
        transmission = st.multiselect("4️⃣ Select Transmission", sorted(df["transmission"].dropna().unique())) if "transmission" in df else []

        # Year filter
        if "year" in df.columns:
            min_year = int(df["year"].min())
            max_year = int(df["year"].max())
            year_range = st.slider("5️⃣ Select Year Range", min_year, max_year, (min_year, max_year))
        else:
            year_range = None

    # ===== Apply Filters =====
    filtered_df = df.copy()
    if selected_brands:
        filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]
    if selected_models:
        filtered_df = filtered_df[filtered_df["model"].isin(selected_models)]
    if fuel:
        filtered_df = filtered_df[filtered_df["fuel_type"].isin(fuel)]
    if transmission:
        filtered_df = filtered_df[filtered_df["transmission"].isin(transmission)]
    if year_range and "year" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])
        ]
    filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated(keep='first')]

    # ===== Show Logos for Brands =====
    if selected_brands:
        st.markdown("### 🏷️ Selected Brands")
        cols = st.columns(len(selected_brands))
        for i, b in enumerate(selected_brands):
            logo_path = f"car_logos/{b.lower()}.png"
            if os.path.exists(logo_path):
                cols[i].image(logo_path, width=80)
            cols[i].markdown(f"**{b}**")

    # ===== Show Images for Models =====
    if selected_models:
        st.markdown("### 🖼️ Selected Models")
        cols = st.columns(len(selected_models))
        for i, m in enumerate(selected_models):
            model_filename = f"{selected_brands[0].lower()}_{m.lower().replace(' ', '_')}"
            for ext in [".jpg", ".png", ".webp"]:
                path = f"car_images/{model_filename}{ext}"
                if os.path.exists(path):
                    cols[i].image(path, width=180, caption=m)
                    break

    # ===== Summary Stats =====
    if not filtered_df.empty:
        avg_price = filtered_df["selling_price"].mean() if "selling_price" in filtered_df else None
        avg_mileage = filtered_df["mileage"].mean() if "mileage" in filtered_df else None

        st.markdown("### 📊 Summary Stats")
        colA, colB, colC = st.columns(3)
        colA.metric("🚘 Cars Found", len(filtered_df))
        if avg_price: colB.metric("💰 Avg Price", f"₹ {avg_price:,.0f}")
        if avg_mileage: colC.metric("🌱 Avg Mileage", f"{avg_mileage:.1f} kmpl")

    # ===== Results Table =====
    st.markdown("### 📋 Filtered Car Results")
    st.write(f"🔢 Total Matching Records: `{len(filtered_df)}`")

    if not filtered_df.empty:
        styled = filtered_df.style.set_properties(**{
            "background-color":"rgba(255,255,255,0.03)",
            "color":"white"
        })
        st.dataframe(styled, use_container_width=True, height=800)

    # ===== Visualization =====
    if not filtered_df.empty and "selling_price" in filtered_df and "year" in filtered_df:
        st.markdown("### 📈 Price vs Year")
        fig = px.scatter(
            filtered_df,
            x="year",
            y="selling_price",
            color="brand",
            hover_data=["model", "fuel_type", "transmission"]
        )
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
