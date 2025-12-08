import streamlit as st
import requests

st.set_page_config(page_title="중3 입시 가이드", layout="centered")
st.title("🎓 중3 전공-과목 추천기")

# 1. API 키 설정
try:
    API_KEY = st.secrets["CAREER_API_KEY"]
except:
    st.error("🔑 API 키 설정을 확인해주세요! (Settings > Secrets)")
    st.stop()

major_name = st.text_input("궁금한 학과 이름 (예: 컴퓨터, 간호, 디자인)")

if major_name:
    # [수정 포인트] svcType=api 추가 및 svcId를 major에서 전문직업/학과로 확인
    # 커리어넷 학과 정보 API 호출 URL 최적화
    url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
    params = {
        "apiKey": API_KEY,
        "svcMeta": "dict",
        "svcId": "major",       # 학과 정보 서비스 ID
        "svcType": "api",       # [중요] 반드시 api로 기재
        "contentType": "json"
    }
    
    with st.spinner('커리어넷에서 정보를 불러오고 있습니다...'):
        try:
            # params를 사용하여 안전하게 URL 생성
            response = requests.get(url, params=params)
            data = response.json()
            
            # 응답 구조 확인 (커리어넷의 실제 반환 구조는 dataSearch 아래에 content가 있음)
            if 'dataSearch' in data and 'content' in data['dataSearch']:
                majors = data['dataSearch']['content']
                # 검색어가 포함된 학과 찾기
                target = next((m for m in majors if major_name in m['majorName']), None)

                if target:
                    st.success(f"✅ {target['majorName']} 정보를 찾았습니다.")
                    
                    # 탭 기능을 사용하여 깔끔하게 정보 분리
                    tab1, tab2 = st.tabs(["학과 소개", "추천 과목 가이드"])
                    
                    with tab1:
                        st.subheader("🏛️ 주요 교육 내용")
                        st.write(target.get('mainCourse', '정보 없음'))
                    
                    with tab2:
                        st.subheader("📚 2022 개정 교육과정 대비")
                        st.info("고교학점제 시행에 따라, 해당 전공은 아래 과목 이수를 권장합니다.")
                        st.write("- **공통과목:** 수학, 영어, 과학")
                        st.write("- **선택과목 추천:** 해당 학과와 연관된 '진로선택과목'을 확인하세요.")
                else:
                    st.warning(f"'{major_name}' 학과를 찾지 못했습니다. (추천: 컴퓨터, 기계, 교육)")
            else:
                st.error("⚠️ 커리어넷 응답 오류")
                st.write("API 요청 파라미터를 다시 확인해주세요.")
                st.expander("에러 상세 로그").json(data)
                
        except Exception as e:
            st.error(f"❌ 연결 오류: {e}")

st.divider()
st.caption("제공: 커리어넷 오픈 API / 중3 고교학점제 준비용 프로토타입")
