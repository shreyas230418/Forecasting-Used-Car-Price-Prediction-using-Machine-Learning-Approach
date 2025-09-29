import streamlit as st
import base64
import Home, Filtering, Analysis, Prediction, Comparison

# ===== Page Config =====
st.set_page_config(page_title="CarDekho Resale Price Predictor", layout="wide")

# ===== Function to set background and sidebar styling =====
def set_bg_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()

    css = f"""
    <style>
    /* ===== Main Background ===== */
    .stApp {{
        background: url("data:image/jpg;base64,{encoded}") no-repeat center center fixed;
        background-size: cover;
    }}

    /* Dark overlay behind content */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: -1;
    }}

    /* ===== Sidebar Clean Glass Style ===== */
    [data-testid="stSidebar"] {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid rgba(255,255,255,0.1);
        padding-top: 10px;
    }}

    /* Sidebar Title */
    [data-testid="stSidebar"] .sidebar-title {{
        font-size: 22px;
        font-weight: 700;
        text-align: center;
        padding: 12px;
        margin-bottom: 15px;
        color: #f2f2f2;
        border-bottom: 1px solid rgba(255,255,255,0.15);
    }}

    /* Sidebar Menu Items */
    div[role="radiogroup"] > label {{
        width: 100%;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 8px;
        background: rgba(255,255,255,0.05);
        font-size: 18px;
        font-weight: 500;
        color: #ffffff !important;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
    }}
    div[role="radiogroup"] > label:hover {{
        background: rgba(255,255,255,0.15);
    }}
    div[role="radiogroup"] > label[data-selected="true"] {{
        background: rgba(255,255,255,0.25);
        font-weight: 600 !important;
        border-left: 4px solid #ffffff;
    }}

    /* Remove white box in main content */
    .main .block-container {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ===== Apply background =====
set_bg_image("assets/263800.jpg")

# ===== Sidebar Branding =====
st.sidebar.markdown(
    """
    <div style="text-align:center; font-size:22px; font-weight:700; margin-bottom:15px;">
        🚗 DASHBOARD
    </div>
    """,
    unsafe_allow_html=True
)

# ===== Sidebar Menu =====
menu = st.sidebar.radio(
    "",
    ["🏠 Home", "🔍 Data Filtering", "📊 Data Analysis", "💰 Price Prediction", "📉 Price Comparison"],
    key="menu",
)

# ===== Handle redirection from Home buttons =====
if "go_to" in st.session_state:
    menu = st.session_state["go_to"]
    del st.session_state["go_to"]

# ===== Page Loader =====
if menu == "🏠 Home":
    Home.app()
elif menu == "🔍 Data Filtering":
    Filtering.app()
elif menu == "📊 Data Analysis":
    Analysis.app()
elif menu == "💰 Price Prediction":
    Prediction.app()
elif menu == "📉 Price Comparison":
    Comparison.app()

# ===== Sidebar Footer =====
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="font-size:14px; text-align:center; color:#cccccc;">
        ⚡ Powered by Gradient Boosting <br>
        📅 Updated: 2025
    </div>
    """,
    unsafe_allow_html=True
)
