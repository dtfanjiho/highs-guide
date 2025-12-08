import streamlit as st
import requests

# 1. UI 설정
st.set_page_config(page_title="중3 필독! 학과별 권장과목", layout="centered")
st.title("🎓 중3을 위한 입시 가이드")
st.write("진학하고 싶은 학과를 입력하면, 선배들이 추천하는 과목을 알려드려요!")

# 2. 커리어넷 API 정보 (인증키를 발급받으면 "YOUR_KEY" 대신 넣으세요)
API_KEY = st.secrets["CAREER_API_KEY"] # 나중에 설정창에서 안전하게 넣을 예정

# 3. 사용자 입력
major_name = st.text_input("궁금한 학과 이름 (예: 컴퓨터, 간호, 디자인)")

if major_name:
    url = f"https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey={API_KEY}&svcMeta=dict&svcId=major&contentType=json"
    
    with st.spinner('커리어넷에서 실시간 정보 가져오는 중...'):
        response = requests.get(url)
        data = response.json()
        majors = data['dataSearch']['content']
        target = next((m for m in majors if major_name in m['majorName']), None)

        if target:
            st.success(f"✅ {target['majorName']} 학과 정보")
            st.subheader("🏛️ 이런 것을 배워요")
            st.write(target['mainCourse'])
            
            st.subheader("📚 고등학교 때 이 과목 추천!")
            # 중3에게 가장 중요한 권장과목 시각화
            st.info("이 전공은 '국어, 영어, 수학' 기초 위에 '진로선택과목'을 전략적으로 선택하는 것이 유리합니다.")
        else:
            st.error("정확한 학과명을 입력해주세요 (예: 인공지능)")

st.divider()
st.caption("제공: 커리어넷 오픈 API / 제작: 중3을 위한 고교학점제 대시보드")
