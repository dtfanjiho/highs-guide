import streamlit as st
import requests

st.set_page_config(page_title="중3 입시 가이드", layout="centered")
st.title("🎓 중3 전공-과목 추천기")

try:
    API_KEY = st.secrets["CAREER_API_KEY"]
except:
    st.error("🔑 API 키를 설정해주세요 (Settings > Secrets)")
    st.stop()

major_name = st.text_input("궁금한 학과 이름 (예: 컴퓨터, 간호, 기계)")

if major_name:
    url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
    params = {
        "apiKey": API_KEY,
        "svcMeta": "dict",
        "svcId": "major",
        "svcType": "api",
        "contentType": "json"
    }
    
    with st.spinner('커리어넷 실시간 데이터 분석 중...'):
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 1. 데이터가 들어있는지 깊게 탐색
            if 'dataSearch' in data and 'content' in data['dataSearch']:
                all_items = data['dataSearch']['content']
                
                # [수정] 대소문자 구분 없이, 그리고 앞뒤 공백 제거하고 검색
                search_term = major_name.strip().lower()
                found = [m for m in all_items if search_term in m.get('majorName', '').lower()]

                if found:
                    item = found[0]
                    st.success(f"✅ '{item['majorName']}' 학과를 찾았습니다!")
                    
                    st.subheader("🏛️ 무엇을 배우나요?")
                    st.write(item.get('mainCourse', '세부 정보 준비 중'))
                    
                    st.subheader("📚 추천 교과목")
                    st.info("고교학점제 대비: 수학, 과학 탐구 과목 중심의 관리가 필요합니다.")
                else:
                    # [디버깅] 검색 결과가 없을 때, 데이터가 오긴 하는지 확인용
                    st.warning(f"'{major_name}' 관련 데이터를 찾지 못했습니다.")
                    with st.expander("데이터가 오고 있나요? (전체 리스트 확인)"):
                        st.write(f"현재 총 {len(all_items)}개의 학과 정보를 불러왔습니다.")
                        st.write("상위 5개 학과 리스트:")
                        for m in all_items[:5]:
                            st.write(f"- {m.get('majorName')}")
            else:
                st.error("데이터 구조를 읽을 수 없습니다.")
                
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")

st.divider()
st.caption("제공: 커리어넷 오픈 API")
