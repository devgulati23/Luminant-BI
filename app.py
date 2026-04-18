import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests
import re
import tempfile
import time  # For the cookie race-condition fix
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from streamlit_cookies_manager import EncryptedCookieManager

# ---------- CONFIG ----------
st.set_page_config(page_title="Luminant BI Analytics Tool", layout="wide")

API_KEY = "AIzaSyA_Rcb6UVBQSqqH_9jBSXeEkbZUn3jnT3k"

# ---------- COOKIE SETUP ("Remember Me") ----------
cookies = EncryptedCookieManager(
    prefix="luminantbi_",
    password="super-secret-bca-project-password" 
)
if not cookies.ready():
    st.stop()

if "user" not in st.session_state:
    st.session_state.user = None

# Auto-Login Logic
if st.session_state.user is None and cookies.get("saved_email"):
    st.session_state.user = {
        "email": cookies["saved_email"], 
        "username": cookies["saved_email"].split('@')[0]
    }

# ---------- STYLE ----------
st.markdown("""
<style>
/* Global Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;500;600;700&display=swap');

/* Base Overrides */
.stApp {
    font-family: 'Inter', sans-serif;
}

/* Dashboard Cards */
.metric-card {
    background: white;
    color: black;
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    font-weight: 600;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.eda-section {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    border: 1px solid #edf2f7;
}

/* Insight cards */
.insight-card {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 16px;
    border: 1px solid;
    transition: all 0.2s ease;
}
.insight-card:hover { transform: translateX(6px); }
.insight-card.strong { background: #f0fdf4; border-color: #86efac; }
.insight-card.moderate { background: #fffbeb; border-color: #fcd34d; }
.insight-card.none { background: #fff5f5; border-color: #feb2b2; }

.insight-badge {
    flex-shrink: 0;
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
}
.insight-badge.strong  { background: #dcfce7; }
.insight-badge.moderate { background: #fef9c3; }
.insight-badge.none    { background: #fee2e2; }

.insight-body { flex: 1; }
.insight-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 4px;
}
.insight-label.strong  { color: #16a34a; }
.insight-label.moderate { color: #d97706; }
.insight-label.none    { color: #dc2626; }

.insight-text {
    font-size: 1rem;
    font-weight: 600;
    color: #1a202c;
}
.insight-subtext {
    font-size: 0.85rem;
    color: #718096;
    margin-top: 4px;
}
.insight-score {
    flex-shrink: 0;
    font-size: 1.5rem;
    font-weight: 800;
    align-self: center;
}
.insight-score.strong  { color: #16a34a; }
.insight-score.moderate { color: #d97706; }
.insight-score.none    { color: #dc2626; }

.insight-summary {
    display: flex;
    gap: 12px;
    margin: 20px 0 32px 0;
    flex-wrap: wrap;
}
.insight-summary-pill {
    padding: 10px 20px;
    border-radius: 30px;
    font-size: 0.9rem;
    font-weight: 600;
.insight-summary-pill.strong  { background: #dcfce7; color: #16a34a; }
.insight-summary-pill.moderate { background: #fef9c3; color: #d97706; }
.insight-summary-pill.none    { background: #fee2e2; color: #dc2626; }

/* Filter Buttons Styling */
div[data-testid="stColumn"] .stButton > button {
    border-radius: 30px !important;
    padding: 8px 16px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    border: 1px solid #e2e8f0 !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stColumn"] .stButton > button:hover {
    border-color: #dc2626 !important;
    background: #fff5f5 !important;
    transform: scale(1.05);
}

/* LOGIN UI SPECIFIC STYLES */
.login-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: #000000;
    z-index: -1;
}

.login-card-container {
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 5vh;
}

.login-card {
    background: #0a0a0a;
    border-radius: 12px;
    border: 2px solid #dc2626;
    padding: 40px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 10px 30px rgba(220, 38, 38, 0.2);
    animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.login-header {
    text-align: center;
    margin-bottom: 25px;
}

.login-header h1 {
    font-family: 'Outfit', sans-serif !important;
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    text-transform: uppercase;
    letter-spacing: -1px;
    margin: 0 !important;
}

.login-header p {
    color: #dc2626 !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Customizing Widgets for Dark Mode Login */
[data-testid="stAppViewContainer"] {
    background: transparent;
}

.stTextInput > label, .stCheckbox > label {
    color: #ffffff !important;
    font-weight: 500 !important;
}

.stTextInput input {
    background-color: #1a1a1a !important;
    border: 1px solid #333333 !important;
    color: white !important;
    border-radius: 4px !important;
    padding: 12px !important;
}

.stTextInput input:focus {
    border-color: #dc2626 !important;
}

.stButton > button {
    width: 100% !important;
    background: #dc2626 !important;
    color: white !important;
    border: none !important;
    padding: 12px 20px !important;
    border-radius: 4px !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    transition: all 0.2s ease !important;
    margin-top: 20px !important;
}

.stButton > button:hover {
    background: #b91c1c !important;
    box-shadow: 0 0 20px rgba(220, 38, 38, 0.4) !important;
}

div[data-testid="stRadio"] label {
    color: #ffffff !important;
}

div[data-testid="stRadio"] [role="radiogroup"] {
    gap: 20px;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# ---------- COLORS ----------
chart_colors = ["#4CAF50","#FF9800","#9C27B0","#2196F3","#F44336","#009688"]

# ---------- HELPERS ----------
def strip_emoji(text):
    return re.sub(r'[^\x00-\x7F]+', '', text).strip()

def close_fig(fig):
    plt.close(fig)

# ---------- AUTH ----------
def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    return requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}).json()

def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    return requests.post(url, json={"email": email, "password": password, "returnSecureToken": True}).json()

# ---------- INSIGHTS (NLG) ----------
def generate_insights(df):
    num = df.select_dtypes(include=[np.number]).columns
    insights = []

    if len(num) >= 2:
        corr = df[num].corr()
        for i in range(len(num)):
            for j in range(i + 1, len(num)):
                val = corr.iloc[i, j]
                if pd.isna(val):
                    continue
                
                direction = "Positive" if val > 0 else "Negative"
                if abs(val) > 0.7:
                    insights.append(f"Strong: '{num[i]}' & '{num[j]}' have a Strong {direction} Trend. They move closely together. ({val:.2f})")
                elif abs(val) > 0.4:
                    insights.append(f"Moderate: '{num[i]}' & '{num[j]}' have a Moderate {direction} Trend. Visible relationship exists. ({val:.2f})")
                elif abs(val) > 0.1:
                    insights.append(f"Weak: '{num[i]}' & '{num[j]}' have a Weak {direction} Trend. A subtle pattern may be present. ({val:.2f})")

    # Categorical Insights
    cat = df.select_dtypes(include=['object', 'category']).columns
    for c in cat:
        vc = df[c].value_counts()
        if not vc.empty:
            top_val = vc.idxmax()
            top_pct = (vc.max() / len(df)) * 100
            if top_pct > 40:
                insights.append(f"Category: In '{c}', '{top_val}' dominates the dataset, making up {top_pct:.1f}% of the records.")

    if not insights:
        insights.append("No strong relationships found")

    corr_matrix = df[num].corr() if len(num) >= 2 else None
    return insights, corr_matrix

# ---------- AUTO EDA (HIGHLIGHTED) ----------
def run_auto_eda(df):
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist() 
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # --- 1. Dataset Overview ---
    st.subheader(" Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Numeric Columns", len(num_cols))
    col4.metric("Categorical Columns", len(cat_cols))

    with st.expander(" Column Data Types", expanded=False):
        dtype_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Non-Null Count": df.notnull().sum().values,
            "Null %": (df.isnull().sum().values / len(df) * 100).round(2)
        })
        st.dataframe(dtype_df.style.map(lambda x: 'background-color: #ffcccc' if x > 0 else '', subset=['Null %']), use_container_width=True)

    st.markdown("---")

    # --- 2. Missing Value Analysis ---
    st.subheader(" Missing Value Analysis")
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        st.success(" No missing values found in the dataset!")
    else:
        miss_df = pd.DataFrame({
            "Column": missing.index,
            "Missing Count": missing.values,
            "Missing %": (missing.values / len(df) * 100).round(2)
        })
        st.dataframe(miss_df.style.background_gradient(cmap='Reds', subset=['Missing %']), use_container_width=True)

        fig = px.bar(
            miss_df, x="Column", y="Missing %",
            title="Missing Values by Column (%)",
            color="Column",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        st.plotly_chart(fig, use_container_width=True, key="eda_missing_data_bar")

    st.markdown("---")

    # --- 3. Statistical Summary ---
    st.subheader(" Statistical Summary")
    if num_cols:
        stats_df = df[num_cols].describe().T.round(2)
        st.dataframe(stats_df.style.background_gradient(cmap='Blues'), use_container_width=True)
    else:
        st.info("No numeric columns to summarize.")

    st.markdown("---")

    # --- 4. Numeric Column Distributions ---
    if num_cols:
        st.subheader("Numeric Column Distributions")
        st.caption("Histogram + Box plot for each numeric column")

        cols_per_row = 2
        for i in range(0, len(num_cols), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, col_name in enumerate(num_cols[i:i + cols_per_row]):
                with row_cols[j]:
                    st.markdown(f"**{col_name}**")
                    global_idx = i + j
                    fig = px.histogram(
                        df, x=col_name,
                        marginal="box",
                        color_discrete_sequence=[px.colors.qualitative.Vivid[global_idx % len(px.colors.qualitative.Vivid)]],
                        title=col_name
                    )
                    fig.update_layout(height=300, margin=dict(t=30, b=10))
                    st.plotly_chart(fig, use_container_width=True, key=f"eda_dist_{col_name}")

        st.markdown("---")

    # --- 5. Outlier Detection ---
    if num_cols:
        st.subheader(" Outlier Detection (IQR Method)")
        outlier_summary = []
        for col_name in num_cols:
            Q1 = df[col_name].quantile(0.25)
            Q3 = df[col_name].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers = df[(df[col_name] < lower) | (df[col_name] > upper)]
            outlier_summary.append({
                "Column": col_name,
                "Outlier Count": len(outliers),
                "Outlier %": round(len(outliers) / len(df) * 100, 2),
                "Lower Bound": round(lower, 2),
                "Upper Bound": round(upper, 2)
            })

        outlier_df = pd.DataFrame(outlier_summary)
        st.dataframe(outlier_df.style.background_gradient(cmap='Oranges', subset=['Outlier %']), use_container_width=True)

        with st.expander("View Box Plots for Outliers"):
            for idx, col_name in enumerate(num_cols):
                fig = px.box(df, y=col_name, title=f"Box Plot — {col_name}",
                             color_discrete_sequence=[px.colors.qualitative.Pastel[idx % len(px.colors.qualitative.Pastel)]])
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True, key=f"eda_outlier_box_{col_name}")

        st.markdown("---")

    # --- 6. Categorical Distribution (Treemap) ---
    if cat_cols:
        st.subheader(" Categorical Distribution")
        st.caption("Visualizing the relative weight of each category using a Treemap")
        for col_name in cat_cols:
            unique_count = df[col_name].nunique()
            top_val = df[col_name].value_counts().idxmax()
            st.markdown(f"**{col_name}** — {unique_count} unique values | Most common: `{top_val}`")

            val_counts = df[col_name].value_counts().reset_index()
            val_counts.columns = [col_name, "count"]
            val_counts = val_counts.head(20)

            # Use a different color scale for each treemap for variety
            color_scales = ["Reds", "Greens", "Blues", "Purples", "Oranges", "Viridis", "Plasma"]
            scale = color_scales[j % len(color_scales)] if 'j' in locals() else color_scales[0]
            # Wait, there's no j in this loop. I'll use index.
            
            fig = px.treemap(
                val_counts, path=[col_name], values="count",
                color=col_name, # Each category segment gets its own distinct color
                color_discrete_sequence=px.colors.qualitative.Prism,
                title=f"Distribution — {col_name} (Top 20)"
            )
            fig.update_layout(height=450, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True, key=f"eda_treemap_dist_{col_name}")

        st.markdown("---")

    # --- 7. Correlation Heatmap ---
    if len(num_cols) >= 2:
        st.subheader(" Correlation Heatmap")
        corr = df[num_cols].corr()

        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            title="Feature Correlation Matrix"
        )
        fig.update_layout(
            height=500,  # Fixed height to avoid scrolling
            margin=dict(t=50, b=50, l=50, r=50)
        )
        st.plotly_chart(fig, use_container_width=True, key="eda_corr_heatmap_plot")

        st.markdown("**Top Correlated Pairs:**")
        mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
        corr_pairs = corr.where(mask).stack().reset_index()
        corr_pairs.columns = ["Feature 1", "Feature 2", "Correlation"]
        corr_pairs["Abs Correlation"] = corr_pairs["Correlation"].abs()
        corr_pairs = corr_pairs.sort_values("Abs Correlation", ascending=False).head(10)
        
        st.dataframe(corr_pairs[["Feature 1", "Feature 2", "Correlation"]].round(3).style.background_gradient(cmap='Greens', subset=['Correlation']),
                     use_container_width=True)

# ---------- REPORT ----------
# ---------- REPORT ----------
def generate_report(df, insights):
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    
    # Advanced Style Tuning
    styles['Title'].alignment = 1 # Center Alignment
    styles['Title'].fontSize = 22
    styles['Title'].textColor = colors.HexColor("#dc2626")
    styles['Heading2'].spaceBefore = 20
    styles['Heading2'].spaceAfter = 12
    styles['Heading3'].spaceBefore = 15
    styles['Heading3'].spaceAfter = 8
    
    elements = []
    
    # helper for KeepTogether
    def add_kt(header_text, content_obj, style_level='Heading2'):
        elements.append(KeepTogether([
            Paragraph(header_text, styles[style_level]),
            Spacer(1, 5),
            content_obj
        ]))
        elements.append(Spacer(1, 15))

    # 1. Main Title
    elements.append(Paragraph("Luminant BI — Automated Data Analysis Report", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 25))

    # 2. Executive Overview
    overview_data = [
        ["Metric", "Value"],
        ["Total Rows", f"{df.shape[0]:,}"],
        ["Total Columns", str(df.shape[1])],
        ["Missing Cells", f"{df.isnull().sum().sum():,}"],
        ["Duplicate Rows", str(df.duplicated().sum())]
    ]
    t = Table(overview_data, colWidths=[200, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10)
    ]))
    add_kt("1. Executive Dataset Overview", t)

    # 3. Missing Values Summary
    missing = df.isnull().sum()
    if missing.any():
        miss_data = [["Column", "Missing Count", "Percentage"]]
        for col_name, val in missing[missing > 0].items():
            miss_data.append([col_name, str(val), f"{(val/len(df)*100):.1f}%"])
        
        t_miss = Table(miss_data, colWidths=[180, 100, 100])
        t_miss.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#dc2626")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        add_kt("2. Data Integrity: Missing Value Summary", t_miss)
    else:
        elements.append(Paragraph("2. Data Integrity: No missing values found.", styles['Heading2']))
        elements.append(Spacer(1, 15))

    # 4. Outlier Statistics
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if num_cols:
        outlier_data = [["Column", "Outlier Count", "Outlier %"]]
        for col_name in num_cols:
            Q1 = df[col_name].quantile(0.25)
            Q3 = df[col_name].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col_name] < (Q1 - 1.5 * IQR)) | (df[col_name] > (Q3 + 1.5 * IQR))]
            outlier_data.append([col_name, str(len(outliers)), f"{(len(outliers)/len(df)*100):.1f}%"])
        
        t_out = Table(outlier_data, colWidths=[180, 100, 100])
        t_out.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        add_kt("3. Data Quality: Outlier Detection", t_out)

    # 5. Automated Insights
    insight_elements = []
    for insight in insights:
        clean = strip_emoji(insight)
        if clean:
            prefix = clean.split(':')[0] if ':' in clean else "Observation"
            text = clean.split(':', 1)[1] if ':' in clean else clean
            insight_elements.append(Paragraph(f"• <b>{prefix}:</b> {text}", styles['Normal']))
            insight_elements.append(Spacer(1, 5))
    
    if insight_elements:
        elements.append(Paragraph("4. Principal Findings & Trend Analysis", styles['Heading2']))
        elements.append(Spacer(1, 12))
        for item in insight_elements:
            elements.append(item)
        elements.append(Spacer(1, 15))

    # 6. Data Visualizations (Heatmap first)
    if len(num_cols) >= 2:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        ax.set_title("Feature Correlation Heatmap")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.savefig(tmp.name, bbox_inches="tight", dpi=150)
        close_fig(fig)
        
        add_kt("5. Global Feature Correlation Matrix", Image(tmp.name, width=400, height=300), 'Heading2')

    # 7. Distribution Plots (Loop all numeric)
    elements.append(PageBreak())
    elements.append(Paragraph("6. Individual Variable Distributions", styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    for i, col_name in enumerate(num_cols):
        fig, ax = plt.subplots(figsize=(7, 4))
        # Use a seaborn-compatible color
        sns_color = sns.color_palette("husl", len(num_cols))[i]
        sns.histplot(df[col_name], kde=True, ax=ax, color=sns_color) 
        ax.set_title(f"Distribution of {col_name}")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        fig.savefig(tmp.name, bbox_inches="tight", dpi=100)
        close_fig(fig)
        
        # Keep heading and plot together
        add_kt(f"Profile: {col_name}", Image(tmp.name, width=450, height=250), 'Heading3')

    doc = SimpleDocTemplate(buffer)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------- LOGIN/SIGNUP UI ----------
if st.session_state.user is None:
    # Render background
    st.markdown('<div class="login-bg"></div>', unsafe_allow_html=True)
    
    login_container = st.empty()
    with login_container.container():
        # Center the card
        st.markdown('<div class="login-card-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            
            # Header section
            st.markdown(f"""
                <div class="login-header">
                    <h1>Luminant BI</h1>
                    <p>Intelligence Reimagined</p>
                </div>
            """, unsafe_allow_html=True)
            
            mode = st.radio("", ["Login", "Sign Up"], horizontal=True)
            
            if mode == "Sign Up":
                username = st.text_input("Username", placeholder="Choose a username")
            else:
                username = None # Not used directly in sign_in
                
            email = st.text_input("Email", placeholder="name@company.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            st.markdown('<div style="margin: 10px 0;"></div>', unsafe_allow_html=True)
            remember_me = st.checkbox("Keep me logged in", value=True)

            if st.button("Proceed to Dashboard"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    res = sign_in(email, password) if mode == "Login" else sign_up(email, password)
                    if "email" in res:
                        # Success
                        st.session_state.user = {"email": email, "username": username or email.split('@')[0]}
                        if remember_me:
                            cookies["saved_email"] = email
                            cookies.save()
                        login_container.empty()
                        st.rerun() # Use rerun for a clean state transition
                    else:
                        st.error("Authentication Failed. Please check your credentials.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# CRITICAL: Stop execution if user is still not logged in
if st.session_state.user is None:
    st.stop()

# ---------- MAIN APP ----------
st.title("Luminant BI Dashboard")

with st.sidebar:
    st.success(f"Logged in as {st.session_state.user['username']}")

    if st.button("Logout"):
        st.session_state.user = None
        if "saved_email" in cookies:
            del cookies["saved_email"]
            cookies.save()
        # Sleep to give browser time to delete the cookie before refreshing
        time.sleep(0.5)
        st.rerun()

    file = st.file_uploader("Upload CSV", type=["csv"])

    st.markdown("### 🧹 Cleaning")
    remove_duplicates = st.checkbox("Remove duplicates")
    drop_missing = st.checkbox("Drop missing rows")
    fill_method = st.selectbox("Fill missing values", ["None", "Mean", "Median", "Mode"])

    if drop_missing and fill_method != "None":
        st.warning("⚠️ 'Drop missing rows' and 'Fill missing values' are both on. Drop runs first, leaving nothing to fill.")

if file:
    df = pd.read_csv(file)

    if remove_duplicates:
        df = df.drop_duplicates()

    if drop_missing:
        df = df.dropna()

    if fill_method != "None" and not drop_missing:
        for col in df.select_dtypes(include=[np.number]).columns:
            if fill_method == "Mean":
                df[col] = df[col].fillna(df[col].mean())
            elif fill_method == "Median":
                df[col] = df[col].fillna(df[col].median())
            elif fill_method == "Mode":
                mode_vals = df[col].mode()
                if not mode_vals.empty: 
                    df[col] = df[col].fillna(mode_vals[0])

    insights, corr = generate_insights(df)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Visualizations", "Auto EDA", "Insights", "Report"])

    with tab1:
        st.markdown("## Dashboard")
        st.caption("A quick overview of your dataset — key stats and the full data table.")

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='metric-card'>Rows<br>{df.shape[0]}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'>Columns<br>{df.shape[1]}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'>Missing<br>{df.isnull().sum().sum()}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='metric-card'>Duplicates<br>{df.duplicated().sum()}</div>", unsafe_allow_html=True)

        st.markdown("---")

        st.dataframe(df)
        st.download_button("Download Cleaned CSV", df.to_csv(index=False), "cleaned.csv")

    with tab2:
        st.markdown("## Visualizations")
        st.caption("Interactively explore your data — select columns to generate histograms, box plots, scatter plots, bar charts, and a correlation heatmap.")
        num = df.select_dtypes(include=[np.number]).columns 
        cat = df.select_dtypes(include=['object', 'category']).columns

        if len(num) > 0:
            viz_col = st.selectbox("Column", num, key="viz_col")
            viz_col_idx = list(num).index(viz_col)
            st.plotly_chart(px.histogram(df, x=viz_col, color_discrete_sequence=[px.colors.qualitative.Dark24[viz_col_idx % len(px.colors.qualitative.Dark24)]]), key=f"viz_hist_{viz_col}")
            st.plotly_chart(px.box(df, y=viz_col, color_discrete_sequence=[px.colors.qualitative.Light24[viz_col_idx % len(px.colors.qualitative.Light24)]]), key=f"viz_box_{viz_col}")

        if len(num) >= 2:
            x = st.selectbox("X axis", num, key="scatter_x")
            y = st.selectbox("Y axis", num, key="scatter_y")

            if len(cat) > 0:
                color = st.selectbox("Color by", [None] + list(cat), key="scatter_color")
                if color:
                    fig = px.scatter(df, x=x, y=y, color=color, color_discrete_sequence=px.colors.qualitative.Safe)
                else:
                    fig = px.scatter(df, x=x, y=y, color_discrete_sequence=[px.colors.qualitative.Bold[0]])
            else:
                fig = px.scatter(df, x=x, y=y, color_discrete_sequence=[px.colors.qualitative.Bold[0]])

            st.plotly_chart(fig, key="viz_scatter")

        if len(cat) > 0:
            c = st.selectbox("Category", key="cat_col", options=cat)
            count_df = df[c].value_counts().reset_index()
            count_df.columns = [c, "count"]
            
            # Donut Chart for better proportion visualization
            fig = px.pie(
                count_df.head(10), 
                names=c, 
                values="count", 
                hole=0.5,
                title=f"Distribution of {c} (Top 10)",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig, use_container_width=True, key=f"viz_donut_proportions_{c}")

        if len(num) >= 2:
            st.markdown("### Feature Correlation")
            corr = df[num].corr()
            fig = px.imshow(
                corr, 
                text_auto=".2f", 
                aspect="auto",
                color_continuous_scale="YlGnBu", # Different scale for visualization tab
                zmin=-1, zmax=1,
                title="Feature Correlation Matrix"
            )
            fig.update_layout(
                height=500, 
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig, use_container_width=True, key="viz_corr_heatmap_plot")

    with tab3:
        st.markdown("## Automatic Exploratory Data Analysis")
        st.caption("Full EDA report generated automatically from your dataset.")
        run_auto_eda(df)

    with tab4:
        st.markdown("## Insights")
        st.caption("Automatically detected relationships between numeric columns based on correlation strength.")

        n_strong   = sum(1 for i in insights if i.startswith("Strong"))
        n_moderate = sum(1 for i in insights if i.startswith("Moderate"))
        n_weak     = sum(1 for i in insights if i.startswith("Weak"))
        n_cat      = sum(1 for i in insights if i.startswith("Category"))
        n_none     = 1 if insights == ["No strong relationships found"] else 0

        # --- 1. Filter State ---
        if "insight_filter" not in st.session_state:
            st.session_state.insight_filter = "All"

        # --- 2. Filter Bar (Interactive Pills) ---
        st.markdown('<div style="margin-top: 10px; margin-bottom: 20px;"></div>', unsafe_allow_html=True)
        f_cols = st.columns([1.2, 1, 1, 1, 1.5], gap="small")
        
        with f_cols[0]:
            if st.button(f" Show All ({len(insights)})", key="f_all", use_container_width=True):
                st.session_state.insight_filter = "All"
        
        with f_cols[1]:
            if n_strong:
                if st.button(f"🟢 {n_strong} Strong", key="f_strong", use_container_width=True):
                    st.session_state.insight_filter = "Strong"
            else: st.empty()

        with f_cols[2]:
            if st.button(f"🟡 {n_moderate} Moderate", key="f_moderate", use_container_width=True, disabled=(n_moderate == 0)):
                st.session_state.insight_filter = "Moderate"

        with f_cols[3]:
            if st.button(f"🔴 {n_weak} Weak", key="f_weak", use_container_width=True, disabled=(n_weak == 0)):
                st.session_state.insight_filter = "Weak"


        if n_none:
            st.warning("⚪ No significant patterns found in this dataset.")

        st.markdown(f"**Viewing:** `{st.session_state.insight_filter}` patterns")
        st.markdown("---")

        # --- 3. Filtered Rendering ---
        visible_insights = 0
        for insight in insights:
            # Filtering logic
            if st.session_state.insight_filter != "All" and not insight.startswith(st.session_state.insight_filter):
                continue
            
            visible_insights += 1
            if insight.startswith("Strong"):
                parts   = insight.replace("Strong: ", "").rsplit("(", 1)
                pair_desc = parts[0].strip()
                score   = parts[1].replace(")", "").strip() if len(parts) > 1 else ""
                
                card_html = f"""
                <div class="insight-card strong">
                    <div class="insight-badge strong">🟢</div>
                    <div class="insight-body">
                        <div class="insight-label strong">Strong Correlation</div>
                        <div class="insight-text">{pair_desc}</div>
                    </div>
                    <div class="insight-score strong">{score}</div>
                </div>"""

            elif insight.startswith("Moderate"):
                parts   = insight.replace("Moderate: ", "").rsplit("(", 1)
                pair_desc = parts[0].strip()
                score   = parts[1].replace(")", "").strip() if len(parts) > 1 else ""
                
                card_html = f"""
                <div class="insight-card moderate">
                    <div class="insight-badge moderate">🟡</div>
                    <div class="insight-body">
                        <div class="insight-label moderate">Moderate Correlation</div>
                        <div class="insight-text">{pair_desc}</div>
                    </div>
                    <div class="insight-score moderate">{score}</div>
                </div>"""

            elif insight.startswith("Weak"):
                parts   = insight.replace("Weak: ", "").rsplit("(", 1)
                pair_desc = parts[0].strip()
                score   = parts[1].replace(")", "").strip() if len(parts) > 1 else ""
                
                card_html = f"""
                <div class="insight-card none" style="background:#fff5f5; border-color:#feb2b2;">
                    <div class="insight-badge none" style="background:#fee2e2;">🔴</div>
                    <div class="insight-body">
                        <div class="insight-label none" style="color:#dc2626;">Weak Correlation</div>
                        <div class="insight-text" style="color:#1a202c;">{pair_desc}</div>
                    </div>
                    <div class="insight-score none" style="color:#dc2626;">{score}</div>
                </div>"""

            elif insight.startswith("Category"):
                desc = insight.replace("Category: ", "").strip()
                card_html = f"""
                <div class="insight-card strong">
                    <div class="insight-badge strong">📊</div>
                    <div class="insight-body">
                        <div class="insight-label strong">Dominant Category</div>
                        <div class="insight-text">{desc}</div>
                    </div>
                </div>"""

            else:
                card_html = """
                <div class="insight-card none">
                    <div class="insight-badge none">🔴</div>
                    <div class="insight-body">
                        <div class="insight-label none">All Clear</div>
                        <div class="insight-text">No significant patterns found</div>
                    </div>
                </div>"""

            st.markdown(card_html, unsafe_allow_html=True)

    with tab5:
        st.markdown("##  Report")
        st.caption("Download a PDF report of your dataset including key insights and charts.")
        report = generate_report(df, insights)
        st.download_button("Download PDF", report, "report.pdf")

else:
    st.info("Upload dataset to start")
