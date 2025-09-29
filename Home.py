import streamlit as st
import base64
from pathlib import Path
import time
import itertools

def app():
    # === Load background image ===
    img_path = "assets/263800.jpg"
    encoded = base64.b64encode(Path(img_path).read_bytes()).decode()

    # === Custom CSS ===
    st.markdown(
        f"""
        <style>
        /* Background with overlay */
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,40,0.8)), 
                        url("data:image/jpg;base64,{encoded}") center/cover no-repeat;
            z-index: -1;
        }}

        /* Glassmorphic Hero */
        .hero {{
            text-align: center;
            margin-top: 70px;
            padding: 40px;
            border-radius: 20px;
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(12px);
            display: inline-block;
            box-shadow: 0 0 40px rgba(0,191,255,0.4);
            animation: fadeIn 2s ease-in-out;
        }}
        .hero h1 {{
            font-size: 70px;
            font-weight: 900;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5, #00ffae, #ff007f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 3s infinite alternate;
            margin-bottom: 15px;
        }}
        .hero h3 {{
            font-size: 26px;
            color: #f0f0f0;
            margin-bottom: 0;
        }}
        @keyframes glow {{
            from {{ text-shadow: 0 0 20px #00d2ff; }}
            to   {{ text-shadow: 0 0 35px #ff00ff; }}
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Stats Section */
        .stats-container {{
            display: flex; justify-content: center; gap: 30px;
            margin: 60px auto; flex-wrap: wrap;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.07);
            backdrop-filter: blur(10px);
            border-radius: 18px;
            padding: 30px;
            text-align: center; color: white;
            width: 220px;
            box-shadow: 0 0 25px rgba(0,191,255,0.3);
            transition: all 0.4s ease-in-out;
        }}
        .stat-card:hover {{
            transform: scale(1.08);
            box-shadow: 0 0 40px rgba(255, 0, 200, 0.7);
        }}
        .stat-num {{
            font-size: 40px; font-weight: 900;
        }}
        .stat-desc {{
            font-size: 16px; font-weight: 600;
        }}

        /* CTA Tiles */
        .cta-container {{
            display: flex; justify-content: center;
            gap: 25px; margin: 60px auto; flex-wrap: wrap;
        }}
        .cta-card {{
            flex: 1; min-width: 250px; max-width: 320px;
            background: linear-gradient(135deg, rgba(0,191,255,0.25), rgba(255,0,180,0.25));
            border-radius: 20px;
            padding: 40px; text-align: center;
            color: white; font-size: 24px; font-weight: 700;
            cursor: pointer;
            transition: transform 0.3s ease-in-out;
            box-shadow: 0 0 20px rgba(0,255,255,0.4);
        }}
        .cta-card:hover {{
            transform: translateY(-12px) rotateX(5deg) rotateY(-5deg);
            box-shadow: 0 0 50px rgba(0,255,180,0.9);
        }}

        /* Footer */
        .footer {{
            text-align: center;
            margin-top: 80px;
            padding: 20px;
            font-size: 16px;
            color: #7afcff;
            border-top: 2px solid rgba(0,191,255,0.4);
            text-shadow: 0px 0px 12px rgba(0,255,255,0.9);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # === Hero Section ===
    st.markdown(
        """
        <div class="hero">
            <h1>🚗 Used Car Price Prediction </h1>
            <h3>Smarter • Faster • Sleeker Car Insights</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # === Stats with Animated Counters ===
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    cols = st.columns(4)
    stats = [("📊", 15000, "Car Records"),
             ("🚘", 30, "Brands"),
             ("⚡", 6, "Fuel Types"),
             ("🏷️", 200, "Models")]
    for col, (icon, num, desc) in zip(cols, stats):
        with col:
            # animated counter
            placeholder = st.empty()
            for i in range(0, num+1, max(1, num//20)):
                placeholder.markdown(
                    f"""
                    <div class="stat-card">
                        <div style="font-size:45px">{icon}</div>
                        <div class="stat-num">{i}+</div>
                        <div class="stat-desc">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                time.sleep(0.02)
    st.markdown('</div>', unsafe_allow_html=True)
         # === About the Project ===
    st.markdown(
        """
        <div style="margin-top:50px; padding:40px; border-radius:18px;
                    background:rgba(255,255,255,0.08); backdrop-filter:blur(12px);
                    box-shadow:0 0 25px rgba(0,255,180,0.35); text-align:center;">
            <h2 style="color:#00ffaa; font-size:32px; margin-bottom:20px;">📖 About the Project</h2>
            <p style="color:#ddd; font-size:20px; line-height:1.8; text-align:justify;">
                The <b>CarDekho Resale Price Predictor</b> is a smart application that helps users 
                estimate the <b>resale value</b> of used cars using <b>Machine Learning</b>.  
                <br><br>
                Powered by a <b>Gradient Boosting Model</b> trained on thousands of real car listings, 
                it predicts realistic prices based on key factors such as brand, model, year, 
                kilometers driven, mileage, fuel type, transmission, and seating capacity.
            </p>
            <br>
            <h3 style="color:#00ffaa; font-size:26px; margin-top:10px;">🌟 What You Can Do</h3>
            <ul style="text-align:left; color:#eee; font-size:18px; line-height:1.8; max-width:800px; margin:auto;">
                <li>📊 <b>Data Analysis</b> – Explore fuel type distribution, brand popularity, and mileage trends.</li>
                <li>🚘 <b>Car Filtering</b> – Find cars that match your exact preferences with smart filters.</li>
                <li>⚡ <b>Comparison Dashboard</b> – Compare multiple models side by side with interactive charts.</li>
                <li>💰 <b>Price Prediction</b> – Instantly get estimated resale value for any car.</li>
            </ul>
            <br>
            <p style="color:#ccc; font-size:19px;">
                ✅ Whether you're a <b>buyer</b>, <b>seller</b>, or <b>analyst</b>, this tool helps you make 
                smarter and data-driven decisions in the used car market.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )



    # === CTA Tiles ===
    st.markdown('<div class="cta-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💰 Price Prediction", use_container_width=True):
            st.session_state["go_to"] = "💰 Price Prediction"
            st.rerun()
    with col2:
        if st.button("📊 Data Analysis", use_container_width=True):
            st.session_state["go_to"] = "📊 Data Analysis"
            st.rerun()
    with col3:
        if st.button("📉 Compare Prices", use_container_width=True):
            st.session_state["go_to"] = "📉 Price Comparison"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # === Footer ===
    st.markdown('<div class="footer">© 2025 • Built with 🚀 by Shreyas</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app()
