import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Smart Pharmacy SaaS", page_icon="💊", layout="wide")

st.title("📊 نظام التنبؤ الذكي بالمخزون والنواقص")
st.markdown("### مستشارك الذكي لإدارة صيدليتك وتحليل بيانات المبيعات والمخزون")

# 2. إعدادات السايدبار الديناميكية
with st.sidebar:
    st.header("📁 تحميل البيانات")
    uploaded_file = st.file_uploader("ارفع ملف المخزون (Excel أو CSV)", type=["csv", "xlsx"])
    
    st.divider()
    st.header("⚙️ إعدادات الأمان الذكية")
    # هنا خلينا حد الأمان ديناميكي في إيد الصيدلي يتغير بناء على ظروف السوق
    safety_factor = st.slider("نسبة مخزون الأمان الإضافي (%)", min_value=0, max_value=100, value=25, step=5)
    st.info(f"💡 سيتم إضافة {safety_factor}% فوق حد الطلب الافتراضي لحماية الصيدلية من نفاد المخزون الفجائي.")

# 3. سيناريو البيانات التجريبية
if uploaded_file is None:
    st.warning("⚠️ أنت تعرض حالياً 'بيانات تجريبية'. يرجى رفع ملف صيدليتك من القائمة الجانبية لتفعيل السيستم حقيقياً.")
    
    medicines = [
        {"name": "Panadol Extra", "stock": 12, "sales": 8.5, "lead": 2},
        {"name": "Catafast 50mg", "stock": 35, "sales": 4.2, "lead": 3},
        {"name": "Augmentin 1g", "stock": 8, "sales": 12.0, "lead": 2},
        {"name": "Conjestal", "stock": 68, "sales": 15.3, "lead": 3},
        {"name": "Brufen 400mg", "stock": 23, "sales": 5.1, "lead": 3},
        {"name": "Omega 3 Plus", "stock": 5, "sales": 0.8, "lead": 5}
    ]
    df = pd.DataFrame(medicines)
    col_name, col_stock, col_sales, col_lead = "name", "stock", "sales", "lead"

else:
    # 4. سيناريو قراءة ملف العميل الحقيقي
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("✅ تم رفع ملفك بنجاح! يرجى مطابقة أعمدة الملف:")
        
        all_columns = df.columns.tolist()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            col_name = st.selectbox("عمود (اسم الدواء):", all_columns, index=0)
        with col2:
            col_stock = st.selectbox("عمود (المخزون الحالي):", all_columns, index=min(1, len(all_columns)-1))
        with col3:
            col_sales = st.selectbox("عمود (متوسط المبيعات اليومي):", all_columns, index=min(2, len(all_columns)-1))
        with col4:
            col_lead = st.selectbox("عمود (فترة التوريد/أيام):", all_columns, index=min(3, len(all_columns)-1))
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        st.stop()

# 5. محرك الحسابات الذكي والديناميكي (Dynamic Reorder Point Engine)
try:
    df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
    df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
    df[col_lead] = pd.to_numeric(df[col_lead], errors='coerce').fillna(3)

    # حساب نقطة الطلب الأساسية (الاستهلاك خلال فترة التوريد)
    base_reorder = df[col_sales] * df[col_lead]
    
    # حساب مخزون الأمان الديناميكي بناء على السلايدر
    df['مخزون الأمان (Safety Stock)'] = (base_reorder * (safety_factor / 100)).round(1)
    
    # نقطة إعادة الطلب النهائية التفاعلية
    df['نقطة إعادة الطلب (الحد الحرج)'] = (base_reorder + df['مخزون الأمان (Safety Stock)']).round(1)
    
    # كم يوم باقي وينفد المخزون فعلياً
    df['الأيام المتبقية لنفاد المخزون'] = np.where(df[col_sales] > 0, (df[col_stock] / df[col_sales]).round(1), 999)
    
    # اتخاذ القرار بناء على النقطة الديناميكية الجديدة
    df['حالة القرار'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب (الحد الحرج)'], '⚠️ اطلب فوراً (مخزون حرج)', '✅ المخزون آمن')

    # 6. عرض مؤشرات الأداء (KPI Cards)
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        critical_count = len(df[df['حالة القرار'] == '⚠️ اطلب فوراً (مخزون حرج)'])
        st.metric(label="🚨 أصناف بحاجة لأمر توريد فوري", value=critical_count)
    with kpi2:
        st.metric(label="📦 إجمالي الأصناف في الملف", value=len(df))

    st.divider()

    # 7. الرسوم البيانية التفاعلية مع تظبيط المحاور والمظهر المائل
    st.subheader("📊 التحليل البصري للمخزون والمبيعات")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("##### 📈 مقارنة متوسط المبيعات اليومي لكل دواء")
        fig_sales = px.bar(
            df, 
            x=col_name, 
            y=col_sales, 
            color='حالة القرار',
            color_discrete_map={'⚠️ اطلب فوراً (مخزون حرج)': '#FF4B4B', '✅ المخزون آمن': '#00F59B'},
            labels={col_name: 'اسم الدواء', col_sales: 'متوسط المبيعات اليومي'},
            template="plotly_dark"
        )
        fig_sales.update_layout(xaxis_tickangle=0, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_sales, use_container_width=True)
        
    with chart_col2:
        st.markdown("##### 📉 المخزون الحالي مقارنة بالحد الحرج")
        fig_stock = px.line(
            df, 
            x=col_name, 
            y=[col_stock, 'نقطة إعادة الطلب (الحد الحرج)'],
            markers=True,
            labels={'value': 'الكمية', 'variable': 'المؤشر', col_name: 'اسم الدواء'},
            template="plotly_dark"
        )
        fig_stock.update_layout(xaxis_tickangle=0, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_stock, use_container_width=True)

    st.divider()

    # 8. عرض الجدول النهائي والتحميل
    st.subheader("📋 تقرير وتوصيات إدارة المخزون التفصيلي")
    status_filter = st.radio("تصفية الجدول حسب:", ["عرض الكل", "أصناف حرجة فقط (اطلب فوراً)", "أصناف آمنة"])
    
    final_df = df[[col_name, col_stock, col_sales, 'الأيام المتبقية لنفاد المخزون', 'مخزون الأمان (Safety Stock)', 'نقطة إعادة الطلب (الحد الحرج)', 'حالة القرار']]
    
    if status_filter == "أصناف حرجة فقط (اطلب فوراً)":
        final_df = final_df[final_df['حالة القرار'] == '⚠️ اطلب فوراً (مخزون حرج)']
    elif status_filter == "أصناف آمنة":
        final_df = final_df[final_df['حالة القرار'] == '✅ المخزون آمن']

    st.dataframe(final_df, use_container_width=True)
    
    # 9. تحميل التقارير
    st.subheader("📥 تحميل أمر التوريد للموردين")
    csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 تحميل النواقص الحالية كملف CSV للمخازن",
        data=csv_data,
        file_name="pharmacy_order_report.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"تأكد من مطابقة الأعمدة بشكل صحيح. تفاصيل الخطأ: {str(e)}")
