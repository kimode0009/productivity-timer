import time
import uuid
from datetime import date, datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="포모도로 + 할일 트래커", page_icon="🍅", layout="wide")

DURATIONS = {"work": 25 * 60, "short": 5 * 60, "long": 15 * 60}
LABELS = {"work": "집중 시간", "short": "짧은 휴식", "long": "긴 휴식"}
MODE_BUTTON_LABELS = {"work": "집중 25분", "short": "짧은 휴식 5분", "long": "긴 휴식 15분"}


def init_state():
    defaults = {
        "mode": "work",
        "running": False,
        "base_remaining": DURATIONS["work"],
        "start_ts": None,
        "todos": [],
        "active_task_id": None,
        "sessions": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_remaining():
    if st.session_state.running:
        elapsed = time.time() - st.session_state.start_ts
        return max(0, st.session_state.base_remaining - elapsed)
    return st.session_state.base_remaining


def fmt(seconds):
    seconds = int(seconds)
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def set_mode(mode):
    st.session_state.mode = mode
    st.session_state.running = False
    st.session_state.base_remaining = DURATIONS[mode]


def start():
    st.session_state.running = True
    st.session_state.start_ts = time.time()


def pause():
    st.session_state.base_remaining = get_remaining()
    st.session_state.running = False


def reset():
    st.session_state.running = False
    st.session_state.base_remaining = DURATIONS[st.session_state.mode]


def week_key(d: date):
    return f"{d.isocalendar().year}-w{d.isocalendar().week}"


def complete_session():
    st.session_state.running = False
    st.session_state.base_remaining = 0
    if st.session_state.mode == "work":
        today = date.today()
        st.session_state.sessions.append({"date": today, "task_id": st.session_state.active_task_id})
        if st.session_state.active_task_id:
            for t in st.session_state.todos:
                if t["id"] == st.session_state.active_task_id:
                    t["pomos"] += 1
    st.session_state.base_remaining = DURATIONS[st.session_state.mode]


init_state()

st.title("🍅 포모도로 + 할일 트래커")

col_timer, col_todo = st.columns([2, 3])

with col_timer:
    mode_cols = st.columns(3)
    for mode_col, mode_key in zip(mode_cols, DURATIONS):
        with mode_col:
            btn_type = "primary" if st.session_state.mode == mode_key else "secondary"
            if st.button(MODE_BUTTON_LABELS[mode_key], key=f"mode_{mode_key}", type=btn_type, use_container_width=True):
                set_mode(mode_key)
                st.rerun()

    remaining = get_remaining()
    if st.session_state.running and remaining <= 0:
        complete_session()
        remaining = get_remaining()
        st.rerun()

    st.markdown(f"<h1 style='text-align:center;font-size:56px;margin:12px 0 0;'>{fmt(remaining)}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;color:gray;margin:0 0 16px;'>{LABELS[st.session_state.mode]}</p>", unsafe_allow_html=True)
    st.progress(1 - (remaining / DURATIONS[st.session_state.mode]))

    start_col, reset_col = st.columns(2)
    with start_col:
        if st.button("일시정지" if st.session_state.running else "시작", type="primary", use_container_width=True):
            pause() if st.session_state.running else start()
            st.rerun()
    with reset_col:
        if st.button("리셋", use_container_width=True):
            reset()
            st.rerun()

    today = date.today()
    today_n = sum(1 for s in st.session_state.sessions if s["date"] == today)
    week_n = sum(1 for s in st.session_state.sessions if week_key(s["date"]) == week_key(today))
    days = {s["date"] for s in st.session_state.sessions}
    streak, cursor = 0, today
    while cursor in days:
        streak += 1
        cursor = date.fromordinal(cursor.toordinal() - 1)

    stat_cols = st.columns(3)
    stat_cols[0].metric("오늘 뽀모도로", today_n)
    stat_cols[1].metric("이번 주", week_n)
    stat_cols[2].metric("연속 일수", streak)

    if st.session_state.running:
        st_autorefresh(interval=1000, key="tick")

with col_todo:
    st.subheader("할 일 목록")

    with st.form("add_todo_form", clear_on_submit=True):
        new_todo = st.text_input("할 일을 입력하고 Enter", max_chars=80, label_visibility="collapsed")
        submitted = st.form_submit_button("+ 추가")
        if submitted and new_todo.strip():
            st.session_state.todos.insert(0, {
                "id": str(uuid.uuid4()),
                "text": new_todo.strip(),
                "done": False,
                "pomos": 0,
            })

    if st.session_state.active_task_id and not any(
        t["id"] == st.session_state.active_task_id for t in st.session_state.todos
    ):
        st.session_state.active_task_id = None

    if not st.session_state.todos:
        st.caption("아직 할 일이 없어요. 위에 입력해보세요.")
    else:
        options = ["없음"] + [t["text"] for t in st.session_state.todos]
        id_by_text = {t["text"]: t["id"] for t in st.session_state.todos}
        current_text = next((t["text"] for t in st.session_state.todos if t["id"] == st.session_state.active_task_id), "없음")
        chosen = st.selectbox("집중 대상", options, index=options.index(current_text), help="완료된 뽀모도로가 이 항목에 기록됩니다")
        st.session_state.active_task_id = id_by_text.get(chosen)

        for t in list(st.session_state.todos):
            row = st.columns([0.08, 0.58, 0.17, 0.17])
            done = row[0].checkbox("", value=t["done"], key=f"done_{t['id']}")
            if done != t["done"]:
                t["done"] = done
                st.rerun()
            label = f"~~{t['text']}~~" if t["done"] else t["text"]
            focus_mark = " 🎯" if t["id"] == st.session_state.active_task_id else ""
            row[1].markdown(label + focus_mark)
            if t["pomos"]:
                row[2].caption(f"🍅 {t['pomos']}")
            if row[3].button("삭제", key=f"del_{t['id']}"):
                st.session_state.todos = [x for x in st.session_state.todos if x["id"] != t["id"]]
                if st.session_state.active_task_id == t["id"]:
                    st.session_state.active_task_id = None
                st.rerun()

    st.caption("할 일을 **집중 대상**으로 지정하면 완료된 뽀모도로가 그 항목에 기록됩니다.")
