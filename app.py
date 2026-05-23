import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy SaaS", layout="wide")

# 2. منطق تسجيل الدخول
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title("🔐 تسجيل الدخول")
    user = st.sidebar.text_input("اسم المستخدم")
    pw = st.sidebar.text_input("كلمة المرور", type="password")
    if st.sidebar.button("دخول"):
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
    st.stop()

# --- بعد تسجيل الدخول ---
st.title("💊 لوحة تحكم صيدليتك الذكية")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ إعدادات النظام")
    uploaded_file = st.file_uploader("ارفع ملف المخزون", type=["csv", "xlsx"])
    safety_factor = st.slider("نسبة مخزون الأمان (%)", 0, 100, 25, 5)
    forecast_months = st.slider("فترة التنبؤ (شهور)", 1, 6, 3)
    if st.button("تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()

# 3. معالجة البيانات
if uploaded_file is None:
    df = pd.DataFrame([
        {"name": "Panadol Extra", "stock": 12, "sales": 8.5, "lead": 2, "last_3": 750, "active": "Paracetamol"},
        {"name": "Augmentin 1g", "stock": 0, "sales": 12.0, "lead": 2, "last_3": 1100, "active": "Amoxicillin"},
        {"name": "Conjestal", "stock": 68, "sales": 15.3, "lead": 3, "last_3": 1400, "active": "Paracetamol"}
    ])
    col_name, col_stock, col_sales, col_lead, col_history, col_active = "name", "stock", "sales", "lead", "last_3", "active"
else:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    cols = df.columns.tolist()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    col_name = c1.selectbox("اسم الدواء", cols, index=0)
    col_stock = c2.selectbox("المخزون", cols, index=1)
    col_sales = c3.selectbox("البيع اليومي", cols, index=2)
    col_lead = c4.selectbox("مدة التوريد", cols, index=3)
    col_history = c5.selectbox("مبيعات 3 شهور", cols, index=4)
    col_active = c6.selectbox("المادة الفعالة", cols, index=5)

# 4. الحسابات
df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
df['نقطة إعادة الطلب'] = ((df[col_sales] * df[col_lead]) * (1 + safety_factor/100)).round(1)

# 5. التبويبات
tab1, tab2, tab3 = st.tabs(["📊 نظرة عامة", "🔮 التنبؤ الذكي", "🥀 الرواكد والبدائل"])

with tab1:
    # كروت الـ KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("إجمالي الأصناف", len(df))
    k2.metric("أصناف حرجة", len(df[df[col_stock] <= df['نقطة إعادة الطلب']]))
    k3.metric("مخزون راكد", len(df[df[col_history] == 0]))
    k4.metric("مبيعات متوقعة", f"{(df[col_sales].sum()*30*forecast_months):,.0f} ج.م")
    
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = px.bar(df, x=col_name, y=col_sales, template="plotly_dark")
        fig1.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        fig2 = px.line(df, x=col_name, y=[col_stock, 'نقطة إعادة الطلب'], markers=True, template="plotly_dark")
        fig2.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(df, use_container_width=True)

with tab2:
    st.header("🔮 التنبؤ الذكي بالمبيعات")
    df['متوقع'] = (df[col_sales] * 30 * forecast_months).round(0)
    st.dataframe(df[[col_name, 'متوقع']], use_container_width=True)

with tab3:
    st.header("🔄 إدارة الرواكد والأصناف الحرجة")
    
    # جدول الأصناف الحرجة
    st.subheader("⚠️ الأصناف الحرجة (يجب طلبها فوراً)")
    critical_df = df[df[col_stock] <= df['نقطة إعادة الطلب']]
    st.dataframe(critical_df[[col_name, col_stock, 'نقطة إعادة الطلب']], use_container_width=True)
    
    # جدول الأصناف الراكدة
    st.subheader("🥀 الأصناف الراكدة (تجميد رأس مال)")
    dead_df = df[df[col_history] == 0]
    st.dataframe(dead_df[[col_name, col_stock]], use_container_width=True)
    
    st.markdown("---")
    # منطق البدائل
    missing = df[df[col_stock] == 0][col_name].tolist()
    if missing:
        st.subheader("🔍 صائد البدائل الذكي")
        sel = st.selectbox("اختار دواء ناقص لمعرفة بدائله:", missing)
        active = df[df[col_name] == sel][col_active].values[0]
        alts = df[(df[col_active] == active) & (df[col_name] != sel) & (df[col_stock] > 0)]
        st.success(f"البدائل المتاحة للـ {sel} في صيدليتك:")
        st.dataframe(alts[[col_name, col_stock]], use_container_width=True)
