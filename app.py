import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy SaaS Pro", page_icon="💊", layout="wide")

st.title("🚀 نظام Smart Pharmacy SaaS الاحترافي المتكامل")
st.markdown("### المنصة الذكية لإدارة المخزون، التنبؤ بالمبيعات، ومعالجة الرواكد")

# 2. إعدادات السايدبار
with st.sidebar:
    st.header("📁 تحميل البيانات")
    uploaded_file = st.file_uploader("ارفع ملف المخزون والمبيعات", type=["csv", "xlsx"])
    
    st.divider()
    st.header("⚙️ إعدادات الأمان والتحليل")
    safety_factor = st.slider("نسبة مخزون الأمان الإضافي (%)", min_value=0, max_value=100, value=25, step=5)
    forecast_months = st.slider("فترة التنبؤ المستقبلي (شهور)", min_value=1, max_value=6, value=3)

# 3. سيناريو البيانات
if uploaded_file is None:
    st.warning("⚠️ أنت تعرض حالياً 'بيانات تجريبية'.")
    medicines = [
        {"name": "Panadol Extra", "stock": 12, "sales": 8.5, "lead": 2, "last_3_months_sales": 750, "active_ingredient": "Paracetamol"},
        {"name": "Catafast 50mg", "stock": 35, "sales": 4.2, "lead": 3, "last_3_months_sales": 380, "active_ingredient": "Diclofenac Potassium"},
        {"name": "Augmentin 1g", "stock": 0, "sales": 12.0, "lead": 2, "last_3_months_sales": 1100, "active_ingredient": "Amoxicillin"},
        {"name": "Conjestal", "stock": 68, "sales": 15.3, "lead": 3, "last_3_months_sales": 1400, "active_ingredient": "Paracetamol"},
        {"name": "Brufen 400mg", "stock": 23, "sales": 5.1, "lead": 3, "last_3_months_sales": 450, "active_ingredient": "Ibuprofen"},
        {"name": "Omega 3 Plus", "stock": 5, "sales": 0.0, "lead": 5, "last_3_months_sales": 0, "active_ingredient": "Fish Oil"}
    ]
    df = pd.DataFrame(medicines)
    col_name, col_stock, col_sales, col_lead, col_history, col_active = "name", "stock", "sales", "lead", "last_3_months_sales", "active_ingredient"
else:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    all_columns = df.columns.tolist()
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    col_name = c1.selectbox("اسم الدواء", all_columns, index=0)
    col_stock = c2.selectbox("المخزون", all_columns, index=1)
    col_sales = c3.selectbox("البيع اليومي", all_columns, index=2)
    col_lead = c4.selectbox("مدة التوريد", all_columns, index=3)
    col_history = c5.selectbox("مبيعات 3 شهور", all_columns, index=4)
    col_active = c6.selectbox("المادة الفعالة", all_columns, index=5)

# 4. الحسابات
df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
df[col_lead] = pd.to_numeric(df[col_lead], errors='coerce').fillna(3)

base_reorder = df[col_sales] * df[col_lead]
df['نقطة إعادة الطلب'] = (base_reorder + (base_reorder * (safety_factor / 100))).round(1)
df['حالة القرار'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب'], '⚠️ اطلب فوراً', '✅ آمن')

# 5. التبويبات
tab1, tab2, tab3 = st.tabs(["📋 لوحة التحكم", "🔮 التنبؤ", "🥀 الراكد والبدائل"])

with tab1:
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig1 = px.bar(df, x=col_name, y=col_sales, color='حالة القرار', template="plotly_dark")
        fig1.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        st.plotly_chart(fig1, use_container_width=True)
    with chart_col2:
        fig2 = px.line(df, x=col_name, y=[col_stock, 'نقطة إعادة الطلب'], markers=True, template="plotly_dark")
        fig2.update_layout(xaxis_tickangle=-45, margin=dict(b=100))
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.header("🔮 محرك التنبؤ")
    df['متوقع_بيع'] = (df[col_sales] * 30 * forecast_months).round(0)
    st.dataframe(df[[col_name, 'متوقع_بيع']], use_container_width=True)

with tab3:
    st.header("🔄 البدائل والرواكد")
    # منطق البدائل
    missing = df[df[col_stock] == 0][col_name].tolist()
    if missing:
        sel = st.selectbox("اختار دواء ناقص:", missing)
        active = df[df[col_name] == sel][col_active].values[0]
        alts = df[(df[col_active] == active) & (df[col_name] != sel) & (df[col_stock] > 0)]
        st.write(f"بدائل الـ {sel} المتاحة:", alts[[col_name, col_stock]])
