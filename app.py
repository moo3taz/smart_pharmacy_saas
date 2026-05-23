import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy SaaS Pro", page_icon="💊", layout="wide")

# 2. منطق تسجيل الدخول (Login System)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title("🔐 تسجيل الدخول")
    user = st.sidebar.text_input("اسم المستخدم")
    pw = st.sidebar.text_input("كلمة المرور", type="password")
    if st.sidebar.button("دخول"):
        # يمكنك تغيير اسم المستخدم وكلمة المرور من هنا
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
    st.stop() # إيقاف الكود هنا إذا لم يتم تسجيل الدخول

# --- بعد تسجيل الدخول بنجاح ---
st.title("🚀 نظام Smart Pharmacy SaaS الاحترافي")
st.markdown("---")

# زر تسجيل الخروج في السايدبار
if st.sidebar.button("تسجيل خروج"):
    st.session_state.logged_in = False
    st.rerun()

# 3. إعدادات السايدبار
with st.sidebar:
    st.header("📁 تحميل البيانات")
    uploaded_file = st.file_uploader("ارفع ملف المخزون (Excel/CSV)", type=["csv", "xlsx"])
    st.divider()
    st.header("⚙️ إعدادات الأمان والتنبؤ")
    safety_factor = st.slider("نسبة مخزون الأمان الإضافي (%)", 0, 100, 25, 5)
    forecast_months = st.slider("فترة التنبؤ المستقبلي (شهور)", 1, 6, 3)

# 4. معالجة البيانات
if uploaded_file is None:
    st.info("💡 قم برفع ملف البيانات لتفعيل التحليل الفعلي.")
    df = pd.DataFrame([
        {"name": "Panadol Extra", "stock": 12, "sales": 8.5, "lead": 2, "last_3_months": 750, "active": "Paracetamol"},
        {"name": "Augmentin 1g", "stock": 0, "sales": 12.0, "lead": 2, "last_3_months": 1100, "active": "Amoxicillin"},
        {"name": "Conjestal", "stock": 68, "sales": 15.3, "lead": 3, "last_3_months": 1400, "active": "Paracetamol"},
        {"name": "Omega 3 Plus", "stock": 5, "sales": 0.0, "lead": 5, "last_3_months": 0, "active": "Fish Oil"}
    ])
    col_name, col_stock, col_sales, col_lead, col_history, col_active = "name", "stock", "sales", "lead", "last_3_months", "active"
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

# 5. محرك الحسابات
df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
df[col_lead] = pd.to_numeric(df[col_lead], errors='coerce').fillna(3)

base_reorder = df[col_sales] * df[col_lead]
df['نقطة إعادة الطلب'] = (base_reorder + (base_reorder * (safety_factor / 100))).round(1)
df['حالة القرار'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب'], '⚠️ اطلب فوراً', '✅ آمن')

# 6. التبويبات
tab1, tab2, tab3 = st.tabs(["📋 لوحة التحكم", "🔮 التنبؤ", "🥀 الرواكد والبدائل"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(df, x=col_name, y=col_sales, color='حالة القرار', template="plotly_dark")
        fig1.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.line(df, x=col_name, y=[col_stock, 'نقطة إعادة الطلب'], markers=True, template="plotly_dark")
        fig2.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        st.plotly_chart(fig2, use_container_width=True)
    st.subheader("📋 تفاصيل المخزون")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.header("🔮 محرك التنبؤ")
    df['متوقع_بيع'] = (df[col_sales] * 30 * forecast_months).round(0)
    st.dataframe(df[[col_name, 'متوقع_بيع']], use_container_width=True)

with tab3:
    st.header("🔄 البدائل والرواكد")
    dead = df[(df[col_history] == 0) & (df[col_stock] > 0)]
    st.write("الأصناف الراكدة:", dead)
    missing = df[df[col_stock] == 0][col_name].tolist()
    if missing:
        sel = st.selectbox("اختار دواء ناقص:", missing)
        active = df[df[col_name] == sel][col_active].values[0]
        alts = df[(df[col_active] == active) & (df[col_name] != sel) & (df[col_stock] > 0)]
        st.success(f"البدائل المتاحة للـ {sel}:")
        st.dataframe(alts[[col_name, col_stock]], use_container_width=True)
