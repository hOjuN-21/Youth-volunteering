import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="청소년 자원봉사 알리미", page_icon="🔔", layout="wide")

# 헤더 영역
st.title("🔔 청소년 맞춤형 자원봉사 알리미 웹앱")
st.write("순천시, 광양시, 진주시 지역의 청소년 참여 가능 봉사활동을 확인하는 대시보드입니다.")

# 사이드바 설정
st.sidebar.header("🔍 검색 및 필터 조건")
selected_region = st.sidebar.selectbox("지역 선택", ["전체", "전라남도 순천시", "전라남도 광양시", "경상남도 진주시"])

# 필터 옵션
include_adult = st.sidebar.checkbox("성인 동반 가능 봉사 포함", value=True)
include_blood = st.sidebar.checkbox("헌혈 봉사 포함", value=True)
include_online = st.sidebar.checkbox("비대면/온라인 봉사 포함", value=True)

# 샘플 데이터 로드 (추후 크롤링 및 API 데이터 연동 영역)
@st.cache_data
def load_sample_data():
    data = [
        {
            "지역": "경상남도 진주시",
            "봉사명": "[진주시 평거동] 주말 남강 고수부지 환경정화 캠페인",
            "활동개요": "남강 고수부지 및 주변 상가 쓰레기 수거 및 청소년 유해환경 개선 캠페인",
            "신청기간": "2026-05-25 ~ 2026-06-05",
            "봉사활동 날짜": "2026-06-06",
            "봉사시간": "2시간 (10:00 ~ 12:00)",
            "유형": "성인동반가능",
            "웹주소": "https://www.1365.go.kr/vols/1572247904127/partcptn/timeCptn.do"
        },
        {
            "지역": "전라남도 순천시",
            "봉사명": "순천만국가정원 주말 관람객 동선 안내 및 환경정리",
            "활동개요": "국가정원 내 관람객 안내, 유모차 대여소 업무 지원 및 주변 정화",
            "신청기간": "2026-05-20 ~ 2026-06-12",
            "봉사활동 날짜": "2026-06-13",
            "봉사시간": "4시간 (13:00 ~ 17:00)",
            "유형": "청소년전용",
            "웹주소": "https://www.1365.go.kr/vols/1572247904127/partcptn/timeCptn.do"
        },
        {
            "지역": "전라남도 순천시",
            "봉사명": "[헌혈] 생명나눔 헌혈 봉사활동 (순천 헌혈의집)",
            "활동개요": "순천 헌혈의 집 방문 및 헌혈 참여 (헌혈증서 지참 시 실적 연계)",
            "신청기간": "상시모집",
            "봉사활동 날짜": "상시",
            "봉사시간": "4시간 인정",
            "유형": "헌혈",
            "웹주소": "https://www.1365.go.kr/vols/1572247904127/partcptn/timeCptn.do"
        },
        {
            "지역": "전라남도 광양시",
            "봉사명": "[비대면/온라인] 시각장애인을 위한 점자도서 타이핑 봉사",
            "활동개요": "배정된 도서를 자택 및 기숙사에서 PC로 타이핑하여 제출하는 온라인 활동",
            "신청기간": "2026-06-01 ~ 2026-06-10",
            "봉사활동 날짜": "2026-06-01 ~ 2026-06-14",
            "봉사시간": "건당 2시간 인정",
            "유형": "비대면",
            "웹주소": "https://www.1365.go.kr/vols/1572247904127/partcptn/timeCptn.do"
        }
    ]
    return pd.DataFrame(data)

df = load_sample_data()

# 필터링 로직 적용
filtered_df = df.copy()

if selected_region != "전체":
    filtered_df = filtered_df[filtered_df["지역"] == selected_region]

# 유형 필터링 목록 구축
types_to_include = ["청소년전용"]
if include_adult:
    types_to_include.append("성인동반가능")
if include_blood:
    types_to_include.append("헌혈")
if include_online:
    types_to_include.append("비대면")

filtered_df = filtered_df[filtered_df["유형"].isin(types_to_include)]

# 결과 대시보드 출력
st.write(f"### 📋 검색 결과 (총 {len(filtered_df)}건)")

if not filtered_df.empty:
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.markdown(f"#### 📍 [{row['지역']}] {row['봉사명']}")
            st.write(f"**💡 활동개요:** {row['활동개요']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"📅 **신청기간:** {row['신청기간']}")
            with col2:
                st.write(f"⏰ **봉사일시:** {row['봉사활동 날짜']}")
            with col3:
                st.write(f"⏳ **봉사시간:** {row['봉사시간']}")
            
            st.markdown(f"[🔗 1365 신청 페이지 바로가기]({row['웹주소']})")
            st.write("---")
else:
    st.warning("선택하신 조건에 맞는 봉사활동이 없습니다. 필터를 조정해 보세요.")