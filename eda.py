import streamlit as st
import numpy as np
import joblib
import plotly.graph_objects as go

# ✅ 모델 불러오기
model = joblib.load("classifier2_model.pkl")

def run_eda():
    st.title("🩺 건강 예측 AI")
    st.markdown("📌 **아래 설문지를 작성하면 AI가 건강 위험도를 예측합니다.**")
    
    # ✅ 평균값 설정 (BMI 추가)
    avg_values_male = {
        "몸무게 (kg)": 74, "대한민국 평균 BMI": 24.8,
        "수축기 혈압": 120, "이완기 혈압": 78,
        "고혈압 위험": 30, "당뇨병 위험": 15, "고지혈증 위험": 25
    }

    avg_values_female = {
        "몸무게 (kg)": 62, "대한민국 평균 BMI": 24.2,
        "수축기 혈압": 115, "이완기 혈압": 75,
        "고혈압 위험": 28, "당뇨병 위험": 12, "고지혈증 위험": 20
    }

    # ✅ 설문 스타일의 입력 폼
    with st.form("health_form"):
        st.markdown("### 📝 **개인정보 설문**")
        st.info("아래 정보를 입력해주세요. (실제 값이 아닐 경우 예측 정확도가 떨어질 수 있습니다.)")

        col1, col2 = st.columns(2)
        with col1:
            gender = st.radio("🔹 성별", ["여성", "남성"])
            age = st.slider("🔹 나이", 10, 100, 40)

        with col2:
            height = st.number_input("🔹 키 (cm)", min_value=120, max_value=250, value=170)
            weight = st.number_input("🔹 몸무게 (kg)", min_value=30, max_value=200, value=70)

        st.markdown("---")  # 🔹 구분선 추가
        st.markdown("### 💖 **건강 정보 입력**")

        col3, col4 = st.columns(2)
        with col3:
            systolic_bp = st.number_input("💓 수축기(최고) 혈압 (mmHg)", min_value=50, max_value=200, value=120)
        with col4:
            diastolic_bp = st.number_input("🩸 이완기(최저) 혈압 (mmHg)", min_value=40, max_value=150, value=80)

        st.markdown("---")  # 🔹 구분선 추가
        st.markdown("### 🏃 **생활 습관 입력**")
        st.text('해당되는 부분에 체크해주세요(중복가능)')

        col5, col6, col7 = st.columns(3)
        with col5:
            smoke = st.checkbox("🚬 흡연 여부")
            smoke = 1 if smoke else 0

        with col6:
            alco = st.checkbox("🍺 음주 여부")
            alco = 1 if alco else 0

        with col7:
            active = st.checkbox("🏃 운동 여부")
            active = 1 if active else 0

        # ✅ 예측 버튼
        st.write("")
        st.write("-----")
        submit = st.form_submit_button("🔮 예측하기")
        st.write("")

    # ✅ 예측 실행
    if submit:
        # 자동 계산 (숨김)
        bp_ratio = round(systolic_bp / diastolic_bp, 2)
        BMI = round(weight / ((height / 100) ** 2), 2)
        blood_pressure_diff = systolic_bp - diastolic_bp

        input_data = np.array([[ 
            1 if gender == "남성" else 0, age, height, weight,
            smoke, alco, active, systolic_bp, diastolic_bp,
            bp_ratio, BMI, blood_pressure_diff  # 🔥 자동 계산된 값 포함 (유저에게 숨김)
        ]])

        predicted_probs = model.predict_proba(input_data)

        # ✅ 질병 리스트
        diseases = ["고혈압", "비만", "당뇨병", "고지혈증"]
        disease_probabilities = {diseases[i]: predicted_probs[i][0][1] * 100 for i in range(len(diseases))}

        st.markdown("---")  # 🔹 구분선 추가
        st.markdown("### 📢 **건강 예측 결과**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="💓 고혈압 위험", value=f"{disease_probabilities['고혈압']:.2f}%")
            st.progress(disease_probabilities["고혈압"] / 100)

            st.metric(label="⚖️ 비만 위험", value=f"{disease_probabilities['비만']:.2f}%")
            st.progress(disease_probabilities["비만"] / 100)

        with col2:
            st.metric(label="🍬 당뇨병 위험", value=f"{disease_probabilities['당뇨병']:.2f}%")
            st.progress(disease_probabilities["당뇨병"] / 100)

            st.metric(label="🩸 고지혈증 위험", value=f"{disease_probabilities['고지혈증']:.2f}%")
            st.progress(disease_probabilities["고지혈증"] / 100)

        st.write("")

        st.write("\n### ✅ 건강 진단 및 조치 추천 ✅")

        def show_health_risk(disease, very_high=90, high=75, moderate=50, low=35):
            prob = disease_probabilities[disease]
    
            if prob > very_high:
                st.error(f"🚨 **{disease} 위험이 매우 높습니다! 즉각적인 관리가 필요합니다. 병원 방문을 추천합니다.**")
            elif prob > high:
                st.warning(f"⚠️ **{disease} 위험이 높습니다. 생활습관 개선이 필요합니다. 주기적인 건강 체크를 권장합니다.**")
            elif prob > moderate:
                st.info(f"ℹ️ **{disease} 위험이 중간 수준입니다. 생활습관 개선을 고려하세요. 운동과 식이조절이 필요할 수 있습니다.**")
            elif prob > low:
                st.success(f"✅ **{disease} 위험이 낮은 편입니다. 건강한 습관을 유지하세요.**")
            else:
                st.success(f"🎉 **{disease} 위험이 매우 낮습니다! 현재 건강 상태가 양호합니다. 건강을 꾸준히 관리하세요.**")
        show_health_risk("고혈압", 90, 70)
        show_health_risk("비만", 90, 70)
        show_health_risk("당뇨병", 70, 50)
        show_health_risk("고지혈증", 70, 50)

        # ✅ 평균 비교 차트 추가 (Plotly 활용)
        st.markdown("---")  # 🔹 구분선 추가
        st.markdown("### 📊 **대한민국 평균값 vs. 유저의 결과값 비교**")
        st.info(
            f"입력한 건강 정보와 일반적인 {gender} 건강 지표를 비교합니다.\n\n"
            "- **파란색:** 대한민국 평균 수치\n"
            "- **빨간색:** 입력한 사용자 데이터\n\n"
            "이를 통해 자신의 건강 상태가 일반적인 평균과 비교해 어느 정도 차이가 있는지 시각적으로 확인할 수 있습니다."
        )

        avg_values = avg_values_male if gender == "남성" else avg_values_female
        user_values = {
            "몸무게 (kg)": weight, "사용자 BMI": BMI,
            "수축기 혈압": systolic_bp, "이완기 혈압": diastolic_bp,
            "고혈압 위험": disease_probabilities["고혈압"],
            "당뇨병 위험": disease_probabilities["당뇨병"],
            "고지혈증 위험": disease_probabilities["고지혈증"]
        }

        # ✅ Plotly 차트 생성
        fig = go.Figure()
        categories = list(avg_values.keys())

        fig.add_trace(go.Bar(
            x=categories, y=list(avg_values.values()),
            name="대한민국 평균", marker_color="blue", opacity=0.7
        ))

        fig.add_trace(go.Bar(
            x=categories, y=list(user_values.values()),
            name="유저 결과값", marker_color="red", opacity=0.7
        ))

        fig.update_layout(
            title="📊 평균값과 결과값 비교",
            xaxis_title="건강 지표",
            yaxis_title="수치",
            barmode="group",
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40),
            height=600  # 🔥 차트 크기 확대
        )

        st.plotly_chart(fig)

        st.markdown("### 📌 **건강 지표 설명**")
        st.info(
            "- **BMI (체질량지수)**: 체중(kg)을 키(m)의 제곱으로 나눈 값으로, 비만 여부를 평가하는 지표입니다. **BMI 25 이상이면 과체중, 30 이상이면 비만**으로 간주됩니다.\n"
            "- **수축기 & 이완기 혈압**: 혈압 측정값 (높을수록 건강 위험 증가)\n"
            "- **고혈압 위험**: 혈압이 정상 범위를 초과할 경우 고혈압 위험 증가\n"
            "- **당뇨병 위험**: 혈당 수치가 높거나 생활습관 요인에 따라 당뇨병 가능성이 높아짐\n"
            "- **고지혈증 위험**: 혈중 콜레스테롤 수치가 높을 경우 혈관 질환 발생 가능성이 증가\n"
            "- **대한민국 평균값**: 한국 성인 평균 건강 지표 (참고용)\n"
        )

if __name__ == "__main__":
    run_eda()
