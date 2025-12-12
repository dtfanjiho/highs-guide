import streamlit as st
import requests
import xmltodict
import urllib.parse 

st.set_page_config(page_title="고교학점제 자료 탐색", layout="centered")
st.title("📚 에듀넷 고교학점제 자료 검색기")
st.write("궁금한 고교학점제 관련 과목/키워드를 검색하고 공식 자료를 확인하세요.")

# 1. API 키 및 도메인 설정 (Secrets에서 가져옴)
try:
    SNO_KEY = st.secrets["KERIS_SNO_KEY"] 
    SVC_DOMAIN = st.secrets.get("SVC_DOMAIN", "highschool-guide.streamlit.app") 
except KeyError:
    st.error("🔑 KERIS_SNO_KEY 또는 SVC_DOMAIN이 Secrets에 등록되지 않았습니다.")
    st.stop()


# --- 에듀넷 API 호출 함수 (이 부분은 변경 없음) ---
def search_keris_contents(query):
    url = "https://api.edunet.net/search/searchApi/search"
    
    params = {
        "collection": "cre_sys", # 고교학점제 관련 자료만 검색
        "sort": "r",            
        "searchType": "all",
        "pageNum": 1,
        "pageSize": 10,
        "sno": SNO_KEY,         
        "svc_version": "4.5",   
        "svc_domain": SVC_DOMAIN 
    }
    
    encoded_query = urllib.parse.quote(query, encoding='utf-8')
    full_url = f"{url}?kwd={encoded_query}&" + urllib.parse.urlencode(params)
    
    try:
        response = requests.get(full_url, timeout=10) 
        if response.status_code == 200 and 'xml' in response.headers.get('Content-Type', '').lower():
            return xmltodict.parse(response.content.decode('utf-8'))
        else:
            return {"error": f"HTTP 오류 발생: {response.status_code}", "raw_content": response.text}
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API 호출 중 네트워크 오류: {e}"}

# --- UI 및 검색 실행 ---
search_query = st.text_input("고교학점제 관련 키워드 (예: 인공지능 기초, 특징)", "특징") # '특징'으로 테스트 권장

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
            # [수정 1] totalCount의 경로를 'search' 직하위로 수정
            total_count = int(api_result['search']['totalCount'])
            
            st.success(f"✅ 총 {total_count}건의 공식 자료를 찾았습니다.")
            
            if total_count > 0:
                # [수정 2] dataList가 totalResults의 자식 노드임을 반영
                data_list_node = api_result['search']['totalResults']['dataList']
                
                # dataList가 NULL이 아닐 때만 'data' 키를 접근
                if data_list_node is not None and 'data' in data_list_node:
                    data_list = data_list_node['data']
                else:
                    data_list = [] # 데이터가 없으면 빈 리스트로 설정
                
                
                # 응답이 단일 항목일 경우 리스트로 변환
                if not isinstance(data_list, list):
                    data_list = [data_list]

                if data_list:
                    for i, item in enumerate(data_list):
                        title = item.get('ttl', '제목 없음')
                        link = item.get('conts_link')
                        
                        st.markdown(f"### {i+1}. {title}")
                        
                        category = item.get('srvc_clsf_nm_path', '분류 정보 없음')
                        st.caption(f"분류: {category}")

                        st.write(item.get('cn', '상세 요약이 없습니다.'))
                        
                        if link:
                            st.markdown(f"[🔗 에듀넷 상세 자료 바로가기]({link})")
                        st.markdown("---")
            else:
                st.warning(f"'{search_query}' 관련 자료가 에듀넷에서 검색되지 않았습니다.")
                
        except KeyError as e:
            st.error(f"⚠️ 데이터 구조 오류: 필수 필드 '{e}'를 찾을 수 없습니다.")
            with st.expander("원본 로그 확인 (구조 파악용)"):
                st.json(api_result)
        except Exception as e:
             st.error(f"알 수 없는 데이터 처리 오류: {e}")

st.divider()
st.caption("제공: 한국교육학술정보원(KERIS) 에듀넷·티클리어 API 기반")
