import streamlit as st
import requests
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict

KST = timezone(timedelta(hours=9))

# ────────────────────────────────────────────
#  페이지 설정
# ────────────────────────────────────────────
st.set_page_config(
    page_title="CineTimeAtMega",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────
#  CSS 스타일
# ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.stApp { background: #0d0d0d; color: #f0f0f0; }

.main-header { text-align: center; padding: 2rem 0 1rem 0; }
.main-header h1 { font-size: 2.2rem; font-weight: 900; color: #fff; letter-spacing: -1px; margin: 0; }
.main-header span { color: #e63946; }
.main-header p { color: #888; font-size: 0.9rem; margin-top: 0.3rem; }

.section-title {
    font-size: 0.75rem; font-weight: 700; color: #e63946;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.8rem;
}

/* 영화 목록 카드 */
.movie-list-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
}
.movie-list-card:hover { border-color: #e63946; background: #1f1f1f; }
.movie-list-title { font-size: 1rem; font-weight: 700; color: #fff; }
.movie-list-meta { font-size: 0.78rem; color: #888; margin-top: 0.2rem; }
.rank-badge {
    display: inline-block; background: #e63946; color: #fff;
    border-radius: 4px; padding: 1px 7px; font-size: 0.72rem;
    font-weight: 700; margin-right: 6px;
}

/* 시간표 테이블 */
.schedule-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.schedule-table th {
    background: #1e1e1e; color: #aaa; font-weight: 500;
    padding: 0.5rem 0.8rem; text-align: left;
    border-bottom: 1px solid #2a2a2a; font-size: 0.75rem; letter-spacing: 1px;
}
.schedule-table td {
    padding: 0.6rem 0.8rem; border-bottom: 1px solid #1e1e1e;
    color: #ddd; vertical-align: middle;
}
.schedule-table tr:last-child td { border-bottom: none; }
.schedule-table tr:hover td { background: #1a1a1a; }

/* 예매 링크 버튼 */
.book-btn {
    display: inline-block;
    background: #e63946;
    color: #fff !important;
    border-radius: 5px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    text-decoration: none !important;
    white-space: nowrap;
}
.book-btn:hover { background: #c1121f; }
.book-btn-disabled {
    display: inline-block;
    background: #2a2a2a;
    color: #666 !important;
    border-radius: 5px;
    padding: 3px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    text-decoration: none !important;
    white-space: nowrap;
}

/* 지점 헤더 */
.branch-header {
    background: #1a1a1a; border-radius: 8px;
    padding: 0.7rem 1rem; margin: 1.5rem 0 0.8rem 0;
    font-size: 0.9rem; font-weight: 700; color: #fff;
}

/* 버튼 */
.stButton > button {
    background: #e63946 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-family: 'Noto Sans KR', sans-serif !important;
    padding: 0.6rem 2rem !important; width: 100%;
    font-size: 1rem !important; letter-spacing: 0.5px; transition: all 0.2s;
}
.stButton > button:hover { background: #c1121f !important; transform: translateY(-1px); }

/* 검색창 */
.stTextInput > div > div > input {
    background: #1a1a1a !important; border-color: #2a2a2a !important;
    color: #f0f0f0 !important; border-radius: 8px !important;
}

.stMultiSelect > div { background: #1a1a1a !important; border-color: #2a2a2a !important; }
.stSelectbox > div > div { background: #1a1a1a !important; border-color: #2a2a2a !important; color: #f0f0f0 !important; }

hr { border-color: #2a2a2a; }

.query-time { text-align: right; font-size: 0.75rem; color: #555; margin-top: 1rem; }
.empty-msg { text-align: center; color: #555; padding: 3rem; font-size: 0.95rem; }
.seat-ok { color: #4ade80; font-weight: 600; }
.seat-no { color: #f87171; }

/* expander 스타일 */
.streamlit-expanderHeader {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-weight: 700 !important;
}
.streamlit-expanderHeader p {
    color: #fff !important;
    font-weight: 700 !important;
}
.streamlit-expanderHeader svg {
    fill: #fff !important;
    stroke: #fff !important;
}
.streamlit-expanderContent {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-top: none !important;
}
/* Streamlit 최신버전 expander 대응 */
[data-testid="stExpander"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    margin-bottom: 0.5rem;
}
[data-testid="stExpander"] summary {
    color: #fff !important;
    font-weight: 700 !important;
    background: #1a1a1a !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #fff !important;
    font-weight: 700 !important;
}

@media (max-width: 640px) {
    .main-header h1 { font-size: 1.6rem; }
    .schedule-table { font-size: 0.75rem; }
    .schedule-table th, .schedule-table td { padding: 0.4rem 0.4rem; }
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
BRANCH_MAP   = {nm: no for no, nm in FAVORITES}
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

@st.cache_data(ttl=300)
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
#  예매 URL 생성
# ────────────────────────────────────────────
def make_booking_url(item):
    """메가박스 영화 상세 페이지 URL 생성"""
    movie_no = item.get("rpstMovieNo") or item.get("movieNo", "")
    if movie_no:
        return f"https://www.megabox.co.kr/movie/detail?movieNo={movie_no}"
    return ""


# ────────────────────────────────────────────
#  시간표 렌더링 (아코디언)
# ────────────────────────────────────────────
def render_schedule(brch_nm, schedule_list, search_keyword):
    # 영화별 묶기
    movies = defaultdict(list)
    for item in schedule_list:
        nm = item.get("movieNm", "?")
        # 검색어 필터
        if search_keyword and search_keyword.strip():
            if search_keyword.strip() not in nm:
                continue
        movies[nm].append(item)

    if not movies:
        st.markdown('<div class="empty-msg">검색 결과가 없습니다.</div>',
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
        rank_txt = f"#{rank}" if rank and rank != "-" else ""

        # 예매 가능한 회차 수 카운트
        avail_cnt = sum(1 for s in items if s.get("bokdAbleAt") == "Y")

        # 아코디언 헤더 레이블
        label = f"{rank_txt}  {movie_nm}  |  {grade}  {runtime}분  |  예매가능 {avail_cnt}회"

        with st.expander(label, expanded=(search_keyword.strip() != "")):
            rows_html = ""
            for s in sorted(items, key=lambda x: x.get("playStartTime", "")):
                start  = s.get("playStartTime", "?")
                end    = s.get("playEndTime", "?")
                hall   = s.get("theabExpoNm", "?")
                kind   = s.get("playKindNm", "-")
                total  = s.get("totSeatCnt", "?")
                remain = s.get("restSeatCnt", "?")
                bokd   = s.get("bokdAbleAt", "N")
                seat_cls = "seat-ok" if bokd == "Y" else "seat-no"

                # 예매 버튼
                booking_url = make_booking_url(s)
                if bokd == "Y" and booking_url:
                    btn = f'<a href="{booking_url}" target="_blank" class="book-btn">예매하기</a>'
                else:
                    btn = '<span class="book-btn-disabled">마감</span>'

                rows_html += f"""
                <tr>
                    <td><strong>{start}</strong></td>
                    <td>{end}</td>
                    <td>{hall}</td>
                    <td>{kind}</td>
                    <td class="{seat_cls}">{remain}<span style="color:#555">/{total}</span></td>
                    <td>{btn}</td>
                </tr>"""

            st.markdown(f"""
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>시작</th><th>종료</th><th>상영관</th>
                        <th>상영타입</th><th>잔여/총</th><th>예매</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)


# ────────────────────────────────────────────
#  메인 UI
# ────────────────────────────────────────────
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
    today = datetime.now(KST)
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

# ── 영화 검색 ──
st.markdown('<div class="section-title" style="margin-top:1rem;">🔎 영화 검색 (선택사항)</div>',
            unsafe_allow_html=True)
search_keyword = st.text_input(
    label="영화 검색",
    placeholder="영화 제목 입력 시 해당 영화만 표시 (비워두면 전체)",
    label_visibility="collapsed",
)

# ── 조회 버튼 ──
st.markdown("")
if st.button("🔍  시간표 조회", use_container_width=True):
    if not selected_names:
        st.warning("영화관을 1개 이상 선택해 주세요.")
    else:
        all_data = {}
        errors   = []

        with st.spinner("데이터를 불러오는 중..."):
            for nm in selected_names:
                no   = BRANCH_MAP[nm]
                data = fetch_schedule(no, play_de)
                if data:
                    all_data[nm] = data
                else:
                    errors.append(nm)

        if errors:
            st.warning(f"상영 정보를 가져오지 못한 지점: {', '.join(errors)}")

        if not all_data:
            st.markdown('<div class="empty-msg">상영 정보가 없습니다.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown("---")

            for brch_nm, data in all_data.items():
                st.markdown(
                    f'<div class="branch-header">📍 {brch_nm}</div>',
                    unsafe_allow_html=True,
                )
                render_schedule(brch_nm, data, search_keyword)

            st.markdown(
                f'<div class="query-time">조회 시각: {datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")}</div>',
                unsafe_allow_html=True,
            )
