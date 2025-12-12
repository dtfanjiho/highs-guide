import streamlit as st
import requests
import xmltodict 
import urllib.parse 
import re  # HTML 태그 제거를 위한 모듈

st.set_page_config(page_title="고교학점제 자료 탐색", layout="centered")
st.title("📚 에듀넷 공식 자료 검색기")
st.write("궁금한 과목/키워드를 검색하고 공식 자료를 확인하세요.")

# 1. API 키 및 도메인 설정 (Streamlit Secrets에서 가져옴)
try:
    SNO_KEY = st.secrets["KERIS_SNO_KEY"] 
    SVC_DOMAIN = st.secrets.get("SVC_DOMAIN", "highschool-guide.streamlit.app") 
except KeyError:
    st.error("🔑 KERIS_SNO_KEY 또는 SVC_DOMAIN이 Secrets에 등록되지 않았습니다.")
    st.stop()


# --- 에듀넷 API 호출 함수 ---
def search_keris_contents(query, collection_id):
    url = "https://api.edunet.net/search/searchApi/search"
    
    params = {
        # [핵심 수정] 컬렉션 ID를 변수(collection_id)로 받습니다.
        "collection": collection_id, 
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
search_query = st.text_input("궁금한 과목/키워드 (예: 경제수학, 인공지능 기초)", "경제수학")

# [추가] 컬렉션 선택 기능 (필터)
collection_options = {
    "🔍 전체 검색 (가장 넓은 범위)": "total",
    "📚 고교학점제 관련 자료만": "cre_sys",
    "📝 교육과정 및 수업 자료": "crclm,lsn_design"
}
selected_option = st.selectbox("검색 대상 컬렉션 선택", list(collection_options.keys()))
collection_id = collection_options[selected_option]


if search_query:
    with st.spinner(f"에듀넷 공식 자료를 '{search_query}'로 검색 중 (대상: {selected_option})..."):
        api_result = search_keris_contents(search_query, collection_id)
    
    if "error" in api_result:
        st.error(f"❌ API 호출 실패: {api_result['error']}")
        with st.expander("원본 오류 메시지 확인"):
            st.write(api_result.get("raw_content", "로그 없음"))
    
    else:
        try:
            total_count = int(api_result['search']['totalCount'])
            st.success(f"✅ 총 {total_count}건의 공식 자료를 찾았습니다.")
            
            if total_count > 0:
                data_list_node = api_result['search']['totalResults']['dataList']
                
                if data_list_node is not None and 'data' in data_list_node:
                    data_list = data_list_node['data']
                else:
                    data_list = [] 
                
                if not isinstance(data_list, list):
                    data_list = [data_list]

                if data_list:
                    def remove_html_tags(text):
                        if text is None:
                            return ''
                        return re.sub(r'</?b>', '', str(text))

                    for i, item in enumerate(data_list):
                        clean_title = remove_html_tags(item.get('ttl', '제목 없음')) 
                        clean_category = remove_html_tags(item.get('srvc_clsf_nm_path', '분류 정보 없음'))
                        clean_summary = remove_html_tags(item.get('cn', '상세 요약이 없습니다.'))
                        link = item.get('conts_link')
                        
                        st.markdown(f"### {i+1}. {clean_title}")
                        st.caption(f"분류: {clean_category}")
                        st.write(clean_summary)
                        
                        if link:
                            st.markdown(f"[🔗 에듀넷 상세 자료 바로가기]({link})")
                        st.markdown("---")
            else:
                st.warning(f"'{search_query}' 관련 자료가 에듀넷에서 검색되지 않았습니다. 다른 키워드(예: 수학 교육과정)를 시도해 보세요.")
                
        except KeyError as e:
            st.error(f"⚠️ 데이터 구조 오류: 필수 필드 '{e}'를 찾을 수 없습니다.")
            with st.expander("원본 로그 확인"):
                st.json(api_result)
        except Exception as e:
             st.error(f"알 수 없는 데이터 처리 오류: {e}")

st.divider()
st.caption("제공: 한국교육학술정보원(KERIS) 에듀넷·티클리어 API 기반")
