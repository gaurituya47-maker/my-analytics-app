import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="Writer Analytics Dashboard", layout="wide")

# --- ฟังก์ชันจำลองข้อมูลให้ใกล้เคียงความจริง (Mock Data) ---
@st.cache_data
def generate_writer_data():
    dates = pd.date_range(start=datetime.now() - timedelta(days=60), end=datetime.now())
    n_days = len(dates)
    
    # ข้อมูลนามปากกา minichiko (เน้นวัยรุ่น/โรมานซ์ - ยอดวิวสูง คอนเมนต์ดุ)
    data_minichiko = {
        "Date": dates,
        "Author": "minichiko",
        "Platform": "ReadAWrite",
        "Views": np.random.normal(5000, 800, n_days).astype(int),
        "Add_to_Shelf": np.random.normal(150, 30, n_days).astype(int),
        "Fave": np.random.normal(80, 15, n_days).astype(int),
        "Comments": np.random.normal(45, 10, n_days).astype(int),
        "Revenue_Coins": np.random.normal(1200, 300, n_days).astype(int) # รายได้จากเหรียญ/โดเนท
    }
    
    # ข้อมูลนามปากกา เหมยลี่ฟาง (เน้นนิยายจีนโบราณ - ยอดเก็บเข้าชั้นสูง ยอดขาย E-book (Meb) เด่น)
    data_meilifang = {
        "Date": dates,
        "Author": "เหมยลี่ฟาง",
        "Platform": "Meb / ReadAWrite",
        "Views": np.random.normal(7000, 1200, n_days).astype(int),
        "Add_to_Shelf": np.random.normal(320, 50, n_days).astype(int),
        "Fave": np.random.normal(180, 40, n_days).astype(int),
        "Comments": np.random.normal(30, 8, n_days).astype(int),
        "Revenue_Coins": np.random.normal(4500, 1000, n_days).astype(int) # รวมยอดขาย E-book เฉลี่ยรายวัน
    }
    
    df1 = pd.DataFrame(data_minichiko)
    df2 = pd.DataFrame(data_meilifang)
    return pd.concat([df1, df2])

df = generate_writer_data()

# --- ส่วนติดต่อผู้ใช้ (UI) ---
st.title("✍️ Writer Backend Analytics: ReadAWrite & Meb")

# Sidebar Filter
author_choice = st.sidebar.selectbox("เลือกนามปากกา", ["ทั้งหมด", "minichiko", "เหมยลี่ฟาง"])
if author_choice != "ทั้งหมด":
    display_df = df[df["Author"] == author_choice]
else:
    display_df = df

# --- สถิติภาพรวม (Key Metrics) ---
total_views = display_df["Views"].sum()
total_shelf = display_df["Add_to_Shelf"].sum()
total_rev = display_df["Revenue_Coins"].sum()
avg_comment = display_df["Comments"].mean()

m1, m2, m3, m4 = st.columns(4)
m1.metric("ยอดวิวรวม", f"{total_views:,}")
m2.metric("เก็บเข้าชั้นรวม", f"{total_shelf:,}")
m3.metric("รายได้ประมาณการ (THB)", f"฿{total_rev:,}")
m4.metric("คอมเมนต์เฉลี่ย/วัน", f"{avg_comment:.1f}")

st.divider()

# --- กราฟวิเคราะห์ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("แนวโน้มยอดวิวรายวัน (Engagement Trend)")
    fig_views = px.line(display_df, x="Date", y="Views", color="Author", 
                        line_shape="spline", template="plotly_dark")
    st.plotly_chart(fig_views, use_container_width=True)

with col2:
    st.subheader("สัดส่วนรายได้เปรียบเทียบ")
    fig_rev = px.area(display_df, x="Date", y="Revenue_Coins", color="Author",
                      title="Revenue Performance (Daily)")
    st.plotly_chart(fig_rev, use_container_width=True)

# --- ตารางวิเคราะห์ Conversion Rate ---
st.subheader("Analytics Deep Dive (Engagement Ratio)")
# คำนวณ Ratio จริงที่นักเขียนมักใช้ดู (Add to Shelf Per Views)
analysis_df = display_df.groupby("Author").agg({
    "Views": "sum",
    "Add_to_Shelf": "sum",
    "Comments": "sum",
    "Revenue_Coins": "sum"
}).reset_index()

analysis_df["Shelf_Rate (%)"] = (analysis_df["Add_to_Shelf"] / analysis_df["Views"] * 100).round(2)
analysis_df["Avg_Revenue_Per_View"] = (analysis_df["Revenue_Coins"] / analysis_df["Views"]).round(2)

st.table(analysis_df)

st.info("💡 **Tips:** สถิติของ 'เหมยลี่ฟาง' มี Shelf Rate สูงกว่าเนื่องจากธรรมชาติของนิยายจีนโบราณที่คนมักดองไว้อ่านทีเดียว ส่วน 'minichiko' จะมี Engagement ในส่วนของคอมเมนต์ที่ Active กว่า")