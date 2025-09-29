import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import numpy as np

def app():
    # ===== Hero Header =====
    st.markdown(
        """
        <div style="text-align:center; padding:25px; margin-bottom:20px;
                    background:rgba(255,255,255,0.08); backdrop-filter:blur(10px);
                    border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.4);">
            <h2 style="margin:0; font-size:36px;
                       background:linear-gradient(90deg,#00ffae,#3a7bd5,#00d2ff,#ff007f);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                📊 Data Analysis
            </h2>
            <p style="color:#ccc; margin:5px 0 0 0;">
                Exploring non-price attributes of used cars
            </p>
        </div>
        """, unsafe_allow_html=True
    )

    # ===== Load Data =====
    @st.cache_data
    def load_data():
        file_path = os.path.join(os.path.dirname(__file__), "car_dataset.csv")
        if not os.path.exists(file_path):
            st.error(f"❌ File not found: {file_path}")
            st.stop()

        df = pd.read_csv(file_path)
        df = df.loc[:, ~df.columns.str.contains("unnamed", case=False)]  # drop Unnamed cols
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.title()

        # Manufactured_By & Car_Model columns
        if "Name" in df.columns:
            df["Manufactured_By"] = df["Name"].str.split().str[0]
            df["Car_Model"] = df["Name"].str.split().str[1:].str.join(" ")
        elif "Brand" in df.columns:
            df["Manufactured_By"] = df["Brand"]
            if "Model" in df.columns:
                df["Car_Model"] = df["Model"]
        else:
            df["Manufactured_By"] = "Unknown"
            df["Car_Model"] = "Unknown"
        return df

    df = load_data()

    # ===== Column Glossary =====
    st.markdown("### 📋 Available Columns")

    column_info = {
        "Car_Name": "Full name of the car",
        "Brand": "Manufacturer brand",
        "Model": "Model name",
        "Vehicle_Age": "Car age in years",
        "Km_Driven": "Total kilometers driven",
        "Fuel_Type": "Type of fuel used",
        "Transmission": "Transmission type",
        "Mileage": "Fuel efficiency (kmpl)",
        "Engine": "Engine capacity (CC)",
        "Max_Power": "Maximum power (bhp)",
        "Seats": "Number of seats",
        "Selling_Price": "Resale price",
        "Manufactured_By": "Extracted brand",
        "Car_Model": "Extracted model"
    }

    cols = st.columns(3)
    i = 0
    for col, desc in column_info.items():
        if col in df.columns:
            with cols[i % 3]:
                st.markdown(
                    f"""
                    <div style="background:rgba(255,255,255,0.05);
                                border-radius:10px; padding:12px; margin:8px;
                                box-shadow:0 2px 6px rgba(0,0,0,0.3);">
                        <b style="color:#4CAF50;">{col}</b><br>
                        <span style="color:#bbb; font-size:90%;">{desc}</span>
                    </div>
                    """, unsafe_allow_html=True
                )
            i += 1

    # ===== Quick Stats (Better KPI Boxes) =====
    st.markdown("### 📊 Quick Stats")

    if not df.empty:
        stats = []
        stats.append({"label": "🚘 Cars", "value": f"{len(df):,}"})

        if "Km_Driven" in df.columns:
            stats.append({"label": "🛣️ Avg Km Driven", "value": f"{df['Km_Driven'].mean():,.0f} km"})

        if "Mileage" in df.columns:
            df["Mileage_Num"] = pd.to_numeric(df["Mileage"].astype(str).str.extract(r"(\d+\.?\d*)")[0], errors="coerce")
            stats.append({"label": "🌱 Avg Mileage", "value": f"{df['Mileage_Num'].mean():.1f} kmpl"})

        if "Engine" in df.columns:
            df["Engine_Num"] = pd.to_numeric(df["Engine"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
            stats.append({"label": "⚙️ Avg Engine", "value": f"{df['Engine_Num'].mean():,.0f} CC"})

        cols = st.columns(len(stats))
        for i, stat in enumerate(stats):
            cols[i].markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(2,0,36,0.4));
                    border-radius: 14px;
                    padding: 20px;
                    margin: 10px;
                    text-align: center;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                ">
                    <h3 style="margin:0; color:#00ffaa;">{stat['label']}</h3>
                    <p style="margin:5px 0 0 0; font-size:22px; font-weight:bold; color:white;">
                        {stat['value']}
                    </p>
                </div>
                """, unsafe_allow_html=True
            )

    # ===== Fuel Type Distribution =====
    if "Fuel_Type" in df.columns:
        st.markdown("## ⛽ Fuel Type Distribution")
        fuel_counts = df["Fuel_Type"].value_counts().reset_index()
        fuel_counts.columns = ["Fuel Type", "Count"]
        fig = px.pie(fuel_counts, values="Count", names="Fuel Type",
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ===== Transmission =====
    if "Transmission" in df.columns:
        st.markdown("## ⚙️ Transmission Type")
        trans_counts = df["Transmission"].value_counts().reset_index()
        trans_counts.columns = ["Transmission", "Count"]
        fig = px.bar(trans_counts, x="Transmission", y="Count", color="Transmission", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ===== Car Year Distribution =====
    if "Year" in df.columns:
        st.markdown("## 📅 Car Year Distribution")
        year_counts = df["Year"].value_counts().sort_index().reset_index()
        year_counts.columns = ["Year", "Count"]
        fig = px.bar(year_counts, x="Year", y="Count", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ===== Mileage vs Engine =====
    if "Mileage_Num" in df.columns and "Engine_Num" in df.columns:
        st.markdown("## 📈 Mileage vs Engine")
        plot_df = df.dropna(subset=["Mileage_Num", "Engine_Num"])
        fig = px.scatter(plot_df, x="Engine_Num", y="Mileage_Num",
                         color="Manufactured_By",
                         hover_data=["Car_Model"] if "Car_Model" in df else None,
                         template="plotly_dark")
        # Add trendline
        try:
            m, b = np.polyfit(plot_df["Engine_Num"], plot_df["Mileage_Num"], 1)
            fig.add_trace(go.Scatter(x=plot_df["Engine_Num"], y=m*plot_df["Engine_Num"]+b,
                                     mode="lines", line=dict(color="red"), name="Trendline"))
        except Exception:
            pass
        fig.update_layout(xaxis_title="Engine (CC)", yaxis_title="Mileage (kmpl)")
        st.plotly_chart(fig, use_container_width=True)

    # ===== Brand Frequency =====
    if "Manufactured_By" in df.columns:
        st.markdown("## 🏷️ Brand Frequency")
        brand_counts = df["Manufactured_By"].value_counts().reset_index()
        brand_counts.columns = ["Brand", "Count"]
        fig = px.bar(brand_counts.head(20), x="Brand", y="Count", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Logos for top brands
        st.markdown("### 🔝 Top Brand Logos")
        cols = st.columns(5)
        for i, b in enumerate(brand_counts["Brand"].head(10)):
            logo_path = f"car_logos/{b.lower()}.png"
            with cols[i % 5]:
                if os.path.exists(logo_path):
                    st.image(logo_path, width=80)
                st.markdown(f"**{b}**")

    # ===== Top Models + Images =====
    if "Car_Model" in df.columns:
        st.markdown("## 🚗 Top 20 Car Models")
        model_counts = df["Car_Model"].value_counts().head(20).reset_index()
        model_counts.columns = ["Model", "Count"]
        fig = px.bar(model_counts, x="Model", y="Count", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Top 5 Model Images
        st.markdown("### 🖼️ Top 5 Popular Models")
        top5_models = model_counts.head(5)

        cols = st.columns(min(len(top5_models), 5))
        for idx, row in enumerate(top5_models.itertuples()):
            model = row.Model
            count = row.Count
            brand = df[df["Car_Model"] == model]["Manufactured_By"].mode()[0] if "Manufactured_By" in df.columns else ""

            model_filename = f"{brand.strip().lower()}_{model.strip().lower().replace(' ', '_')}" if brand else model.strip().lower().replace(" ", "_")
            img_path = None
            for ext in [".jpg", ".png", ".webp"]:
                path = f"car_images/{model_filename}{ext}"
                if os.path.exists(path):
                    img_path = path
                    break

            with cols[idx % len(cols)]:
                if img_path:
                    st.image(img_path, use_container_width=True)
                st.markdown(
                    f"""
                    <div style="text-align:center; margin-top:5px;">
                        <b style="color:white;">{brand} {model}</b><br>
                        <span style="color:#00ffaa;">Listings: {count}</span>
                    </div>
                    """, unsafe_allow_html=True
                )

    # ===== Top Selling Cars (Image Gallery) =====
    if "Selling_Price" in df.columns and "Car_Model" in df.columns:
        st.markdown("## 🏆 Top 5 High Value Cars")

        top_selling = (df.groupby(["Manufactured_By", "Car_Model"])["Selling_Price"]
                       .mean().reset_index()
                       .sort_values(by="Selling_Price", ascending=False)
                       .head(5))

        cols = st.columns(min(len(top_selling), 5))
        for idx, row in enumerate(top_selling.itertuples()):
            brand = row.Manufactured_By
            model = row.Car_Model
            price = row.Selling_Price

            model_filename = f"{brand.strip().lower()}_{model.strip().lower().replace(' ', '_')}"
            img_path = None
            for ext in [".jpg", ".png", ".webp"]:
                path = f"car_images/{model_filename}{ext}"
                if os.path.exists(path):
                    img_path = path
                    break

            with cols[idx % len(cols)]:
                if img_path:
                    st.image(img_path, use_container_width=True)
                st.markdown(
                    f"""
                    <div style="text-align:center; margin-top:5px;">
                        <b style="color:white;">{brand} {model}</b><br>
                        <span style="color:#00ffaa;">₹ {price:,.0f}</span>
                    </div>
                    """, unsafe_allow_html=True
                )
