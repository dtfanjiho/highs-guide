import streamlit as st
import requests

st.set_page_config(page_title="중3 입시 가이드", layout="centered")
st.title("🎓 중3 전공-과목 추천기")

try:
    API_KEY = st.secrets["CAREER_API_KEY"]
except:
    st.error("🔑 API 키 설정을 확인해주세요 (Settings > Secrets)")
    st.stop()

major_name = st.text_input("궁금한 직업/학과 이름 (예: 간호사, 의사, 요리사)")

if major_name:
    url = "https://www.career.go.kr/cnet/openapi/getOpenApi"
    # [전략 변경] svcId를 'job'(직업)으로 변경하여 권한 테스트
    params = {
        "apiKey": API_KEY,
        "svcMeta": "dict",
        "svcId": "job",      # 'major' 대신 'job' 시도
        "svcType": "api",
        "contentType": "json"
    }
    
    with st.spinner('데이터 수신 시도 중...'):
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            # 응답 데이터 구조 확인용 로그
            if 'dataSearch' in data and 'content' in data['dataSearch']:
                all_items = data['dataSearch']['content']
                
                # 직업명(jobNm)에서 검색
                found = [m for m in all_items if major_name in m.get('jobNm', '')]

                if found:
                    item = found[0]
                    st.success(f"✅ '{item['jobNm']}' 정보를 찾았습니다!")
                    st.subheader("🏛️ 주요 업무 및 필요 역량")
                    st.write(item.get('jobDic', '상세 정보 준비 중'))
                else:
                    st.warning(f"리스트({len(all_items)}개)에 해당 키워드가 없습니다.")
                    with st.expander("현재 수신 가능한 직업 목록 보기"):
                        for i in all_items[:10]:
                            st.write(f"- {i.get('jobNm')}")
            else:
                st.error("⚠️ 데이터를 성공적으로 받았으나 내부에 데이터가 없습니다.")
                st.write("커리어넷 관리 페이지에서 '서비스 신청 현황'을 꼭 확인하세요!")
                st.expander("실제 수신된 원본 데이터(JSON)").json(data)
                
        except Exception as e:
            st.error(f"❌ 요청 오류: {e}")
