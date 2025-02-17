import os
import datetime
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ✅ Google Fit OAuth 설정
CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/fitness.activity.read"]
REDIRECT_URI = "http://localhost:8501"  

def authenticate_google_fit():
    """Google Fit API OAuth 2.0 인증"""

    if not os.path.exists(CLIENT_SECRET_FILE):
        st.error("⚠️ OAuth 인증 파일 (`client_secret.json`)이 없습니다. Google Cloud에서 다운로드하여 추가하세요.")
        return None

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        SCOPES
    )

    # ✅ `redirect_uri` 제거 → 자동으로 처리되도록 설정
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    # ✅ OAuth 요청 URL 출력 (디버깅용)
    st.write(f"🔍 **Debug: 생성된 인증 URL:** `{auth_url}`")
    st.info("Google Fit 데이터를 가져오려면 아래 링크를 클릭하여 로그인하세요.")
    st.markdown(f"[🔗 Google 로그인하기]({auth_url})", unsafe_allow_html=True)

    # ✅ 사용자가 인증 코드를 입력하도록 UI 제공
    auth_code = st.text_input("인증 코드를 입력하고 Enter를 눌러주세요:")

    if auth_code:
        with st.spinner("🔄 인증 진행 중... 잠시만 기다려 주세요."):
            creds = flow.fetch_token(
                code=auth_code,
                redirect_uri=REDIRECT_URI  # ✅ `fetch_token()`에서만 `redirect_uri` 추가
            )
        st.success("✅ 인증이 완료되었습니다! 이제 데이터를 가져올 수 있습니다.")
        return creds
    else:
        return None  # 인증이 완료되지 않으면 None 반환

def get_user_google_fit_data(creds):
    """Google Fit에서 건강 데이터를 가져오는 함수"""

    # ✅ Google Fit API 클라이언트 빌드
    service = build("fitness", "v1", credentials=creds)

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