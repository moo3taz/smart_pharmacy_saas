import streamlit as st
import pandas as pd
import numpy as np

# إعدادات الصفحة
st.set_page_config(page_title="Smart Pharmacy SaaS", page_icon="💊", layout="wide")

st.title("📊 نظام التنبؤ الذكي بالمخزون والنواقص")
st.markdown("### مستشارك الذكي لإدارة صيدليتك بدون خسائر")

# توليد البيانات
medicines = [
    {"id": 101, "name": "Panadol Extra", "type": "Fast-Moving"},
    {"id": 102, "name": "Catafast 50mg", "type": "Medium-Moving"},
    {"id": 103, "name": "Augmentin 1g", "type": "Fast-Moving"},
    {"id": 104, "name": "Conjestal", "type": "Seasonal-Winter"},
    {"id": 105, "name": "Brufen 400mg", "type": "Medium-Moving"},
    {"id": 106, "name": "Omega 3 Plus", "type": "Slow-Moving"}
]

inventory_data = []
for med in medicines:
    if med["type"] == "Fast-Moving":
        stock, sales, time = np.random.randint(10, 30), round(np.random.uniform(8, 15), 1), 2
    elif med["type"] == "Seasonal-Winter":
        stock, sales, time = np.random.randint(50, 100), round(np.random.uniform(12, 20), 1), 3
    elif med["type"] == "Slow-Moving":
        stock, sales, time = np.random.randint(5, 15), round(np.random.uniform(0.1, 1), 1), 5
    else: 
        stock, sales, time = np.random.randint(20, 50), round(np.random.uniform(3, 7), 1), 3

    inventory_data.append({
        "Item_ID": med["id"], "Item_Name": med["name"],
        "Current_Stock": stock, "Daily_Sales_Avg": sales, "Lead_Time_Days": time
    })

df = pd.DataFrame(inventory_data)

# الحسابات
df['Days_Left'] = (df['Current_Stock'] / df['Daily_Sales_Avg']).round(1)
df['Reorder_Point'] = (df['Daily_Sales_Avg'] * df['Lead_Time_Days']).round(1)
df['Status'] = np.where(df['Current_Stock'] <= df['Reorder_Point'], '⚠️ اطلب الآن', '✅ آمن')

# الواجهة
col1, col2 = st.columns(2)
with col1:
    st.metric(label="🚨 أصناف أوشكت على النفاد", value=len(df[df['Status'] == '⚠️ اطلب الآن']))
with col2:
    st.metric(label="📦 إجمالي الأصناف المراقبة", value=len(df))

st.divider()
st.dataframe(df[['Item_Name', 'Current_Stock', 'Daily_Sales_Avg', 'Days_Left', 'Reorder_Point', 'Status']], use_container_width=True)
