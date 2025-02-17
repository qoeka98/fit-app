import streamlit as st
from huggingface_hub import InferenceClient
import re

def clean_input(text):
    """불필요한 단어(해줘, 알려줘 등)를 제거한 사용자 입력을 반환"""
    text = re.sub(r"\b(해줘|알려줘|설명해 줘|말해 줘)\b", "", text, flags=re.IGNORECASE)
    return text.strip()

def is_health_related(text):
    """입력된 질문이 건강 관련 질문인지 판별"""
    health_keywords = [
        # ✅ 기본 건강 관련 키워드
        "건강", "의학", "의료", "약학", "한의학", "당뇨", "비만", "고지혈증", "고혈압",
        "운동", "영양", "콜레스테롤", "혈압", "혈당", "체중", "심장", "신장", "식습관",
        "혈액 검사", "당뇨병", "저혈압", "체질량", "콜레스테롤 수치",
        
        # ✅ 추가된 질환 관련 키워드
        "암", "폐암", "간암", "위암", "대장암", "심장병", "뇌졸중", "심근경색", "협심증", 
        "치매", "파킨슨병", "우울증", "불안장애", "스트레스", "알츠하이머", "천식", "폐질환",
        "간경화", "신부전", "위염", "장염", "소화불량", "갑상선", "류마티스", "관절염",

        # ✅ 영양 및 다이어트 관련 키워드
        "다이어트", "식이요법", "영양소", "칼슘", "철분", "단백질", "비타민", "미네랄",
        "섭취량", "칼로리", "저염식", "고단백", "채식", "비건", "키토제닉", "간헐적 단식",
        
        # ✅ 생활 습관 및 예방 관련 키워드
        "면역력", "스트레스 관리", "수면", "불면증", "건강검진", "예방접종", "운동법",
        "근력 운동", "유산소 운동", "요가", "필라테스", "명상", "호흡법",

        # ✅ 특정 검사 및 수치 관련 키워드
        "혈당 수치", "혈압 수치", "체지방률", "BMI", "콜레스테롤 검사", "간 수치",
        "신장 기능 검사", "심전도", "혈액형", "빈혈 검사"
    ]
    return any(keyword in text for keyword in health_keywords)

def filter_ai_response(response, user_input):
    """AI 응답에서 첫 줄(질문을 반복한 부분)을 제거"""
    response = response.replace(user_input, "").strip()  # 사용자 질문 제거
    response_lines = response.split("\n")  # 응답을 줄 단위로 분할
    if len(response_lines) > 1:
        response = "\n".join(response_lines[1:]).strip()  # ✅ 첫 줄 제거하고 나머지 반환
    return response
def get_huggingface_token():
    
    token=st.secrets.get("HUGGINGFACE_API_TOKEN")
    return token

def run_snagdam():
    st.title("💬 건강 상담 챗봇")
    st.info('''건강예측을 바탕으로 건강 상담을 진행해보세요! ''')
    token=get_huggingface_token()
    # ✅ Hugging Face Inference API 클라이언트 설정
    client = InferenceClient(
        
        model="google/gemma-2-9b-it", 
        api_key=token
    )

    # ✅ 대화 기록 저장 (초기 시스템 메시지 추가)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "user", "content": "건강 상담을 진행해주세요"}
        ]

    # ✅ 기존 채팅 기록 표시
    for message in st.session_state.messages:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.markdown(message["content"])

    # ✅ 사용자 입력 받기
    chat = st.chat_input("건강 관련 질문을 입력하세요!")

    if chat:
        clean_chat = clean_input(chat)  # 불필요한 단어 제거

        if not is_health_related(clean_chat):
            response = "죄송합니다. 건강 관련 상담만 가능합니다."
        else:
            # ✅ AI가 사용자 입력을 포함하지 않도록 프롬프트 강화
            system_prompt = (
                "너는 건강, 의학, 의료, 약학, 한의학, 당뇨병, 비만, 고지혈증, 고혈압 전문가 AI야. "
                "사용자의 질문을 분석하고, **절대** 사용자 질문을 다시 포함하지 말고 바로 답변만 제공해. "
                "추가적인 문장은 생성하지 않고, 오직 핵심 정보만 전달해."
            )

            # ✅ 사용자 메시지 저장 & UI에 표시
            st.session_state.messages.append({"role": "user", "content": clean_chat})
            with st.chat_message("user"):
                st.markdown(clean_chat)

            # ✅ AI 응답 요청 (Gemma 모델 사용)
            full_prompt = system_prompt + "\n\n" + clean_chat

            response = client.text_generation(
                prompt=full_prompt,
                max_new_tokens=250
            )

            # ✅ 응답에서 첫 줄 제거
            response = filter_ai_response(response, clean_chat)

        # ✅ AI 응답 저장 & UI 표시
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
