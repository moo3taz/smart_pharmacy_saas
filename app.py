import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Smart Pharmacy SaaS Pro", page_icon="💊", layout="wide")

st.title("🚀 نظام Smart Pharmacy SaaS الاحترافي المتكامل")
st.markdown("### المنصة الذكية لإدارة المخزون، التنبؤ بالمبيعات، ومعالجة الرواكد")

# 2. إعدادات السايدبار الديناميكية
with st.sidebar:
    st.header("📁 تحميل البيانات")
    uploaded_file = st.file_uploader("ارفع ملف المخزون والمبيعات", type=["csv", "xlsx"])
    
    st.divider()
    st.header("⚙️ إعدادات الأمان والتحليل")
    safety_factor = st.slider("نسبة مخزون الأمان الإضافي (%)", min_value=0, max_value=100, value=25, step=5)
    forecast_months = st.slider("فترة التنبؤ المستقبلي (شهور)", min_value=1, max_value=6, value=3)

# 3. سيناريو البيانات التجريبية الموسعة لدعم الميزات الجديدة
if uploaded_file is None:
    st.warning("⚠️ أنت تعرض حالياً 'بيانات تجريبية'. يرجى رفع ملف صيدليتك لتفعيل السيستم حقيقياً.")
    
    # داتا افتراضية غنية بالبيانات عشان الميزات الجديدة تبان صح
    medicines = [
        {"name": "Panadol Extra", "stock": 12, "sales": 8.5, "lead": 2, "last_3_months_sales": 750, "active_ingredient": "Paracetamol"},
        {"name": "Catafast 50mg", "stock": 35, "sales": 4.2, "lead": 3, "last_3_months_sales": 380, "active_ingredient": "Diclofenac Potassium"},
        {"name": "Augmentin 1g", "stock": 0, "sales": 12.0, "lead": 2, "last_3_months_sales": 1100, "active_ingredient": "Amoxicillin"},
        {"name": "Conjestal", "stock": 68, "sales": 15.3, "lead": 3, "last_3_months_sales": 1400, "active_ingredient": "Paracetamol + Chlorpheniramine"},
        {"name": "Brufen 400mg", "stock": 23, "sales": 5.1, "lead": 3, "last_3_months_sales": 450, "active_ingredient": "Ibuprofen"},
        {"name": "Omega 3 Plus", "stock": 5, "sales": 0.0, "lead": 5, "last_3_months_sales": 0, "active_ingredient": "Fish Oil"} # راكد
    ]
    df = pd.DataFrame(medicines)
    col_name, col_stock, col_sales, col_lead, col_history, col_active = "name", "stock", "sales", "lead", "last_3_months_sales", "active_ingredient"

else:
    # 4. سيناريو قراءة ملف العميل الحقيقي
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("✅ تم رفع ملفك بنجاح! طابق أعمدة ملفك الحقيقي:")
        
        all_columns = df.columns.tolist()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            col_name = st.selectbox("عمود (اسم الدواء):", all_columns, index=0)
        with col2:
            col_stock = st.selectbox("عمود (المخزون الحالي):", all_columns, index=min(1, len(all_columns)-1))
        with col3:
            col_sales = st.selectbox("عمود (متوسط البيع اليومي):", all_columns, index=min(2, len(all_columns)-1))
        with col4:
            col_lead = st.selectbox("عمود (أيام التوريد):", all_columns, index=min(3, len(all_columns)-1))
            
        col5, col6 = st.columns(2)
        with col5:
            col_history = st.selectbox("عمود (إجمالي مبيعات آخر 3 شهور):", all_columns, index=min(4, len(all_columns)-1))
        with col6:
            col_active = st.selectbox("عمود (المادة الفعالة / البدائل):", all_columns, index=min(5, len(all_columns)-1))
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        st.stop()

# 5. محرك الحسابات الأساسي والديناميكي
try:
    df[col_stock] = pd.to_numeric(df[col_stock], errors='coerce').fillna(0)
    df[col_sales] = pd.to_numeric(df[col_sales], errors='coerce').fillna(0)
    df[col_lead] = pd.to_numeric(df[col_lead], errors='coerce').fillna(3)
    df[col_history] = pd.to_numeric(df[col_history], errors='coerce').fillna(0)

    # حسابات المخزون الذكي
    base_reorder = df[col_sales] * df[col_lead]
    df['مخزون الأمان (Safety Stock)'] = (base_reorder * (safety_factor / 100)).round(1)
    df['نقطة إعادة الطلب'] = (base_reorder + df['مخزون الأمان (Safety Stock)']).round(1)
    df['الأيام المتبقية لنفاد المخزون'] = np.where(df[col_sales] > 0, (df[col_stock] / df[col_sales]).round(1), 999)
    df['حالة القرار'] = np.where(df[col_stock] <= df['نقطة إعادة الطلب'], '⚠️ اطلب فوراً (مخزون حرج)', '✅ المخزون آمن')

    # 📊 إنشاء التبويبات الفاخرة في الواجهة
    tab_dashboard, tab_forecasting, tab_dead_stock = st.tabs([
        "📋 لوحة التحكم والمخزون الحركي", 
        "🔮 التنبؤ الذكي بالمبيعات (Forecasting)", 
        "🥀 الراكد والبدائل الذكية"
    ])

    # ---------------------------------------------------------
    # TAB 1: لوحة التحكم والمخزون الحركي
    # ---------------------------------------------------------
    with tab_dashboard:
        kpi1, kpi2 = st.columns(2)
        with kpi1:
            critical_count = len(df[df['حالة القرار'] == '⚠️ اطلب فوراً (مخزون حرج)'])
            st.metric(label="🚨 أصناف بحاجة لأمر توريد فوري", value=critical_count)
        with kpi2:
            st.metric(label="📦 إجمالي الأصناف المراقبة", value=len(df))

        st.divider()
        
        # الرسوم البيانية المتناسقة
        with chart_col1:
        st.markdown("##### 📈 مقارنة متوسط المبيعات اليومي لكل دواء")
        fig_sales = px.bar(df, x=col_name, y=col_sales, color='حالة القرار',
                           color_discrete_map={'⚠️ اطلب فوراً (مخزون حرج)': '#FF4B4B', '✅ المخزون آمن': '#00F59B'}, 
                           template="plotly_dark")
        
        # التعديل هنا:
        fig_sales.update_layout(
            xaxis_tickangle=-45,  # ميل الأسماء بـ 45 درجة
            margin=dict(t=50, b=100, l=50, r=50) # زيادة الهامش السفلي عشان الأسماء
        )
        st.plotly_chart(fig_sales, use_container_width=True)
        
    with chart_col2:
        st.markdown("##### 📉 المخزون الحالي مقارنة بالحد الحرج")
        fig_stock = px.line(df, x=col_name, y=[col_stock, 'نقطة إعادة الطلب'], markers=True, template="plotly_dark")
        
        # التعديل هنا:
        fig_stock.update_layout(
            xaxis_tickangle=-45,
            margin=dict(t=50, b=100, l=50, r=50)
        )
        st.plotly_chart(fig_stock, use_container_width=True)
        st.divider()
        
        # الجدول والتحميل
        status_filter = st.radio("تصفية الجدول حسب الحالة:", ["عرض الكل", "أصناف حرجة فقط", "أصناف آمنة"])
        final_df = df[[col_name, col_stock, col_sales, 'الأيام المتبقية لنفاد المخزون', 'نقطة إعادة الطلب', 'حالة القرار']]
        if status_filter == "أصناف حرجة فقط":
            final_df = final_df[final_df['حالة القرار'] == '⚠️ اطلب فوراً (مخزون حرج)']
        elif status_filter == "أصناف آمنة":
            final_df = final_df[final_df['حالة القرار'] == '✅ المخزون آمن']
            
        st.dataframe(final_df, use_container_width=True)
        
        csv_data = final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(label="📥 تحميل أمر التوريد المفلتر كملف CSV", data=csv_data, file_name="pharmacy_order_report.csv", mime="text/csv")

    # ---------------------------------------------------------
    # 🔥 TAB 2: التنبؤ الذكي بالمبيعات (Forecasting)
    # ---------------------------------------------------------
    with tab_forecasting:
        st.header("🔮 محرك التنبؤ الإحصائي بالطلب المستقبلي")
        st.markdown(f"بناءً على مبيعات الصيدلية السابقة، إليك حجم الطلبيات المتوقع والمطلوب تجهيزه خلال الـ **{forecast_months} شهور القادمة** لتجنب النواقص:")
        
        # معادلة التنبؤ الذكي (حساب الطلب المستقبلي = متوسط البيع اليومي * 30 يوم * عدد الشهور المستهدفة)
        df['الكمية المتوقع بيعها مستقبلاً'] = (df[col_sales] * 30 * forecast_months).round(0)
        df['الطلب المقترح لشراءه (شحنة جديدة)'] = np.where(df['الكمية المتوقع بيعها مستقبلاً'] > df[col_stock], df['الكمية المتوقع بيعها مستقبلاً'] - df[col_stock], 0)
        
        # رسم بياني يوضح الكميات المطلوبة مستقبلاً
        fig_forecast = px.bar(
            df, x=col_name, y='الكمية المتوقع بيعها مستقبلاً',
            title=f"📦 حجم المبيعات المتوقع المخزن الشامل لكل صنف خلال {forecast_months} شهور",
            labels={'الكمية المتوقع بيعها مستقبلاً': 'الكمية بالعلبة'}, template="plotly_dark", color_discrete_sequence=['#00CCFF']
        )
        st.plotly_chart(fig_forecast, use_container_width=True)
        
        # عرض تقرير المشتريات المستقبلي للصيدلي
        st.subheader("📋 تقرير شحنات الشراء الاستباقية المقترحة للمخازن")
        st.dataframe(df[[col_name, col_stock, col_sales, 'الكمية المتوقع بيعها مستقبلاً', 'الطلب المقترح لشراءه (شحنة جديدة)']], use_container_width=True)

    # ---------------------------------------------------------
    # 🔥 TAB 3: الراكد والبدائل الذكية (Dead Stock & Alternatives)
    # ---------------------------------------------------------
    with tab_dead_stock:
        st.header("🥀 إدارة الرواكد وصيد البدائل الذكية")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📉 أدوية راكدة (خسارة مركونة في الرف)")
            st.markdown("الأدوية دي متباعش منها أي حاجة خلال آخر 3 شهور، السيستم ينصحك ترجعها للمورد فوراً أو تعمل عليها عروض:")
            
            # فلترة الرواكد (المبيعات التاريخية = 0 والمخزون أكبر من 0)
            dead_stock_df = df[(df[col_history] == 0) & (df[col_stock] > 0)]
            if len(dead_stock_df) > 0:
                st.error(f"🚨 تحذير: عندك {len(dead_stock_df)} أصناف راكدة كلياً في المخزن!")
                st.dataframe(dead_stock_df[[col_name, col_stock, col_active]], use_container_width=True)
            else:
                st.success("🎉 هنيئاً لك! لا يوجد أي مخزون راكد في الصيدلية حالياً.")
                
        with col_right:
            st.subheader("🔄 صائد البدائل الذكي للأصناف المنتهية")
            st.markdown("لما يجيلك زبون يطلب دواء ومخزونه عندك **صفر**، اكتب اسم الدواء الناقص هنا والسيستم هيطلعلك الأدوية التانية اللي فيها **نفس المادة الفعالة ومتوفرة عندك في الرف**:")
            
            # كود محرك البدائل المتاح
            out_of_stock_medicines = df[df[col_stock] == 0][col_name].tolist()
            
            if out_of_stock_medicines:
                selected_missing_med = st.selectbox("اختار الدواء الناقص اللي الزبون بيسأل عليه:", out_of_stock_medicines)
                
                # جلب المادة الفعالة للدواء المختار
                missing_active_ingredient = df[df[col_name] == selected_missing_med][col_active].values[0]
                
                # البحث عن البدائل اللي ليها نفس المادة الفعالة ومخزونها أكبر من صفر
                alternatives_df = df[(df[col_active] == missing_active_ingredient) & (df[col_name] != selected_missing_med) & (df[col_stock] > 0)]
                
                if len(alternatives_df) > 0:
                    st.info(f"💡 المادة الفعالة للـ ({selected_missing_med}) هي: **{missing_active_ingredient}**")
                    st.success("✨ البدائل المتاحة عندك في الصيدلية وليها نفس المفعول:")
                    st.dataframe(alternatives_df[[col_name, col_stock]], use_container_width=True)
                else:
                    st.warning(f"⚠️ الدواء ناقص، وللأسف مفيش أي دواء بديل متوفر في الرف حالياً ل نفس المادة الفعالة ({missing_active_ingredient}).")
            else:
                st.success("✅ مفيش أي دواء مخزونه صفر حالياً! كل الأصناف متوفرة.")

except Exception as e:
    st.error(f"تأكد من مطابقة الأعمدة بشكل صحيح. تفاصيل الخطأ: {str(e)}")
