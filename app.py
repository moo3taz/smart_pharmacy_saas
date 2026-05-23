import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة (أساس ديزاين نظيف)
st.set_page_config(page_title="Smart Pharmacy Pro", layout="wide")

st.title("💊 لوحة تحكم صيدليتك الذكية")

# 2. Sidebar (لرفع الملف)
with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    uploaded_file = st.file_uploader("ارفع ملف المخزون", type=["csv", "xlsx"])

# 3. معالجة البيانات (بشكل مرن)
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # اختيار الأعمدة (عشان السيستم ميبوظش لو الملف اتغير)
    cols = df.columns.tolist()
    with st.expander("🛠️ ضبط أعمدة الملف (هام)"):
        c1, c2, c3 = st.columns(3)
        col_name = c1.selectbox("اسم الدواء", cols, index=0)
        col_stock = c2.selectbox("المخزون", cols, index=1)
        col_sales = c3.selectbox("البيع اليومي", cols, index=2)
        col_lead = c4.selectbox("مدة التوريد", cols, index=3)
        col_price = c5.selectbox("السعر", cols, index=4) if len(cols) > 4 else None

    # تنظيف البيانات من أي نصوص
    for c in [col_stock, col_sales, col_lead]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # 4. الحسابات (معادلات بسيطة عشان متهنجش)
    df['Reorder_Point'] = (df[col_sales] * df[col_lead] * 1.2).round(0)
    
    # 5. عرض الديزاين الجديد (KPIs)
    k1, k2, k3 = st.columns(3)
    k1.metric("أصناف حرجة", len(df[df[col_stock] <= df['Reorder_Point']]))
    k2.metric("إجمالي المخزون", int(df[col_stock].sum()))
    k3.metric("عدد الأصناف", len(df))

    # عرض الجدول الرئيسي
    st.subheader("📋 تقرير المخزون")
    st.dataframe(df, use_container_width=True)

    # 6. شارت بسيط (للتوضيح)
    fig = px.bar(df, x=col_name, y=col_stock, color=col_stock, title="مستويات المخزون الحالية")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👋 مرحباً بك! يرجى رفع ملف المخزون للبدء.")
