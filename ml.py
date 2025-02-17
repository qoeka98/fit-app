import datetime
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ✅ Google Fit API OAuth 인증 정보
SCOPES = ["https://www.googleapis.com/auth/fitness.activity.read"]
CLIENT_SECRET_FILE = "client_secret.json"  # 다운로드한 JSON 파일

def authenticate_google_fit():
    """✅ Google Fit OAuth 인증 실행"""
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)  # 사용자가 직접 로그인해야 함
    service = build("fitness", "v1", credentials=creds)
    return service

def get_user_google_fit_data():
    """✅ 사용자의 Google Fit 데이터를 가져오는 함수"""
    service = authenticate_google_fit()

    now = datetime.datetime.utcnow()
    start_time = now - datetime.timedelta(days=1)  # 최근 하루 데이터 가져오기
    dataset_id = f"{int(start_time.timestamp() * 1e9)}-{int(now.timestamp() * 1e9)}"

    data_types = {
        "heart_rate": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
        "blood_pressure": "derived:com.google.blood_pressure:com.google.android.gms:merge_blood_pressure",
        "weight": "derived:com.google.weight:com.google.android.gms:merge_weight",
        "height": "derived:com.google.height:com.google.android.gms:merge_height",
    }

    fit_data = {}

    for key, data_source in data_types.items():
        try:
            result = service.users().dataSources().datasets().get(
                userId="me", dataSourceId=data_source, datasetId=dataset_id
            ).execute()

            if "point" in result and len(result["point"]) > 0:
                fit_data[key] = result["point"][-1]["value"][0]["fpVal"]
            else:
                fit_data[key] = "정보 없음"
        except KeyError:
            fit_data[key] = "정보 없음"
        except Exception as e:
            fit_data[key] = f"오류 발생: {e}"

    return fit_data

def run_ml():
    st.title("🩺 건강 예측 AI (Google Fit 연동)")
    st.markdown("📌 **Google Fit에서 데이터를 가져와 자동으로 건강 예측을 실행합니다.**")

    if st.button("🔄 Google Fit 데이터 가져오기"):
        google_fit_data = get_user_google_fit_data()
        st.session_state["google_fit_data"] = google_fit_data  

    fit_data = st.session_state.get("google_fit_data", {})

    heart_rate = fit_data.get("heart_rate", "정보 없음")
    systolic_bp = fit_data.get("blood_pressure", "정보 없음")
    weight = fit_data.get("weight", "정보 없음")
    height = fit_data.get("height", "정보 없음")

    st.write(f"✅ **심박수**: {heart_rate} bpm" if heart_rate != "정보 없음" else "⚠️ **심박수 정보 없음**")
    st.write(f"✅ **수축기 혈압**: {systolic_bp} mmHg" if systolic_bp != "정보 없음" else "⚠️ **수축기 혈압 정보 없음**")
    st.write(f"✅ **몸무게**: {weight} kg" if weight != "정보 없음" else "⚠️ **몸무게 정보 없음**")
    st.write(f"✅ **키**: {height} cm" if height != "정보 없음" else "⚠️ **키 정보 없음**")

if __name__ == "__main__":
    run_ml()
