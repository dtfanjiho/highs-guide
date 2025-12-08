import streamlit as st
import requests

st.set_page_config(page_title="중3 입시 가이드", layout="centered")
st.title("🎓 중3 전공-과목 추천기")

# 1. API 키 설정 (Advanced Settings의 Secrets에 들어있는지 확인하세요)
try:
    API_KEY = st.secrets["CAREER_API_KEY"]
except:
    st.error("🔑 API 키 설정을 확인해주세요! (Advanced Settings > Secrets)")
    st.stop()

major_name = st.text_input("궁금한 학과 이름 (예: 컴퓨터, 간호, 디자인)")

if major_name:
    # 커리어넷 API 호출
    url = f"https://www.career.go.kr/cnet/openapi/getOpenApi?apiKey={API_KEY}&svcMeta=dict&svcId=major&contentType=json"
    
    with st.spinner('커리어넷에서 정보를 불러오고 있습니다...'):
        try:
            response = requests.get(url)
            data = response.json()
            
            # [핵심] 데이터 구조가 맞는지 확인하는 방어 로직
            if 'dataSearch' in data:
                majors = data['dataSearch']['content']
                target = next((m for m in majors if major_name in m['majorName']), None)

                if target:
                    st.success(f"✅ {target['majorName']} 정보를 찾았습니다.")
                    st.subheader("🏛️ 무엇을 배우나요?")
                    st.write(target.get('mainCourse', '정보 없음'))
                    
                    st.subheader("📚 관련 고교 과목")
                    st.info("이 전공은 '전문교과'와 '진로선택과목' 관리가 중요합니다.")
                else:
                    st.warning(f"'{major_name}'와(과) 일치하는 학과를 찾지 못했습니다.")
            else:
                # API 응답에 dataSearch가 없는 경우 (키 오류 등)
                st.error("⚠️ 커리어넷 API 응답 오류")
                st.write("API 키가 아직 승인되지 않았거나 만료되었을 수 있습니다.")
                st.expander("응답 상세 보기").write(data) # 원인 파악용 로그
                
        except Exception as e:
            st.error(f"❌ 연결 오류: {e}")

st.divider()
st.caption("커리어넷 실시간 API 기반 서비스")
