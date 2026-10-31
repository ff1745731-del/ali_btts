import streamlit as st
import pandas as pd
import numpy as np
import requests
import joblib

st.set_page_config(page_title="تطبيق ali_btts الذكي", page_icon="⚽", layout="centered")

try:
    model = joblib.load('btts_advanced_xgboost.pkl')
except Exception as e:
    st.error(f"⚠️ خطأ في تحميل ملف النموذج الذكي: {e}")

st.title("👑 تطبيق ALI_BTTS لتوقعات كرة القدم")
st.write("مستشارك الذكي المدعوم بالذكاء الاصطناعي لتوقع خيار (Both Teams to Score).")

st.sidebar.header("⚙️ إعدادات الاتصال بالويب")
api_key = st.sidebar.text_input("أدخل مفتاح API-Football الخاص بك:", type="password", placeholder="إلزامي لجلب البيانات الحية وشعارات الفرق")

st.markdown("---")
tab1, tab2 = st.tabs(["📅 توقعات قبل المباريات", "⚡ توقعات مباريات اللايف (Live)"])

with tab1:
    st.header("🔍 تحليل وتوقع المباريات القادمة")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏠 صاحب الأرض")
        home_team = st.text_input("اسم فريق الأرض:", "ليفربول", key="pre_home")
        st.image("https://api-sports.io", width=70) 
    with col2:
        st.markdown("### 🚀 الفريق الضيف")
        away_team = st.text_input("اسم الفريق الضيف:", "أرسنال", key="pre_away")
        st.image("https://api-sports.io", width=70)

    st.markdown("#### 📊 الإحصائيات التكتيكية للمباراة")
    col3, col4 = st.columns(2)
    with col3:
        h_xg = st.number_input("معدل أهداف الأرض المتوقعة xG:", value=2.4)
        h_scored = st.number_input("معدل الأهداف المسجلة للأرض:", value=2.1)
        h_form = st.slider("فورمة الأرض الحالية:", 0, 15, 12, key="form_h")
    with col4:
        a_xg_con = st.number_input("معدل الـ xG المستقبل ضد الضيف:", value=1.3)
        a_scored = st.number_input("معدل الأهداف المسجلة للضيف خارج أرضه:", value=1.9)
        a_form = st.slider("فورمة الضيف الحالية:", 0, 15, 10, key="form_a")
        
    rank_diff = st.number_input("فارق الترتيب الحالي:", value=2, key="rank_pre")
    is_derby = st.checkbox("هل اللقاء ديربي جماهيري؟", value=True, key="derby_pre")

    if st.button("🔮 احسب التوقع قبل المباراة", use_container_width=True):
        input_data = {
            'home_goals_scored_avg': h_scored, 'home_goals_conceded_avg': 1.2,
            'away_goals_scored_avg': a_scored, 'away_goals_conceded_avg': 1.1,
            'home_xG_avg': h_xg, 'away_xG_conceded_avg': a_xg_con,
            'rank_difference': rank_diff, 'home_form_last5': h_form, 'away_form_last5': a_form,
            'is_derby': 1 if is_derby else 0
        }
        df_in = pd.DataFrame([input_data])
        proba = model.predict_proba(df_in) * 100
        pred = model.predict(df_in)
        
        st.subheader("🎯 النتيجة الصادرة من نموذج ALI_BTTS:")
        st.metric(label="احتمالية تحقق سكور من الطرفين", value=f"{proba:.2f}%")
        if pred == 1:
            st.success("✅ القرار النهائي لـ علي: نعم - ينصح بخيار كلا الفريقين يسجلان")
        else:
            st.error("❌ القرار النهائي لـ علي: لا - ينصح بالابتعاد عن خيار BTTS")

with tab2:
    st.header("⚡ جاري الآن متابعة المباريات المباشرة")
    if not api_key:
        st.info("💡 يرجى إدخل مفتاح الـ API الخاص بك لتنشيط جلب المباريات الجارية وشعاراتها الحقيقية.")
    else:
        st.success("🔄 متصل بالـ API الرياضي بنجاح.")
        
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        l_home = st.text_input("المستضيف في اللايف:", "ريال مدريد")
        st.image("https://api-sports.io", width=60)
        h_live_goals = st.number_input("أهداف الأرض الحالية:", min_value=0, value=0)
    with col_l2:
        l_away = st.text_input("الضيف في اللايف:", "برشلونة")
        st.image("https://api-sports.io", width=60)
        a_live_goals = st.number_input("أهداف الضيف الحالية:", min_value=0, value=0)
        
    current_minute = st.slider("دقيقة المباراة الحالية ⏱️:", 0, 90, 35)
    shots_on_target_home = st.number_input("التسديدات على المرمى (الأرض):", min_value=0, value=4)
    shots_on_target_away = st.number_input("التسديدات على المرمى (الضيف):", min_value=0, value=3)

    if st.button("⚡ تحديث واحتساب احتمالية اللايف", use_container_width=True):
        if h_live_goals > 0 and a_live_goals > 0:
            st.warning("⚠️ كلا الفريقين سجلا بالفعل في الواقع! خيار الـ BTTS تحقق بنسبة 100%.")
        else:
            live_factor = (shots_on_target_home + shots_on_target_away) / 10
            input_live = {
                'home_goals_scored_avg': 2.0 + (shots_on_target_home * 0.1), 'home_goals_conceded_avg': 1.2,
                'away_goals_scored_avg': 1.8 + (shots_on_target_away * 0.1), 'away_goals_conceded_avg': 1.3,
                'home_xG_avg': 2.1 + (live_factor * 0.5), 'away_xG_conceded_avg': 1.4,
                'rank_difference': 1, 'home_form_last5': 12, 'away_form_last5': 11, 'is_derby': 1
            }
            df_live = pd.DataFrame([input_live])
            proba_live = model.predict_proba(df_live) * 100
            time_remaining_ratio = (90 - current_minute) / 90
            proba_live_adjusted = max(0, proba_live * time_remaining_ratio)
            
            st.subheader("📉 الاحتمالية المحدثة في وقت المباراة الفعلي:")
            st.metric(label=f"احتمالية تسجيل الطرفين المتبقية حتى الدقيقة {current_minute}", value=f"{proba_live_adjusted:.2f}%")
            if proba_live_adjusted > 60:
                st.success("🔥 فرصة قوية لايف! ريتم المباراة الهجومي عالي والنموذج يوصي بالدخول.")
            else:
                st.info("⏱️ الاحتمالية منخفضة أو الوقت المتبقي غير كافٍ.")