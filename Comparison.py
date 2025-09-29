import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os, base64

def app():
    # ===== Hero Header =====
    st.markdown(
        """
        <div style="text-align:center; padding:20px; margin-bottom:20px;
                    background:rgba(255,255,255,0.08); backdrop-filter:blur(10px);
                    border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.4);">
            <h2 style="margin:0; color:white;">📊 Car Comparison Dashboard</h2>
            <p style="color:#ccc; margin:5px 0 0 0;">
                Compare car specs and prices across different models with interactive charts
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    # ===== Load Data =====
    @st.cache_data
    def load_data():
        df = pd.read_csv("car_dataset.csv")
        df.columns = df.columns.str.strip().str.lower()
        numeric_cols = ['vehicle_age','km_driven','mileage','engine','max_power','seats','selling_price']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df.dropna(subset=['brand','model'])

    df = load_data()
    if df.empty:
        st.error("❌ Dataset not loaded or empty")
        return

    # ===== Filters Section =====
    st.markdown(
        """
        <div style="background:rgba(255,255,255,0.05); backdrop-filter:blur(6px);
                    padding:15px; border-radius:12px; margin-bottom:20px;">
            <h4 style="color:white; margin-top:0;">🔎 Filter Cars Before Comparison</h4>
        </div>
        """, unsafe_allow_html=True
    )
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        fuel_filter = st.multiselect("Fuel Type", sorted(df['fuel_type'].dropna().unique()), default=df['fuel_type'].unique())
    with col_filter2:
        trans_filter = st.multiselect("Transmission", sorted(df['transmission'].dropna().unique()), default=df['transmission'].unique())
    with col_filter3:
        year_filter = st.slider("Manufactured Year", int(df['vehicle_age'].max()*-1 + 2025), 2024, (2000, 2024))

    # Apply filters
    filtered_df = df[
        (df['fuel_type'].isin(fuel_filter)) &
        (df['transmission'].isin(trans_filter)) &
        ((2025 - df['vehicle_age']).between(year_filter[0], year_filter[1]))
    ]
    if filtered_df.empty:
        st.warning("⚠️ No cars match the selected filters")
        return

    # ===== Select Models to Compare =====
    st.markdown("## 🚗 Select Models to Compare")
    brands = sorted(filtered_df['brand'].unique())
    col1, col2, col3 = st.columns(3)
    with col1:
        brand1 = st.selectbox("Brand 1", brands)
        model1 = st.selectbox("Model 1", sorted(filtered_df[filtered_df['brand']==brand1]['model'].unique()))
    with col2:
        brand2 = st.selectbox("Brand 2", brands, index=min(1,len(brands)-1))
        model2 = st.selectbox("Model 2", sorted(filtered_df[filtered_df['brand']==brand2]['model'].unique()))
    with col3:
        brand3 = st.selectbox("Brand 3 (Optional)", ["None"] + brands)
        if brand3 != "None":
            model3 = st.selectbox("Model 3", ["None"] + sorted(filtered_df[filtered_df['brand']==brand3]['model'].unique()))
        else:
            model3 = None

    compare_btn = st.button("🔍 Compare Models", type="primary")

    # ===== Comparison Section =====
    if compare_btn:
        models_to_compare = []
        for brand, model in [(brand1, model1), (brand2, model2)]:
            data = filtered_df[(filtered_df['brand']==brand) & (filtered_df['model']==model)]
            if not data.empty:
                models_to_compare.append((brand, model, data))
        if model3 and model3 != "None":
            data = filtered_df[(filtered_df['brand']==brand3) & (filtered_df['model']==model3)]
            if not data.empty:
                models_to_compare.append((brand3, model3, data))

        if not models_to_compare:
            st.warning("⚠️ No data available for selected models")
            return

        # ===== Show Logos & Images for Each Model =====
        st.markdown("### 🖼️ Selected Cars")
        cols = st.columns(len(models_to_compare))
        for idx, (brand, model, data) in enumerate(models_to_compare):
            logo_path = f"car_logos/{brand.lower()}.png"
            car_img = ""
            model_filename = f"{brand.strip().lower()}_{model.strip().lower().replace(' ', '_')}"
            for ext in [".jpg", ".png", ".webp"]:
                img_path = f"car_images/{model_filename}{ext}"
                if os.path.exists(img_path):
                    car_img = f'<img src="data:image/{ext[1:]};base64,{base64.b64encode(open(img_path,"rb").read()).decode()}" style="max-width:200px; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.5);"/>'
                    break
            with cols[idx]:
                if os.path.exists(logo_path):
                    st.image(logo_path, width=80)
                st.markdown(f"### {brand} {model}")
                if car_img:
                    st.markdown(car_img, unsafe_allow_html=True)

        # ===== Specs Comparison (Grouped Bar Chart + Heatmap) =====
        st.markdown("### 📊 Specs Comparison (Engine, Mileage, Seats, Age)")
        spec_features = ['engine', 'mileage', 'seats', 'vehicle_age']
        labels = ["Engine (CC)", "Mileage (kmpl)", "Seats", "Age (yrs)"]

        # --- Build grouped bar chart data ---
        spec_data = []
        for brand, model, data in models_to_compare:
            avg_values = [data[f].mean() for f in spec_features]
            for l, v in zip(labels, avg_values):
                spec_data.append({"Model": f"{brand} {model}", "Spec": l, "Value": v})
        spec_df = pd.DataFrame(spec_data)

        # --- Grouped Bar Chart ---
        bar_fig = px.bar(
            spec_df,
            x="Spec",
            y="Value",
            color="Model",
            barmode="group",
            text="Value",
            title="📊 Specs Comparison (Grouped Bar Chart)"
        )
        bar_fig.update_layout(template="plotly_dark", yaxis_title="Value")
        st.plotly_chart(bar_fig, use_container_width=True)

        # --- Heatmap Style Comparison Table ---
        st.markdown("### 🔥 Specs Heatmap Table")
        heatmap_df = pd.DataFrame({
            f"{brand} {model}": [
                round(data['engine'].mean(),1),
                round(data['mileage'].mean(),1),
                round(data['seats'].mean(),1),
                round(data['vehicle_age'].mean(),1)
            ]
            for brand, model, data in models_to_compare
        }, index=labels)

        def color_scale(val, col_name):
            """Green for higher is better, red for lower (except Age, where lower is better)."""
            if pd.isna(val): 
                return "color:white;"
            col_values = heatmap_df[col_name]
            if col_name == "Age (yrs)":  # lower age is better
                if val <= col_values.min(): return "background-color: rgba(0,255,0,0.4);"
                elif val >= col_values.max(): return "background-color: rgba(255,0,0,0.4);"
            else:  # higher is better
                if val >= col_values.max(): return "background-color: rgba(0,255,0,0.4);"
                elif val <= col_values.min(): return "background-color: rgba(255,0,0,0.4);"
            return "background-color: rgba(255,255,255,0.05);"

        styled_df = heatmap_df.style.apply(
            lambda col: [color_scale(v, col.name) for v in col], axis=0
        ).set_properties(**{'color':'white'})

        st.dataframe(styled_df, use_container_width=True)

        # ===== Price Distribution =====
        st.markdown("### 💰 Price Distribution")
        box_fig = go.Figure()
        for brand, model, data in models_to_compare:
            box_fig.add_trace(go.Box(
                y=data['selling_price'],
                name=f"{brand} {model}"
            ))
        box_fig.update_layout(yaxis_title="Price (₹)", template="plotly_dark")
        st.plotly_chart(box_fig, use_container_width=True)

        # ===== Detailed Comparison Table =====
        st.markdown("### 📋 Detailed Comparison Table")
        table_data = []
        for brand, model, data in models_to_compare:
            avg_price = data['selling_price'].mean()
            min_price = data['selling_price'].min()
            max_price = data['selling_price'].max()
            price_per_km = (avg_price / data['km_driven'].mean()) if data['km_driven'].mean() else np.nan
            depreciation = 100*(1 - (avg_price / max_price)) if max_price else 0
            table_data.append({
                "Model": f"{brand} {model}",
                "Avg Price (₹)": round(avg_price, 2),
                "Min Price (₹)": round(min_price, 2),
                "Max Price (₹)": round(max_price, 2),
                "Price per km (₹)": round(price_per_km, 4) if not np.isnan(price_per_km) else "N/A",
                "Depreciation %": round(depreciation, 2),
                "Avg Mileage (kmpl)": round(data['mileage'].mean(), 2),
                "Avg Engine (cc)": round(data['engine'].mean(), 2),
                "Avg Seats": round(data['seats'].mean(), 1),
                "Avg Age (yrs)": round(data['vehicle_age'].mean(), 1)
            })
        st.dataframe(pd.DataFrame(table_data).set_index("Model"), use_container_width=True)

        # ===== Scatter: Price vs Mileage =====
        st.markdown("### 🚀 Price vs Mileage")
        scatter_fig = go.Figure()
        colors = px.colors.qualitative.Plotly
        for i, (brand, model, data) in enumerate(models_to_compare):
            scatter_fig.add_trace(go.Scatter(
                x=data['mileage'],
                y=data['selling_price'],
                mode='markers',
                name=f"{brand} {model}",
                marker=dict(color=colors[i%len(colors)], size=10, line=dict(width=1, color='DarkSlateGrey'))
            ))
        scatter_fig.update_layout(
            xaxis_title="Mileage (kmpl)",
            yaxis_title="Selling Price (₹)",
            template="plotly_dark"
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

        # ===== Insights Section =====
        st.markdown(
            """
            <div style="background:rgba(0,255,180,0.1); backdrop-filter:blur(8px);
                        padding:20px; border-radius:12px; margin-top:25px;">
                <h4 style="color:#00ffaa; margin-top:0;">📈 Insights</h4>
                <ul style="color:#ddd;">
                    <li>🚙 SUVs in Diesel usually retain higher resale value.</li>
                    <li>⚡ Automatic cars tend to depreciate faster than Manual.</li>
                    <li>📅 Older cars (>10 yrs) show sharp price drops.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )
