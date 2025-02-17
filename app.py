import streamlit as st
from streamlit_option_menu import option_menu
from eda import run_eda
from home import run_home
from ml import run_ml
from snagdam import run_snagdam

# ✅ 전체 페이지 스타일 설정
st.set_page_config(
    page_title="건강 예측 AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"  # 기본적으로 사이드바 확장
)

def main():
    # ✅ Streamlit Option Menu 사용
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #007bff; font-weight: bold;'>📌 건강 예측 AI</h2>", unsafe_allow_html=True)
        st.markdown("---")  # 구분선 추가
        
        menu = option_menu(
            menu_title="메뉴 선택",
            options=["🏠 홈", "🔍 질병 예측", "📊 구글핏 연동", "💬 상담 챗봇"],
            icons=["house", "stethoscope", "bar-chart-line", "chat-text"],  # 상담 챗봇 아이콘 추가
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px", "background-color": "#f8f9fa"},
                "icon": {"color": "blue", "font-size": "20px"}, 
                "nav-link": {
                    "font-size": "17px",
                    "text-align": "left",
                    "margin": "5px",
                    "padding": "12px",
                    "border-radius": "10px",
                    "transition": "0.3s",
                    "color": "#333",
                },
                "nav-link-selected": {"background-color": "#007bff", "color": "white"},
                "nav-link:hover": {"background-color": "#e9ecef"}  # 호버 효과 추가
            }
        )

    # ✅ 선택된 메뉴 실행
    if menu == "🏠 홈":
        run_home()
    elif menu == "🔍 질병 예측":
        run_eda()
    elif menu == "💬 상담 챗봇":
        run_snagdam()
    elif menu == "📊 구글핏 연동":
        run_ml()
    
# ✅ 실행
if __name__ == "__main__":
    main()
