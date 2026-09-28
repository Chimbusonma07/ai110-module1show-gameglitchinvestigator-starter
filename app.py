import random
import streamlit as st

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

# FIX: deleted the duplicated check_guess, get_range_for_difficulty and
# update_score that shadowed logic_utils.py, so the app and the tests now
# exercise one shared definition of each.

st.set_page_config(
    page_title="Glitchy Guesser",
    page_icon="🎮",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Styling. Cards are translucent grey rather than a fixed colour so the whole
# sheet reads correctly on both the light and dark Streamlit themes.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .gg-hero {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 55%, #d946ef 100%);
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.28);
      }
      .gg-hero h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 0.3rem 0;
        line-height: 1.15;
      }
      .gg-hero p {
        color: rgba(255, 255, 255, 0.85);
        font-size: 0.95rem;
        margin: 0;
      }

      .gg-card {
        background: rgba(128, 128, 128, 0.09);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 1rem;
      }
      .gg-card-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        opacity: 0.62;
        margin-bottom: 0.25rem;
      }
      .gg-card-value {
        font-size: 1.45rem;
        font-weight: 700;
        line-height: 1.2;
      }

      .gg-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.2rem 0 0.4rem 0;
      }
      .gg-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        font-variant-numeric: tabular-nums;
        border: 1px solid transparent;
      }
      .gg-pill-high {
        background: rgba(239, 68, 68, 0.14);
        border-color: rgba(239, 68, 68, 0.4);
        color: #ef4444;
      }
      .gg-pill-low {
        background: rgba(59, 130, 246, 0.14);
        border-color: rgba(59, 130, 246, 0.4);
        color: #3b82f6;
      }
      .gg-pill-win {
        background: rgba(34, 197, 94, 0.16);
        border-color: rgba(34, 197, 94, 0.45);
        color: #22c55e;
      }

      .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 0.5rem 0.9rem;
        transition: transform 0.08s ease, box-shadow 0.15s ease;
        width: 100%;
      }
      .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 16px rgba(99, 102, 241, 0.25);
      }

      .gg-empty {
        opacity: 0.5;
        font-size: 0.88rem;
        font-style: italic;
      }
      .gg-foot {
        text-align: center;
        opacity: 0.45;
        font-size: 0.8rem;
        margin-top: 1.2rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="gg-hero">
      <h1>🎮 Game Glitch Investigator</h1>
      <p>An AI-generated guessing game. Something is off.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.header("⚙️ Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

difficulty_blurb = {
    "Easy": "🟢 A small range and plenty of tries.",
    "Normal": "🟡 The standard game.",
    "Hard": "🔴 A wider range and fewer tries.",
}
st.sidebar.caption(difficulty_blurb[difficulty])

side_a, side_b = st.sidebar.columns(2)
side_a.metric("Range", f"{low}–{high}")
side_b.metric("Tries", attempt_limit)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    # FIX: started at 1, so the first game had one fewer attempt than any game
    # started with New Game (which resets to 0) and the banner showed one
    # attempt already spent before the player had guessed.
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.pop("just_started", False):
    st.toast("New game started 🔁")

attempts_left = attempt_limit - st.session_state.attempts

# ---------------------------------------------------------------------------
# Scoreboard
# ---------------------------------------------------------------------------
stat_1, stat_2, stat_3 = st.columns(3)

with stat_1:
    st.markdown(
        f'<div class="gg-card"><div class="gg-card-label">Score</div>'
        f'<div class="gg-card-value">{st.session_state.score}</div></div>',
        unsafe_allow_html=True,
    )
with stat_2:
    st.markdown(
        f'<div class="gg-card"><div class="gg-card-label">Attempts left</div>'
        f'<div class="gg-card-value">{attempts_left} / {attempt_limit}</div></div>',
        unsafe_allow_html=True,
    )
with stat_3:
    # FIX: the banner hardcoded "1 and 100", which was wrong on Easy (1-20) and
    # Hard (1-50) and contradicted the range validation in parse_guess.
    st.markdown(
        f'<div class="gg-card"><div class="gg-card-label">Range</div>'
        f'<div class="gg-card-value">{low} – {high}</div></div>',
        unsafe_allow_html=True,
    )

st.progress(
    min(st.session_state.attempts / attempt_limit, 1.0),
    text=f"Guess a number between {low} and {high}",
)

# ---------------------------------------------------------------------------
# Guess history
# ---------------------------------------------------------------------------
st.markdown("##### 🧾 Your guesses")

if st.session_state.history:
    pills = []
    for past in st.session_state.history:
        if past == st.session_state.secret:
            style, arrow = "gg-pill-win", "✓"
        elif past > st.session_state.secret:
            style, arrow = "gg-pill-high", "▼"
        else:
            style, arrow = "gg-pill-low", "▲"
        pills.append(f'<span class="gg-pill {style}">{past} {arrow}</span>')

    st.markdown(
        '<div class="gg-pills">' + "".join(pills) + "</div>",
        unsafe_allow_html=True,
    )
    st.caption("▼ too high · ▲ too low")
else:
    st.markdown(
        '<div class="gg-empty">No guesses yet — the board is clean.</div>',
        unsafe_allow_html=True,
    )

st.divider()

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}",
    placeholder=f"A whole number from {low} to {high}…",
)

col1, col2, col3 = st.columns([2, 2, 3])
with col1:
    submit = st.button("Submit Guess 🚀", type="primary", use_container_width=True)
with col2:
    new_game = st.button("New Game 🔁", use_container_width=True)
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    # FIX: New Game reset only attempts and secret, so status stayed "won" or
    # "lost" and the rerun fell straight into the st.stop() guard below - the
    # button was dead once a round ended. Every per-game key resets now.
    st.session_state.attempts = 0
    # FIX: was randint(1, 100), so a new game on Easy or Hard could pick a
    # secret outside the advertised range - and therefore outside the set of
    # guesses parse_guess will accept, making the game unwinnable.
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0
    st.session_state.history = []
    st.session_state.status = "playing"
    # FIX: st.success() here never rendered, because st.rerun() discards the
    # current page before it paints. The confirmation is deferred to the next
    # run instead, where it actually reaches the player.
    st.session_state.just_started = True
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("🏆 You already won. Start a new game to play again.")
    else:
        st.error("💀 Game over. Start a new game to try again.")

    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: invalid or blank input no longer costs an attempt, and is not
        # recorded in history. Only a successfully parsed guess counts.
        st.error(err, icon="🚫")
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: on every other attempt the secret was cast to str, so check_guess
        # compared int to str and fell back to lexicographic order ("9" > "50"),
        # inverting the hint. The secret stays an int now.
        outcome, message = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(message, icon="🧭")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"🎉 You won! The secret was **{st.session_state.secret}**. "
                f"Final score: **{st.session_state.score}**",
                icon="🏆",
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was **{st.session_state.secret}**. "
                    f"Score: **{st.session_state.score}**",
                    icon="💀",
                )

with st.expander("🛠️ Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

st.markdown(
    '<div class="gg-foot">Built by an AI that claims this code is production-ready.</div>',
    unsafe_allow_html=True,
)
