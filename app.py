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
    # [에러 해결 전략] svcId를 기반으로 한 가장 표준적인 요청
    # 만약 major에서 계속 에러가 나면 svcId를 'job'으로 바꿔서 시도해보는 것도 방법입니다.
    url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
    params = {
        "apiKey": API_KEY,
        "svcMeta": "dict",
        "svcId": "major",       
        "svcType": "api",       
        "contentType": "json"
        # 파라미터를 최소화하여 -4 에러 유발 요인을 차단
    }
    
    with st.spinner('커리어넷 인증 및 데이터 동기화 중...'):
        try:
            # 1. 데이터 가져오기
            response = requests.get(url, params=params)
            data = response.json()
            
            # [디버깅] 데이터가 제대로 안 오면 구조 확인
            if 'dataSearch' in data:
                all_items = data['dataSearch'].get('content', [])
                
                # 검색어 필터링
                found = [m for m in all_items if major_name in m.get('majorName', '') or major_name in m.get('jobName', '')]

                if found:
                    item = found[0]
                    st.success(f"✅ '{item.get('majorName', item.get('jobName'))}' 정보를 찾았습니다!")
                    
                    st.subheader("🏛️ 상세 내용")
                    st.write(item.get('mainCourse', item.get('summary', '정보를 준비 중입니다.')))
                    
                    st.subheader("📚 추천 교과목 전략")
                    st.info("고교학점제 시행으로 인해 위 학과 진학 시 '수학/과학' 탐구 역량이 중요하게 평가됩니다.")
                else:
                    st.warning("학과명을 조금 더 짧게 입력해보세요 (예: 인공지능학과 -> 인공지능)")
            
            # 여전히 -4가 뜨면 에러 원인 분석용 데이터 출력
            elif 'result' in data and data['result'].get('code') == '-4':
                st.error("⚠️ [권한 오류] 커리어넷 API 키 권한 확인 필요")
                st.markdown("""
                이 오류는 발급받은 API 키가 **'학과 정보'** 접근 승인이 안 되었을 때 발생합니다.
                1. **커리어넷 관리 페이지**에서 '학과 정보' 서비스가 신청되었는지 확인하세요.
                2. 만약 안 된다면 **svcId를 'job'**으로 바꿔서 테스트해보겠습니다.
                """)
                
        except Exception as e:
            st.error(f"❌ 요청 중 오류 발생: {e}")

st.divider()
st.caption("커리어넷 실시간 데이터를 연동한 학생용 포털")
