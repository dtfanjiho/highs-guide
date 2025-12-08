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
    # [수정 포인트] 커리어넷 표준 API 파라미터 구조로 재정렬
    url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
    params = {
        "apiKey": API_KEY,
        "svcMeta": "dict",
        "svcId": "major",       # 학과 정보
        "svcType": "api",       # API 타입
        "contentType": "json",
        "searchMajor": major_name # [핵심] 검색어를 파라미터로 직접 전달
    }
    
    with st.spinner('커리어넷에서 최신 입시 정보를 분석 중...'):
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 커리어넷 응답 데이터의 계층 구조를 안전하게 탐색
            # 결과가 data['dataSearch']['content']에 담겨 옵니다.
            if 'dataSearch' in data and 'content' in data['dataSearch']:
                majors = data['dataSearch']['content']
                
                if majors:
                    # 첫 번째 검색 결과 가져오기
                    target = majors[0]
                    
                    st.success(f"✅ {target['majorName']} 학과를 찾았습니다!")
                    
                    tab1, tab2 = st.tabs(["🏛️ 학과 상세 소개", "📚 고교학점제 가이드"])
                    
                    with tab1:
                        st.subheader("주요 교육 내용")
                        st.write(target.get('mainCourse', '정보가 없습니다.'))
                    
                    with tab2:
                        st.subheader("중3을 위한 과목 선택 전략")
                        st.info(f"'{target['majorName']}' 전공은 기초 소양과 함께 진로선택과목의 전문성이 중요합니다.")
                        st.markdown("---")
                        st.markdown("#### 💡 권장 선택 과목 예시")
                        st.write("1. **기초:** 국어, 수학, 영어 공통과목 충실 이수")
                        st.write(f"2. **심화:** 해당 학과와 연관된 탐구(과학/사회) 및 전문 교과 확인")
                        st.caption("※ 학교별로 개설 과목이 다를 수 있으므로 학교 알리미를 함께 참조하세요.")
                else:
                    st.warning(f"'{major_name}' 학과에 대한 검색 결과가 없습니다.")
            else:
                # 에러 로그 노출 및 설명
                st.error("⚠️ 데이터 구조 분석 오류")
                st.write("커리어넷 서버 응답 형식이 변경되었거나 파라미터 불일치 현상이 발생했습니다.")
                st.expander("에러 상세 로그 (디버깅용)").json(data)
                
        except Exception as e:
            st.error(f"❌ 연결 오류: {e}")

st.divider()
st.caption("제공: 커리어넷 오픈 API / 중3 고교학점제 준비용 프로토타입")
