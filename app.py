import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.set_page_config(page_title="Auto BI Tool", layout="wide")

st.title("📊 Auto BI – Automated Data Analysis Tool")
st.write("Upload a CSV dataset to automatically analyze it.")

# -----------------------------
# PDF REPORT GENERATOR
# -----------------------------

def generate_report(df, numeric_cols):

    buffer = BytesIO()
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Auto BI Data Analysis Report", styles['Title']))
    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"Rows: {df.shape[0]}", styles['Normal']))
    elements.append(Paragraph(f"Columns: {df.shape[1]}", styles['Normal']))
    elements.append(Spacer(1,20))

    elements.append(Paragraph("Statistical Summary", styles['Heading2']))
    elements.append(Spacer(1,10))

    for col in numeric_cols:
        elements.append(
            Paragraph(
                f"{col} → Mean: {df[col].mean():.2f}, "
                f"Max: {df[col].max():.2f}, "
                f"Min: {df[col].min():.2f}",
                styles['Normal']
            )
        )

    elements.append(Spacer(1,20))
    elements.append(Paragraph("Charts", styles['Heading2']))
    elements.append(Spacer(1,10))

    # Histogram chart
    for col in numeric_cols[:2]:

        fig, ax = plt.subplots(figsize=(4,3))
        ax.hist(df[col], bins=20, color="skyblue", edgecolor="black")
        ax.set_title(col)

        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png")
        img_buffer.seek(0)

        elements.append(Image(img_buffer, width=400, height=250))
        elements.append(Spacer(1,20))

        plt.close(fig)

    # Correlation heatmap
    if len(numeric_cols) >= 2:

        corr = df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(4,3))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)

        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png")
        img_buffer.seek(0)

        elements.append(Image(img_buffer, width=400, height=250))
        elements.append(Spacer(1,20))

        plt.close(fig)

    doc = SimpleDocTemplate(buffer)
    doc.build(elements)

    buffer.seek(0)

    return buffer

# -----------------------------
# FILE UPLOAD
# -----------------------------

file = st.file_uploader("Upload CSV File", type=["csv"])

if file is not None:

    df = pd.read_csv(file)

    st.subheader("Dataset Preview")
    st.dataframe(df)

    # Dataset metrics
    st.subheader("Dataset Overview")

    c1, c2, c3 = st.columns(3)

    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing Values", df.isnull().sum().sum())

    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns
    numeric_cols = [col for col in numeric_cols if "index" not in col.lower() and "id" not in col.lower()]

    # Missing values
    st.subheader("Missing Values")
    st.write(df.isnull().sum())

    # Statistical summary
    st.subheader("Statistical Summary")
    st.write(df[numeric_cols].describe())

    # Color palette
    colors = itertools.cycle([
        "#4CAF50", "#2196F3", "#FF9800", "#9C27B0",
        "#E91E63", "#009688", "#FFC107", "#795548"
    ])

    # -----------------------------
    # HISTOGRAMS
    # -----------------------------

    st.subheader("Automatic Visualizations")

    cols = st.columns(2)

    for i, col in enumerate(numeric_cols):

        with cols[i % 2]:

            fig, ax = plt.subplots(figsize=(3.5,2.5))

            color = next(colors)

            ax.hist(df[col], bins=20, color=color, edgecolor="black", label=col)

            ax.set_title(col)
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")

            ax.legend()

            st.pyplot(fig)

    # -----------------------------
    # HEATMAP
    # -----------------------------

    if len(numeric_cols) >= 2:

        st.subheader("Correlation Heatmap")

        corr = df[numeric_cols].corr()

        fig, ax = plt.subplots(figsize=(4,2.5))

        sns.heatmap(
            corr,
            annot=True,
            cmap="coolwarm",
            linewidths=0.5,
            cbar_kws={"shrink":0.6},
            ax=ax
        )

        ax.set_title("Feature Correlation")

        st.pyplot(fig)

    # -----------------------------
    # INSIGHTS
    # -----------------------------

    st.subheader("Automatic Insights")

    for col in numeric_cols:

        st.write(
            f"📌 **{col}** → "
            f"Mean: {df[col].mean():.2f}, "
            f"Max: {df[col].max():.2f}, "
            f"Min: {df[col].min():.2f}"
        )

    # -----------------------------
    # DOWNLOAD REPORT
    # -----------------------------

    st.subheader("Download Shareable Report")

    report = generate_report(df, numeric_cols)

    st.download_button(
        label="Download PDF Report",
        data=report,
        file_name="AutoBI_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("Upload a CSV file to begin analysis.")