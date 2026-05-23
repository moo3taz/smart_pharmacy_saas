import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy Pro", layout="wide")

# منطق تسجيل الدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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

# 2. Sidebar & Upload
with st.sidebar:
    st.header("⚙️ إعدادات الإدارة")
    uploaded_file = st.file_uploader("ارفع ملف الإكسيل", type=["csv", "xlsx"])
    safety_factor = st.slider("مخزون الأمان (%)", 0, 100, 25)
    if st.button("تسجيل خروج"): st.session_state.logged_in = False; st.rerun()

# 3. معالجة البيانات
if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    cols = df.columns.tolist()
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    col_name = c1.selectbox("اسم الدواء", cols, index=0)
    col_stock = c2.selectbox("المخزون", cols, index=1)
    col_sales = c3.selectbox("البيع اليومي", cols, index=2)
    col_lead = c4.selectbox("مدة التوريد", cols, index=3)
    col_history = c5.selectbox("مبيعات 3 شهور", cols, index=4)
    col_price = c6.selectbox("السعر", cols, index=5)
    col_active = c7.selectbox("المادة الفعالة", cols, index=6)
else:
    # بيانات افتراضية لو مفيش ملف
    df = pd.DataFrame([{"name": "Panadol", "stock": 5, "sales": 8, "lead": 2, "last_3": 0, "price": 50, "active": "Paracetamol"}])
    col_name, col_stock, col_sales, col_lead, col_history, col_price, col_active = "name", "stock", "sales", "lead", "last_3", "price", "active"

# 4. الحسابات الذكية
df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
df['نقطة إعادة الطلب'] = ((df[col_sales] * df[col_lead]) * (1 + safety_factor/100)).round(1)
df['حالة القرار'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب'], '⚠️ اطلب فوراً', '✅ آمن')
df['قيمة_النقص'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب'], (df['نقطة إعادة الطلب'] - df[col_stock]) * df[col_price], 0)

# 5. التبويبات
tab1, tab2, tab3 = st.tabs(["📊 لوحة التحكم", "🔮 التنبؤ والمالية", "🥀 الرواكد والبدائل"])

with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("أصناف حرجة", len(df[df['حالة القرار'] == '⚠️ اطلب فوراً']))
    c2.metric("إجمالي قيمة النواقص", f"{df['قيمة_النقص'].sum():,.0f} ج.م")
    c3.metric("مخزون راكد", len(df[df[col_history] == 0]))
    
    st.subheader("تقرير المخزون")
    def highlight_status(val):
        color = '#FF4B4B' if val == '⚠️ اطلب فوراً' else '#008080'
        return f'background-color: {color}'
    st.dataframe(df.style.applymap(highlight_status, subset=['حالة القرار']), use_container_width=True)

with tab2:
    st.subheader("🔮 التنبؤ والسيولة المطلوبة")
    df['متوقع_بيع'] = (df[col_sales] * 30 * 3).round(0)
    st.dataframe(df[[col_name, 'متوقع_بيع', 'قيمة_النقص']], use_container_width=True)

with tab3:
    st.subheader("🥀 الرواكد والبدائل")
    st.dataframe(df[df[col_history] == 0][[col_name, col_stock, 'قيمة_النقص']], use_container_width=True)
