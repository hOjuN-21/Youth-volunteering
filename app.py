import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# 페이지 설정
st.set_page_config(page_title="청소년 자원봉사 알리미", page_icon="🔔", layout="wide")

# 안전한 API 키 불러오기 (Streamlit Secrets 활용)
# 로컬에서는 .streamlit/secrets.toml 에서, 클라우드에서는 Settings -> Secrets 에서 가져옵니다.
try:
    API_KEY = st.secrets["API_KEY"]
except KeyError:
    st.error("API 키가 설정되지 않았습니다. 환경변수(Secrets) 설정을 확인해 주세요.")
    st.stop()

st.title("🔔 청소년 맞춤형 자원봉사 실시간 알리미")
st.write("1365 자원봉사포털의 실시간 공공데이터를 기반으로 조회합니다.")

# 사이드바 설정
st.sidebar.header("🔍 검색 및 필터 조건")
selected_region = st.sidebar.selectbox("지역 선택", ["전체", "순천시", "광양시", "진주시"])

include_adult = st.sidebar.checkbox("성인 동반 가능 봉사 포함", value=True)
include_blood = st.sidebar.checkbox("헌혈 봉사 포함", value=True)
include_online = st.sidebar.checkbox("비대면/온라인 봉사 포함", value=True)

@st.cache_data(ttl=3600) # 1시간마다 데이터 갱신
def fetch_volunteer_data(keyword):
    """공공데이터 API를 호출하여 봉사활동 목록을 가져오는 함수"""
    url = "https://apis.data.go.kr/1741000/volunteerPartcptnService/getVltrPartcptnItem"
    
    # API 요청 매개변수
    params = {
        'serviceKey': API_KEY,
        'numOfRows': '50',  # 한 번에 가져올 데이터 수
        'pageNo': '1',
        'keyword': keyword  # 지역명 등으로 검색
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # XML 데이터 파싱
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        data = []
        for item in items:
            # 안전하게 태그 값을 추출하는 내부 함수
            def get_text(tag):
                element = item.find(tag)
                return element.text if element is not None else ""
                
            data.append({
                "봉사명": get_text('progrmSj'),
                "활동개요": get_text('progrmCn'),
                "지역": get_text('nanmmbyNm'),
                "신청기간": f"{get_text('progrmBgnde')} ~ {get_text('progrmEndde')}",
                "활동기간": f"{get_text('actBeginTm')} ~ {get_text('actEndTm')}",
                "모집상태": get_text('progrmSttusSe'),
                "성인참여": get_text('adultPosblAt'),
                "청소년참여": get_text('yngbgsPosblAt'),
                "url": f"https://www.1365.go.kr/vols/1572247904127/partcptn/timeCptn.do?type=show&progrmRegistNo={get_text('progrmRegistNo')}"
            })
        return data
    except Exception as e:
        st.sidebar.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return []

# 데이터 로딩 스피너
with st.spinner("실시간 1365 데이터를 불러오는 중입니다..."):
    # 선택된 지역에 따라 API 검색어 설정
    search_keywords = ["순천", "광양", "진주"] if selected_region == "전체" else [selected_region[:2]]
    
    all_data = []
    for kw in search_keywords:
        all_data.extend(fetch_volunteer_data(kw))
        
    df = pd.DataFrame(all_data)

if not df.empty:
    # --- 데이터 필터링 로직 ---
    # 1. 청소년 참여 가능한 것만 기본적으로 필터링 (청소년참여 == 'Y')
    filtered_df = df[df['청소년참여'] == 'Y'].copy()
    
    # 2. 조건부 필터링
    if not include_adult:
        filtered_df = filtered_df[filtered_df['성인참여'] != 'Y']
        
    if not include_blood:
        filtered_df = filtered_df[~filtered_df['봉사명'].str.contains('헌혈')]
        
    if not include_online:
        filtered_df = filtered_df[~filtered_df['봉사명'].str.contains('비대면|온라인')]

    # --- 결과 출력 ---
    st.write(f"### 📋 실시간 검색 결과 (총 {len(filtered_df)}건)")
    
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"#### 📍 [{row['지역']}] {row['봉사명']}")
            st.write(f"**💡 활동상세:** {row['활동개요'][:100]}...") # 너무 길면 자름
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"📅 **신청기간:** {row['신청기간']}")
            with col2:
                st.write(f"⏰ **활동시간:** {row['활동기간']}")
                
            st.markdown(f"[🔗 1365 신청 페이지 바로가기]({row['url']})")
            st.write("---")
else:
    st.warning("현재 해당 지역에 모집 중인 봉사활동 데이터가 없거나, API 응답이 지연되고 있습니다.")