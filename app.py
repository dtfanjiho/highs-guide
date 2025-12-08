import streamlit as st
import requests

st.set_page_config(page_title="중3 입시 가이드", layout="centered")
st.title("🎓 중3 전공-과목 추천기")

try:
    API_KEY = st.secrets["CAREER_API_KEY"]
except:
    st.error("🔑 API 키 설정을 확인해주세요 (Settings > Secrets)")
    st.stop()

major_name = st.text_input("궁금한 학과 이름 (예: 간호, 컴퓨터, 경영)")

if major_name:
    url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
    params = {
        "apiKey": API_KEY,
        "svcMeta": "dict",
        "svcId": "major",
        "svcType": "api",
        "contentType": "json"
    }
    
    with st.spinner('커리어넷 데이터 구조 정밀 분석 중...'):
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 1단계: 커리어넷 데이터 추출 시도 (다양한 경로 탐색)
            all_items = []
            if 'dataSearch' in data and 'content' in data['dataSearch']:
                all_items = data['dataSearch']['content']
            elif 'content' in data: # 직계 구조일 경우
                all_items = data['content']
            elif isinstance(data, list): # 리스트 자체가 데이터일 경우
                all_items = data
            
            # 2단계: 필터링 및 결과 출력
            if all_items:
                search_term = major_name.strip().lower()
                found = [m for m in all_items if search_term in m.get('majorName', '').lower()]

                if found:
                    item = found[0]
                    st.success(f"✅ '{item['majorName']}' 학과를 찾았습니다!")
                    
                    st.subheader("🏛️ 무엇을 배우나요?")
                    st.write(item.get('mainCourse', '세부 정보가 제공되지 않는 학과입니다.'))
                    
                    st.subheader("📚 추천 교과목 전략")
                    st.info(f"'{item['majorName']}' 지망생은 고교학점제에서 기초 과목 외에 관련 탐구 과목 이수가 필수적입니다.")
                else:
                    st.warning(f"'{major_name}' 학과를 리스트(총 {len(all_items)}개)에서 찾지 못했습니다.")
                    with st.expander("실제 수신된 학과 목록 맛보기"):
                        for i in all_items[:10]:
                            st.write(f"- {i.get('majorName')}")
            else:
                st.error("⚠️ 데이터를 성공적으로 받았으나 내부에 학과 목록이 없습니다.")
                st.expander("수신된 전체 원본 데이터 확인 (디버깅용)").json(data)
                
        except Exception as e:
            st.error(f"❌ 데이터 파싱 오류: {e}")

st.divider()
st.caption("커리어넷 실시간 API 수신 기반")
