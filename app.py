import streamlit as st
import requests
import xmltodict # XML 처리 라이브러리
import urllib.parse # 검색어 URL 인코딩을 위해 필요

st.set_page_config(page_title="고교학점제 자료 탐색", layout="centered")
st.title("📚 에듀넷 고교학점제 자료 검색기")
st.write("궁금한 고교학점제 관련 과목/키워드를 검색하고 공식 자료를 확인하세요.")

# 1. API 키 및 도메인 설정 (Secrets에서 가져옴)
try:
    SNO_KEY = st.secrets["KERIS_SNO_KEY"] 
    # Streamlit에서 배포된 주소로 가정 (혹은 localhost)
    SVC_DOMAIN = st.secrets.get("SVC_DOMAIN", "highschool-guide.streamlit.app") 
except KeyError:
    st.error("🔑 KERIS_SNO_KEY 또는 SVC_DOMAIN이 Secrets에 등록되지 않았습니다.")
    st.stop()


# --- 에듀넷 API 호출 함수 ---
def search_keris_contents(query):
    # 문서에 명시된 요청 URL
    url = "https://api.edunet.net/search/searchApi/search"
    
    # 2. 요청 변수(Request Parameters) 설정
    params = {
        # 'kwd'는 요청 후 URL 인코딩을 위해 여기서 제외
        "collection": "cre_sys", # 고교학점제 관련 자료만 검색하도록 설정
        "sort": "r",             # 정확도순 정렬
        "searchType": "all",
        "pageNum": 1,
        "pageSize": 10,
        "sno": SNO_KEY,          # 5자리 인증키
        "svc_version": "4.5",    # 현재 검색 엔진 버전
        "svc_domain": SVC_DOMAIN # 접속 도메인 정보
    }
    
    # 3. kwd (검색어)를 UTF-8 URL 인코딩하여 직접 URL에 합침
    encoded_query = urllib.parse.quote(query, encoding='utf-8')
    full_url = f"{url}?kwd={encoded_query}&" + urllib.parse.urlencode(params)
    
    try:
        response = requests.get(full_url, timeout=10) 
        
        if response.status_code == 200:
            # XML을 Python 딕셔너리로 변환
            data_dict = xmltodict.parse(response.content.decode('utf-8'))
            return data_dict
        else:
            return {"error": f"HTTP 오류 발생: {response.status_code}", "raw_content": response.text}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API 호출 중 네트워크 오류: {e}"}

# --- UI 및 검색 실행 ---
search_query = st.text_input("고교학점제 관련 키워드 (예: 인공지능 기초, 경제수학)", "인공지능 기초")

if search_query:
    with st.spinner(f"에듀넷 공식 자료를 '{search_query}'로 검색 중..."):
        api_result = search_keris_contents(search_query)
    
    if "error" in api_result:
        st.error(f"❌ API 호출 실패: {api_result['error']}")
        with st.expander("원본 오류 메시지 확인"):
            st.write(api_result.get("raw_content", "로그 없음"))
    
    else:
        # 4. XML 데이터 구조를 기반으로 최종 데이터 추출
        try:
            # 문서에 명시된 경로: <search><totalResults><dataList>
            total_results = api_result['search']['totalResults']
            total_count = int(total_results['totalCount'])
            
            st.success(f"✅ 총 {total_count}건의 공식 자료를 찾았습니다.")
            
            # 검색 결과 리스트 추출
            data_list = total_results['dataList']['data']
            
            # 응답이 단일 항목일 경우 리스트로 변환
            if not isinstance(data_list, list):
                data_list = [data_list]

            if data_list:
                for i, item in enumerate(data_list):
                    title = item.get('ttl', '제목 없음')
                    link = item.get('conts_link')
                    
                    st.markdown(f"### {i+1}. {title}")
                    
                    # 카테고리 정보 표시
                    category = item.get('srvc_clsf_nm_path', '분류 정보 없음')
                    st.caption(f"분류: {category}")

                    # 본문 요약
                    st.write(item.get('cn', '상세 요약이 없습니다.'))
                    
                    # 상세 페이지 링크 제공
                    if link:
                        st.markdown(f"[🔗 에듀넷 상세 자료 바로가기]({link})")
                    st.markdown("---")
            else:
                st.warning(f"'{search_query}' 관련 자료가 에듀넷에서 검색되지 않았습니다.")
                
        except KeyError as e:
            st.error(f"⚠️ 데이터 구조 오류: 필수 필드 '{e}'를 찾을 수 없습니다.")
            st.write("에듀넷의 XML 응답 구조가 변경되었을 수 있습니다.")
            with st.expander("원본 로그 확인 (구조 파악용)"):
                st.json(api_result)
        except Exception as e:
             st.error(f"알 수 없는 데이터 처리 오류: {e}")

st.divider()
st.caption("제공: 한국교육학술정보원(KERIS) 에듀넷·티클리어 API 기반")
