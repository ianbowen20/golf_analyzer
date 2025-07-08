import streamlit as st
import pandas as pd
import numpy as np
import io

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Golf Analytics Model", layout="wide")
st.title("🏌️ RickRunGood-Style Golf Model")

# -------------------------
# FILE UPLOAD
# -------------------------
st.sidebar.header("Upload Your Player Data CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV with player metrics", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### Raw Data Preview")
    st.dataframe(df.head())

    # -------------------------
    # SLIDERS FOR WEIGHTS
    # -------------------------
    st.sidebar.header("Adjust Metric Weights")
    weight_approach = st.sidebar.slider("SG: Approach Weight", 0.0, 1.0, 0.25)
    weight_t2g = st.sidebar.slider("SG: Tee to Green Weight", 0.0, 1.0, 0.20)
    weight_ott = st.sidebar.slider("SG: Off the Tee Weight", 0.0, 1.0, 0.10)
    weight_putting = st.sidebar.slider("SG: Putting Weight", 0.0, 1.0, 0.10)
    weight_bob = st.sidebar.slider("Birdie or Better Weight", 0.0, 1.0, 0.10)
    weight_par5 = st.sidebar.slider("Par 5 Scoring Weight", 0.0, 1.0, 0.05)

    # Normalize weights to sum to 1
    weight_sum = weight_approach + weight_t2g + weight_ott + weight_putting + weight_bob + weight_par5
    if weight_sum == 0:
        st.warning("Please adjust weights to be greater than 0.")
    else:
        weight_approach /= weight_sum
        weight_t2g /= weight_sum
        weight_ott /= weight_sum
        weight_putting /= weight_sum
        weight_bob /= weight_sum
        weight_par5 /= weight_sum

        # -------------------------
        # Z-SCORE NORMALIZATION
        # -------------------------
        for col in ["SG: Approach", "SG: T2G", "SG: OTT", "SG: Putting", "Birdie or Better", "Par 5 Scoring"]:
            if col in df.columns:
                df[col + " Z"] = (df[col] - df[col].mean()) / df[col].std()
            else:
                st.error(f"Column {col} not found in uploaded CSV.")

        # -------------------------
        # CALCULATE WEIGHTED SCORE
        # -------------------------
        df["Model Score"] = (
            df["SG: Approach Z"] * weight_approach +
            df["SG: T2G Z"] * weight_t2g +
            df["SG: OTT Z"] * weight_ott +
            df["SG: Putting Z"] * weight_putting +
            df["Birdie or Better Z"] * weight_bob +
            df["Par 5 Scoring Z"] * weight_par5
        )

        # Sort and display
        df_sorted = df.sort_values("Model Score", ascending=False)

        st.write("### Ranked Players")
        st.dataframe(df_sorted[["Player", "Model Score"] + [col for col in df.columns if "Z" in col]].reset_index(drop=True))

        # -------------------------
        # DOWNLOAD BUTTON
        # -------------------------
        csv = df_sorted.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Ranked CSV",
            data=csv,
            file_name='golf_model_ranked.csv',
            mime='text/csv'
        )
else:
    st.info("Please upload a CSV file to begin.")

# -------------------------
# USAGE:
# Your CSV should have columns:
# 'Player', 'SG: Approach', 'SG: T2G', 'SG: OTT', 'SG: Putting', 'Birdie or Better', 'Par 5 Scoring'
# Add more metrics and sliders as needed for advanced build
# -------------------------
