import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import urllib.parse
import random
import requests

# ─────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="서울 나이트 스팟",
    page_icon="🌃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# 다크 모드 스타일
# ─────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #0d0d1a; color: #e0e0f0; }
  .block-container { padding-top: 1.5rem; }
  section[data-testid="stSidebar"] { background-color: #12122a; }
  .night-header {
    background: linear-gradient(135deg, #1a1a3e 0%, #0d0d1a 100%);
    border: 1px solid #3a3a6a;
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
  }
  .night-header h1 { color: #a78bfa; margin: 0; font-size: 2.2rem; }
  .night-header p { color: #94a3b8; margin: 0.4rem 0 0; font-size: 1rem; }
  .metric-card {
    background: #1a1a3e;
    border: 1px solid #3a3a6a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    margin-bottom: 0.5rem;
  }
  .metric-num { font-size: 2rem; font-weight: 700; color: #a78bfa; }
  .metric-label { font-size: 0.85rem; color: #94a3b8; margin-top: 0.2rem; }
  .spot-card {
    background: #1a1a3e;
    border: 1px solid #3a3a6a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
  }
  .spot-title { color: #c4b5fd; font-weight: 600; font-size: 1.05rem; }
  .spot-tag {
    display: inline-block;
    background: #2d2b55;
    color: #a78bfa;
    border-radius: 999px;
    padding: 2px 10px;
    font-size: 0.75rem;
    margin-right: 4px;
  }
  .spot-tag.free { background: #1e3a2f; color: #4ade80; }
  .spot-tag.paid { background: #3a1e1e; color: #f87171; }
  label { color: #c4b5fd !important; }
  .stMultiSelect [data-baseweb="tag"] { background-color: #3a3a6a; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 실시간 혼잡도 API
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def get_realtime_congestion(api_key: str) -> dict:
    AREA_NAMES = [
        "강남 MICE 관광특구", "동대문 관광특구", "명동 관광특구", "이태원 관광특구",
        "잠실 관광특구", "종로·청계 관광특구", "홍대 관광특구", "경복궁·서촌마을",
        "광화문·덕수궁", "창덕궁·종묘", "가산디지털단지역", "강남역", "건대입구역",
        "고속터미널역", "교대역", "구로디지털단지역", "서울역", "신촌·이대역",
        "여의도", "영등포 타임스퀘어", "왕십리역", "용산역", "혜화역",
        "DMC(디지털미디어시티)", "북촌한옥마을", "인사동·익선동", "낙산공원·이화마을",
        "남산공원", "서울숲공원", "월드컵공원", "올림픽공원", "뚝섬한강공원",
        "반포한강공원", "여의도한강공원", "이촌한강공원", "한강(잠실)",
    ]
    level_map = {"여유": "여유", "보통": "보통", "약간 붐빔": "붐빔", "붐빔": "붐빔"}
    congestion_dict = {}
    for area in AREA_NAMES:
        try:
            encoded_area = urllib.parse.quote(area)
            url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/citydata/1/1/{encoded_area}"
            response = requests.get(url, timeout=10)
            data = response.json()
ppltn_list = data.get("CITYDATA", {}).get("LIVE_PPLTN_STTS", [])
if not ppltn_list:
    congestion_dict[area] = "보통"
    continue

level = ppltn_list[0].get("AREA_CONGEST_LVL", "").strip()
congestion_dict[area] = level_map.get(level, "보통")
        except Exception:
            congestion_dict[area] = "보통"
    return congestion_dict

# ─────────────────────────────────────────
# Unsplash 이미지
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_place_image(place_name: str, unsplash_key: str) -> str:
    try:
        query = urllib.parse.quote(place_name + " 서울 야경")
        url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&orientation=landscape"
        headers = {"Authorization": f"Client-ID {unsplash_key}"}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        results = data.get("results", [])
        if results:
            return results[0]["urls"]["small"]
    except Exception:
        pass
    return ""

# ─────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/seoul_nightspot.csv")
    try:
        API_KEY = st.secrets["SEOUL_API_KEY"]
        congestion_dict = get_realtime_congestion(API_KEY)
        def match_congestion(place_name):
            for api_name, level in congestion_dict.items():
                if any(k in place_name for k in api_name.split("·")) or \
                   any(k in api_name for k in place_name.split()):
                    return level
            return "보통"
        df["혼잡도"] = df["장소명"].apply(match_congestion)
    except Exception:
        random.seed(42)
        df["혼잡도"] = [random.choice(["여유", "여유", "보통", "붐빔"]) for _ in range(len(df))]
    df["혼잡도_점수"] = df["혼잡도"].map({"여유": 1, "보통": 2, "붐빔": 3})
    df["주차가능"] = df["주차안내"].notna() & (df["주차안내"].str.strip() != "")
    return df

# ─────────────────────────────────────────
# ✅ df 호출은 딱 한 번만
# ─────────────────────────────────────────
df = load_data()

# ─────────────────────────────────────────
# 🔧 임시 디버그 — API 응답 확인용 (확인 후 삭제)
# ─────────────────────────────────────────
with st.expander("🔧 API 디버그 (확인 후 삭제 예정)", expanded=True):
    try:
        API_KEY = st.secrets["SEOUL_API_KEY"]
        st.write("✅ API 키 로드 성공:", API_KEY[:6] + "****")

        test_area = "남산공원"
        encoded = urllib.parse.quote(test_area)
        url = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/citydata/1/1/{encoded}"
        st.write("📡 요청 URL:", url.replace(API_KEY, "****"))

        r = requests.get(url, timeout=10)
        st.write("📶 상태코드:", r.status_code)
        st.json(r.json())

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

# ─────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────
st.markdown("""
<div class="night-header">
  <h1>🌃 서울 나이트 스팟</h1>
  <p>예쁜 곳보다 <b>지금 가기 좋은 곳</b>을 추천합니다.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 사이드바 필터
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 필터")
    congestion_filter = st.multiselect("혼잡도", options=["여유", "보통", "붐빔"], default=["여유", "보통"])
    categories = df["분류"].dropna().unique().tolist()
    category_filter = st.multiselect("분류", options=categories, default=categories)
    fee_filter = st.multiselect("요금", options=["무료", "유료"], default=["무료", "유료"])
    parking_only = st.checkbox("주차 가능한 곳만 보기", value=False)
    st.markdown("---")
    st.markdown("#### 📌 정렬 기준")
    sort_by = st.radio("", options=["혼잡도 낮은 순", "이름 가나다 순"], index=0, label_visibility="collapsed")
    st.markdown("---")
    st.caption("⚠️ 혼잡도는 서울시 실시간 인구 API 기준이며 5분마다 갱신됩니다.")

# ─────────────────────────────────────────
# 필터 적용
# ─────────────────────────────────────────
filtered = df[
    df["혼잡도"].isin(congestion_filter) &
    df["분류"].isin(category_filter) &
    df["유무료구분"].isin(fee_filter)
]
if parking_only:
    filtered = filtered[filtered["주차가능"] == True]
if sort_by == "혼잡도 낮은 순":
    filtered = filtered.sort_values("혼잡도_점수")
else:
    filtered = filtered.sort_values("장소명")

# ─────────────────────────────────────────
# 상단 요약 메트릭
# ─────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(filtered)}</div><div class="metric-label">검색된 명소</div></div>', unsafe_allow_html=True)
with c2:
    n_ease = len(filtered[filtered["혼잡도"] == "여유"])
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#4ade80">{n_ease}</div><div class="metric-label">🟢 지금 여유로운 곳</div></div>', unsafe_allow_html=True)
with c3:
    n_free_fee = len(filtered[filtered["유무료구분"] == "무료"])
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#60a5fa">{n_free_fee}</div><div class="metric-label">💙 무료 입장</div></div>', unsafe_allow_html=True)
with c4:
    n_park = len(filtered[filtered["주차가능"] == True])
    st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#f9a8d4">{n_park}</div><div class="metric-label">🅿️ 주차 가능</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 지도 + 목록 (2컬럼)
# ─────────────────────────────────────────
col_map, col_list = st.columns([3, 2])

with col_map:
    st.markdown("#### 🗺️ 야경 명소 지도")
    color_map = {"여유": "green", "보통": "orange", "붐빔": "red"}
    icon_map  = {"여유": "star", "보통": "info-sign", "붐빔": "warning-sign"}
    m = folium.Map(location=[37.55, 126.99], zoom_start=12, tiles="CartoDB dark_matter")

    try:
        UNSPLASH_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]
    except Exception:
        UNSPLASH_KEY = ""

    for _, row in filtered.iterrows():
        try:
            lat, lon = float(row["위도"]), float(row["경도"])
        except Exception:
            continue
        if UNSPLASH_KEY:
            img_url = get_place_image(row["장소명"], UNSPLASH_KEY)
            img_tag = f"<img src='{img_url}' style='width:100%;border-radius:6px;margin-bottom:6px'>" if img_url else ""
        else:
            img_tag = ""
        congestion_color = "green" if row["혼잡도"] == "여유" else "orange" if row["혼잡도"] == "보통" else "red"
        popup_html = f"""
        <div style='font-family:sans-serif;min-width:180px;max-width:220px'>
          {img_tag}
          <b style='font-size:14px'>{row['장소명']}</b><br>
          <span style='color:{congestion_color}'>● {row['혼잡도']}</span><br>
          <small>{row['분류']} · {row['유무료구분']}</small><br>
          <small style='color:#666'>{str(row['운영시간'])[:40] if pd.notna(row['운영시간']) else ''}</small>
        </div>"""
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=240),
            tooltip=row["장소명"],
            icon=folium.Icon(color=color_map[row["혼잡도"]], icon=icon_map[row["혼잡도"]], prefix="glyphicon"),
        ).add_to(m)
    st_folium(m, width="100%", height=500, returned_objects=[])
    st.markdown("<div style='display:flex;gap:20px;margin-top:8px;font-size:0.85rem'><span>🟢 여유</span><span>🟡 보통</span><span>🔴 붐빔</span></div>", unsafe_allow_html=True)

with col_list:
    st.markdown("#### 📋 명소 목록")
    if filtered.empty:
        st.info("조건에 맞는 명소가 없습니다. 필터를 조정해보세요.")
    else:
        congestion_emoji = {"여유": "🟢", "보통": "🟡", "붐빔": "🔴"}
        for _, row in filtered.head(20).iterrows():
            emoji = congestion_emoji.get(row["혼잡도"], "⚪")
            fee_icon = "💚 무료" if row["유무료구분"] == "무료" else "💳 유료"
            parking = "🅿️ 주차가능" if row["주차가능"] else ""
            hours = str(row["운영시간"])[:50] if pd.notna(row["운영시간"]) else "운영시간 정보 없음"
            with st.container(border=True):
                st.markdown(f"**{row['장소명']}**")
                st.caption(f"{emoji} {row['혼잡도']}  |  {row['분류']}  |  {fee_icon}  {parking}")
                st.caption(f"🕐 {hours}")

# ─────────────────────────────────────────
# 상세 정보
# ─────────────────────────────────────────
st.markdown("---")
st.markdown("#### 🔎 장소 상세 정보")
selected_name = st.selectbox(
    "장소 선택",
    options=filtered["장소명"].tolist() if not filtered.empty else df["장소명"].tolist(),
    label_visibility="collapsed"
)
selected = df[df["장소명"] == selected_name].iloc[0]
with st.expander(f"📍 {selected_name} 상세보기", expanded=True):
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f"**주소:** {selected['주소']}")
        st.markdown(f"**분류:** {selected['분류']}")
        st.markdown(f"**요금:** {selected['유무료구분']} ({selected['이용요금'] if pd.notna(selected['이용요금']) else '정보 없음'})")
        st.markdown(f"**운영시간:** {selected['운영시간'] if pd.notna(selected['운영시간']) else '정보 없음'}")
    with d2:
        st.markdown(f"**전화번호:** {selected['전화번호'] if pd.notna(selected['전화번호']) else '정보 없음'}")
        st.markdown(f"**지하철:** {selected['지하철'] if pd.notna(selected['지하철']) else '정보 없음'}")
        st.markdown(f"**버스:** {selected['버스'] if pd.notna(selected['버스']) else '정보 없음'}")
        st.markdown(f"**주차:** {selected['주차안내'] if pd.notna(selected['주차안내']) else '주차 정보 없음'}")
    if pd.notna(selected.get("홈페이지 URL")):
        st.markdown(f"🔗 [공식 홈페이지]({selected['홈페이지 URL']})")
