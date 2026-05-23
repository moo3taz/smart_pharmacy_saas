import streamlit as st
import pandas as pd
import numpy as np

# 1. إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy SaaS", page_icon="💊", layout="wide")

st.title("📊 نظام التنبؤ الذكي بالمخزون والنواقص")
st.markdown("### ارفع ملف مبيعات ومخزون صيدليتك للحصول على تحليلات حقيقية")

# 2. مكان رفع الملف في السايدبار (Sidebar)
with st.sidebar:
    st.header("📁 تحميل البيانات")
    uploaded_file = st.file_uploader("ارفع ملف المخزون (Excel أو CSV)", type=["csv", "xlsx"])
    st.info("💡 ملاحظة: بعد رفع الملف، حدد الأعمدة المقابلة لبياناتك بالأسفل.")

# 3. سيناريو لو العميل لسه مارفعش ملف (نعرض له داتا تجريبية عشان الشاشة ما تظهرش فاضية)
if uploaded_file is None:
    st.warning("⚠️ أنت تعرض حالياً 'بيانات تجريبية'. يرجى رفع ملف صيدليتك من القائمة الجانبية لتفعيل السيستم حقيقياً.")
    
    # داتا تجريبية
    medicines = [
        {"id": 101, "name": "Panadol Extra", "type": "Fast-Moving"},
        {"id": 102, "name": "Catafast 50mg", "type": "Medium-Moving"},
        {"id": 103, "name": "Augmentin 1g", "type": "Fast-Moving"},
        {"id": 104, "name": "Conjestal", "type": "Seasonal-Winter"}
    ]
    inventory_data = []
    for med in medicines:
        inventory_data.append({
            "اسم الدواء": med["name"],
            "المخزون الحالي": np.random.randint(5, 40),
            "متوسط المبيعات اليومي": round(np.random.uniform(2, 10), 1),
            "فترة التوريد (أيام)": 3
        })
    df = pd.DataFrame(inventory_data)
    
    # أسماء الأعمدة الافتراضية للبيانات التجريبية
    col_name = "اسم الدواء"
    col_stock = "المخزون الحالي"
    col_sales = "متوسط المبيعات اليومي"
    col_lead = "فترة التوريد (أيام)"

else:
    # 4. سيناريو قراءة ملف العميل الحقيقي
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("✅ تم رفع ملفك بنجاح! يرجى مطابقة أعمدة الملف:")
        
        # خريطة مطابقة الأعمدة الذكية (تخلي الصيدلي يختار العمود الصح لو الاسم مختلف عنده)
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

# 5. محرك الحسابات الذكي (بيشتغل على الداتا الوهمية أو الحقيقية ديناميكياً)
try:
    # تحويل البيانات لأرقام لضمان عدم حدوث خطأ في الحسابات
    df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
    df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
    df[col_lead] = pd.to_numeric(df[col_lead], errors='coerce').fillna(3) # افتراضي 3 أيام لو فاضي

    # المعادلات
    # كم يوم باقي وينفد المخزون (المخزون ÷ متوسط البيع اليومي)
    df['الأيام المتبقية لنفاد المخزون'] = np.where(df[col_sales] > 0, (df[col_stock] / df[col_sales]).round(1), 999)
    
    # نقطة إعادة الطلب (متوسط البيع × أيام التوريد)
    df['نقطة إعادة الطلب (الحد الحرج)'] = (df[col_sales] * df[col_lead]).round(1)
    
    # تحديد الحالة وأخذ الأكشن
    df['حالة القرار'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب (الحد الحرج)'], '⚠️ اطلب فوراً (مخزون حرج)', '✅ المخزون آمن')

    # 6. عرض مؤشرات الأداء (KPI Cards)
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        critical_count = len(df[df['حالة القرار'] == '⚠️ اطلب فوراً (مخزون حرج)'])
        st.metric(label="🚨 أصناف بحاجة لأمر توريد فوري", value=critical_count)
    with kpi2:
        st.metric(label="📦 إجمالي الأصناف في الملف", value=len(df))

    st.divider()

    # 7. عرض الجدول النهائي الفلتر والبحث والتحميل
    st.subheader("📋 تقرير وتوصيات إدارة المخزون الذكية")
    
    # إمكانية الفلترة بالحالة لحصر النواقص فورا
    status_filter = st.radio("تصفية التقرير حسب:", ["عرض الكل", "أصناف حرجة فقط (اطلب فوراً)", "أصناف آمنة"])
    
    final_df = df[[col_name, col_stock, col_sales, 'الأيام المتبقية لنفاد المخزون', 'نقطة إعادة الطلب (الحد الحرج)', 'حالة القرار']]
    
    if status_filter == "أصناف حرجة فقط (اطلب فوراً)":
        final_df = final_df[final_df['حالة القرار'] == '⚠️ اطلب فوراً (مخزون حرج)']
    elif status_filter == "أصناف آمنة":
        final_df = final_df[final_df['حالة القرار'] == '✅ المخزون آمن']

    st.dataframe(final_df, use_container_width=True)
    
    # 8. أكشن إضافي: الصيدلي يقدر ينزل تقرير النواقص المفلتر كـ Excel أو CSV يبعته للمخزن!
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
