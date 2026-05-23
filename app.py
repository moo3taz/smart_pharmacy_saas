import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Smart Pharmacy Pro", layout="wide")
st.title("💊 لوحة تحكم صيدليتك الذكية")

with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    uploaded_file = st.file_uploader("ارفع ملف المخزون", type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    cols = df.columns.tolist()

    with st.expander("🛠️ ضبط الأعمدة"):
        c1, c2, c3 = st.columns(3)
        col_name = c1.selectbox("اسم الدواء", cols)
        col_stock = c2.selectbox("المخزون", cols)
        col_sales = c3.selectbox("البيع اليومي", cols)
        c4, c5 = st.columns(2)
        col_lead = c4.selectbox("مدة التوريد", cols)
        col_price = c5.selectbox("السعر", cols)

    for c in [col_stock, col_sales, col_lead, col_price]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
    
    df['Reorder_Point'] = (df[col_sales] * df[col_lead] * 1.25).round(0)
    
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("إجمالي الأصناف", len(df))
    k2.metric("أصناف حرجة", len(df[df[col_stock] <= df['Reorder_Point']]))
    k3.metric("مخزون راكد", len(df[df[col_stock] > (df[col_sales]*30*6)]))
    k4.metric("إجمالي قيمة المخزون", f"{int((df[col_stock]*df[col_price]).sum()):,}")

    st.markdown("---")
    
    # الشارتس (الديزاين الجديد)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 مستويات المخزون الحالي")
        fig1 = px.bar(df, x=col_name, y=col_stock, color=col_stock, template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        st.subheader("⚠️ الأصناف التي تقترب من النفاذ")
        df_critical = df[df[col_stock] <= df['Reorder_Point']]
        fig2 = px.pie(df_critical, names=col_name, values=col_stock, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 تقرير المخزون التفصيلي")
    st.dataframe(df, use_container_width=True)

else:
    st.info("👋 يرجى رفع ملف المخزون لتظهر لك الـ KPIs والشارتات.")
