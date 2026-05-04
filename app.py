import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict

# ────────────────────────────────────────────
#  페이지 설정
# ────────────────────────────────────────────
st.set_page_config(
    page_title="CineTimeAtMega",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────
#  CSS 스타일
# ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 배경 */
.stApp {
    background: #0d0d0d;
    color: #f0f0f0;
}

/* 헤더 */
.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.main-header h1 {
    font-size: 2.2rem;
    font-weight: 900;
    color: #fff;
    letter-spacing: -1px;
    margin: 0;
}
.main-header span {
    color: #e63946;
}
.main-header p {
    color: #888;
    font-size: 0.9rem;
    margin-top: 0.3rem;
}

/* 섹션 카드 */
.section-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.section-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: #e63946;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}

/* 영화 카드 */
.movie-card {
    background: #111;
    border: 1px solid #222;
    border-left: 3px solid #e63946;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.movie-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.3rem;
}
.movie-meta {
    font-size: 0.78rem;
    color: #888;
    margin-bottom: 0.8rem;
}

/* 시간표 테이블 */
.schedule-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.schedule-table th {
    background: #1e1e1e;
    color: #aaa;
    font-weight: 500;
    padding: 0.5rem 0.8rem;
    text-align: left;
    border-bottom: 1px solid #2a2a2a;
    font-size: 0.75rem;
    letter-spacing: 1px;
}
.schedule-table td {
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid #1e1e1e;
    color: #ddd;
    vertical-align: middle;
}
.schedule-table tr:last-child td {
    border-bottom: none;
}
.schedule-table tr:hover td {
    background: #1a1a1a;
}

/* 예매 상태 배지 */
.badge-ok {
    display: inline-block;
    background: #1a472a;
    color: #4ade80;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
}
.badge-no {
    display: inline-block;
    background: #2a1a1a;
    color: #f87171;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* 지점 구분선 */
.branch-header {
    background: #1a1a1a;
    border-radius: 8px;
    padding: 0.7rem 1rem;
    margin: 1.5rem 0 0.8rem 0;
    font-size: 0.9rem;
    font-weight: 700;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* 버튼 */
.stButton > button {
    background: #e63946 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    padding: 0.6rem 2rem !important;
    width: 100%;
    font-size: 1rem !important;
    letter-spacing: 0.5px;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: #c1121f !important;
    transform: translateY(-1px);
}

/* 멀티셀렉트 */
.stMultiSelect > div {
    background: #1a1a1a !important;
    border-color: #2a2a2a !important;
}

/* 셀렉트박스 */
.stSelectbox > div > div {
    background: #1a1a1a !important;
    border-color: #2a2a2a !important;
    color: #f0f0f0 !important;
}

/* 라디오 */
.stRadio > div {
    gap: 0.5rem;
}

/* 구분선 */
hr {
    border-color: #2a2a2a;
}

/* 조회시각 */
.query-time {
    text-align: right;
    font-size: 0.75rem;
    color: #555;
    margin-top: 1rem;
}

/* 빈 결과 */
.empty-msg {
    text-align: center;
    color: #555;
    padding: 3rem;
    font-size: 0.95rem;
}

/* 잔여석 */
.seat-ok { color: #4ade80; font-weight: 600; }
.seat-no { color: #f87171; }

/* 모바일 대응 */
@media (max-width: 640px) {
    .main-header h1 { font-size: 1.6rem; }
    .schedule-table { font-size: 0.78rem; }
    .schedule-table th, .schedule-table td { padding: 0.45rem 0.5rem; }
}
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────
#  지점 목록
# ────────────────────────────────────────────
FAVORITES = [
    ("4651", "하남스타필드"),
    ("0084", "미사강변"),
    ("0019", "남양주현대아울렛 스페이스원 (다산)"),
    ("1029", "코엑스"),
    ("1030", "롯데월드"),
    ("1059", "판교"),
    ("1067", "일산"),
    ("7601", "수원"),
    ("1337", "북수원"),
    ("1005", "인천 송도"),
    ("1008", "대전 둔산"),
    ("1004", "대구 신세계"),
    ("1010", "부산 해운대"),
    ("1017", "센텀시티"),
    ("1022", "광주 하남"),
]
BRANCH_MAP  = {nm: no for no, nm in FAVORITES}
BRANCH_NAMES = [nm for _, nm in FAVORITES]


# ────────────────────────────────────────────
#  데이터 조회
# ────────────────────────────────────────────
def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.megabox.co.kr/",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.megabox.co.kr",
    }

@st.cache_data(ttl=300)  # 5분 캐시
def fetch_schedule(brch_no, play_de):
    url = "https://www.megabox.co.kr/on/oh/ohc/Brch/schedulePage.do"
    payload = {
        "masterType": "brch",
        "detailType": "area",
        "brchNo":  brch_no,
        "brchNo1": brch_no,
        "firstAt": "Y",
        "playDe":  play_de,
    }
    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        mega_map = data.get("megaMap", {})
        return (
            mega_map.get("movieFormList")
            or mega_map.get("scheduleList")
            or mega_map.get("brchSchdulList")
            or []
        )
    except Exception:
        return []


# ────────────────────────────────────────────
#  시간표 렌더링
# ────────────────────────────────────────────
def render_schedule(brch_nm, schedule_list, movie_filter):
    # 영화별 묶기
    movies = defaultdict(list)
    for item in schedule_list:
        nm = item.get("movieNm", "?")
        if movie_filter and movie_filter != "전체" and movie_filter not in nm:
            continue
        movies[nm].append(item)

    if not movies:
        st.markdown('<div class="empty-msg">해당 영화의 상영 정보가 없습니다.</div>',
                    unsafe_allow_html=True)
        return

    def rank_key(x):
        r = x[1][0].get("boxoRank")
        return r if r else 999

    for movie_nm, items in sorted(movies.items(), key=rank_key):
        first   = items[0]
        grade   = first.get("admisClassCdNm", "-")
        runtime = first.get("moviePlayTime", "-")
        rank    = first.get("boxoRank", "-")

        rows_html = ""
        for s in sorted(items, key=lambda x: x.get("playStartTime", "")):
            start  = s.get("playStartTime", "?")
            end    = s.get("playEndTime", "?")
            hall   = s.get("theabExpoNm", "?")
            kind   = s.get("playKindNm", "-")
            total  = s.get("totSeatCnt", "?")
            remain = s.get("restSeatCnt", "?")
            bokd   = s.get("bokdAbleAt", "N")

            badge  = '<span class="badge-ok">예매가능</span>' if bokd == "Y" \
                     else '<span class="badge-no">마감</span>'
            seat_cls = "seat-ok" if bokd == "Y" else "seat-no"

            rows_html += f"""
            <tr>
                <td><strong>{start}</strong></td>
                <td>{end}</td>
                <td>{hall}</td>
                <td>{kind}</td>
                <td class="{seat_cls}">{remain}<span style="color:#555">/{total}</span></td>
                <td>{badge}</td>
            </tr>"""

        st.markdown(f"""
        <div class="movie-card">
            <div class="movie-title">🎥 {movie_nm}</div>
            <div class="movie-meta">
                {grade} &nbsp;|&nbsp; {runtime}분 &nbsp;|&nbsp; 박스오피스 {rank}위
            </div>
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>시작</th><th>종료</th><th>상영관</th>
                        <th>상영타입</th><th>잔여/총</th><th>상태</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ────────────────────────────────────────────
#  메인 UI
# ────────────────────────────────────────────

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🎬 CineTime<span>AtMega</span></h1>
    <p>지점과 날짜를 선택하면 상영 시간표를 바로 조회합니다</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── 조회 설정 ──
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="section-title">📍 영화관 선택</div>', unsafe_allow_html=True)
    selected_names = st.multiselect(
        label="영화관",
        options=BRANCH_NAMES,
        default=["하남스타필드"],
        label_visibility="collapsed",
    )

with col2:
    st.markdown('<div class="section-title">📅 날짜 선택</div>', unsafe_allow_html=True)
    today = datetime.today()
    date_options = {}
    for i in range(7):
        d = today + timedelta(days=i)
        label = f"{d.strftime('%m/%d')} ({['월','화','수','목','금','토','일'][d.weekday()]})"
        if i == 0: label += " 오늘"
        if i == 1: label += " 내일"
        date_options[label] = d.strftime("%Y%m%d")

    selected_date_label = st.selectbox(
        label="날짜",
        options=list(date_options.keys()),
        label_visibility="collapsed",
    )
    play_de = date_options[selected_date_label]

# ── 조회 버튼 ──
st.markdown("")
if st.button("🔍  시간표 조회", use_container_width=True):
    if not selected_names:
        st.warning("영화관을 1개 이상 선택해 주세요.")
    else:
        # 데이터 수집
        all_data   = {}
        combined   = []
        errors     = []

        with st.spinner("데이터를 불러오는 중..."):
            for nm in selected_names:
                no   = BRANCH_MAP[nm]
                data = fetch_schedule(no, play_de)
                if data:
                    all_data[nm] = data
                    combined.extend(data)
                else:
                    errors.append(nm)

        if errors:
            st.warning(f"상영 정보를 가져오지 못한 지점: {', '.join(errors)}")

        if not combined:
            st.markdown('<div class="empty-msg">상영 정보가 없습니다.</div>',
                        unsafe_allow_html=True)
        else:
            # 영화 목록 추출
            seen = {}
            for item in combined:
                nm   = item.get("movieNm", "?")
                rank = item.get("boxoRank")
                if nm not in seen:
                    seen[nm] = rank
            movie_list = ["전체"] + [
                nm for nm, _ in sorted(seen.items(),
                key=lambda x: (x[1] if x[1] else 999))
            ]

            st.markdown("---")
            st.markdown('<div class="section-title">🎬 영화 선택</div>',
                        unsafe_allow_html=True)
            movie_filter = st.selectbox(
                "영화 선택",
                options=movie_list,
                label_visibility="collapsed",
            )

            st.markdown("---")

            # 지점별 결과 출력
            for brch_nm, data in all_data.items():
                st.markdown(
                    f'<div class="branch-header">📍 {brch_nm}</div>',
                    unsafe_allow_html=True,
                )
                render_schedule(brch_nm, data, movie_filter)

            st.markdown(
                f'<div class="query-time">조회 시각: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
                unsafe_allow_html=True,
            )
