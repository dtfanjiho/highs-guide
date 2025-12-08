import streamlit as st
import requests

st.set_page_config(page_title="중3 입시 가이드", layout="centered")
st.title("🎓 중3 전공-과목 추천기")

# 1. API 키 설정
try:
    API_KEY = st.secrets["CAREER_API_KEY"]
except:
    st.error("🔑 API 키를 설정해주세요 (Settings > Secrets)")
    st.stop()

major_name = st.text_input("궁금한 학과 이름 (예: 컴퓨터, 간호, 기계)")

if major_name:
    # [에러 -4 해결책] 파라미터를 최소화하여 서버 에러 방지
    url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
    params = {
        "apiKey": API_KEY,
        "svcMeta": "dict",
        "svcId": "major",       # 학과 정보 서비스 ID
        "svcType": "api",       # api 고정
        "contentType": "json"
    }
    
    with st.spinner('커리어넷에서 데이터를 가져오는 중...'):
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 응답 구조 확인 및 데이터 추출
            if 'dataSearch' in data and 'content' in data['dataSearch']:
                all_majors = data['dataSearch']['content']
                
                # [중요] 파이썬 내부에서 검색어가 포함된 학과 필터링
                found_majors = [m for m in all_majors if major_name in m.get('majorName', '')]

                if found_majors:
                    target = found_majors[0] # 가장 유사한 첫 번째 결과
                    
                    st.success(f"✅ '{target['majorName']}' 학과 정보를 찾았습니다!")
                    
                    tab1, tab2 = st.tabs(["🏛️ 학과 상세", "📚 추천 선택과목"])
                    
                    with tab1:
                        st.subheader("주요 교육 내용")
                        st.write(target.get('mainCourse', '세부 정보가 제공되지 않는 학과입니다.'))
                    
                    with tab2:
                        st.subheader("고교학점제 가이드")
                        st.info(f"'{target['majorName']}' 지망생은 기초 교과(국·영·수)와 함께 전공 연계 탐구 과목 이수를 권장합니다.")
                        st.markdown("---")
                        st.markdown("#### 💡 추천 과목 예시")
                        st.write("1. **기초:** 공통 수학, 공통 과학, 공통 영어")
                        st.write("2. **선택:** 학과와 관련된 사회/과학 탐구 및 전문교과")
                else:
                    st.warning(f"'{major_name}' 학과를 찾지 못했습니다. 다른 키워드로 검색해보세요.")
            else:
                st.error("⚠️ 커리어넷 응답 형식 오류")
                st.expander("로그 보기").json(data)
                
        except Exception as e:
            st.error(f"❌ 데이터 연결 실패: {e}")

st.divider()
st.caption("제공: 커리어넷 오픈 API / 중3 고교학점제 준비용 프로토타입")
