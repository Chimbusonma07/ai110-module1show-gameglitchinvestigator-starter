import pytest

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

# FIX: check_guess returns a (outcome, message) tuple, so comparing the whole
# result to "Win" could never pass. These three now unpack it and assert on the
# outcome, matching how app.py consumes the function.

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"


# ---------------------------------------------------------------------------
# Regression tests for the out-of-range bug.
#
# parse_guess used to return (True, value, None) for ANY integer it could
# parse, because it only validated the *format* of the input and never its
# *bounds*. A guess of 500 or -3 was therefore treated as legitimate: it cost
# the player an attempt, was appended to history, and was fed into scoring.
# The fix gives parse_guess the (low, high) range and rejects anything outside
# it before returning success.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", ["101", "500", "9999", "1000000"])
def test_guess_above_high_is_rejected(raw):
    """The core bug: integers above the maximum used to be accepted."""
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == "Enter a number between 1 and 100."


@pytest.mark.parametrize("raw", ["0", "-1", "-3", "-500"])
def test_guess_below_low_is_rejected(raw):
    """The other half of the bug: zero and negatives used to be accepted."""
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == "Enter a number between 1 and 100."


@pytest.mark.parametrize("raw,expected", [("1", 1), ("50", 50), ("100", 100)])
def test_in_range_guesses_still_accepted(raw, expected):
    """The range check must be inclusive at both ends - 1 and 100 are legal."""
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is True
    assert guess_int == expected
    assert err is None


@pytest.mark.parametrize(
    "difficulty,low,high,rejected,accepted",
    [
        ("Easy", 1, 20, "21", "20"),
        ("Normal", 1, 100, "101", "100"),
        ("Hard", 1, 50, "51", "50"),
    ],
)
def test_bounds_follow_the_difficulty_range(difficulty, low, high, rejected, accepted):
    """
    The range is not hardcoded: a guess of 25 is fine on Normal but must be
    rejected on Easy, whose range is 1-20.
    """
    ok_rejected, _, err = parse_guess(rejected, low, high)
    assert ok_rejected is False, f"{rejected} should be out of range on {difficulty}"
    assert err == f"Enter a number between {low} and {high}."

    ok_accepted, guess_int, _ = parse_guess(accepted, low, high)
    assert ok_accepted is True, f"{accepted} should be valid on {difficulty}"
    assert guess_int == int(accepted)


def test_out_of_range_guess_returns_no_value_to_score():
    """
    app.py appends guess_int to history and feeds it to update_score only when
    ok is True. Returning None alongside ok=False is what stops an out-of-range
    guess from costing an attempt or moving the score.
    """
    ok, guess_int, err = parse_guess("750", 1, 50)

    assert ok is False
    assert guess_int is None
    assert err is not None


def test_range_check_applies_after_whitespace_is_stripped():
    ok, guess_int, err = parse_guess("  500  ", 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == "Enter a number between 1 and 100."


def test_defaults_to_one_through_one_hundred():
    """Called without an explicit range, parse_guess assumes 1-100."""
    assert parse_guess("500")[0] is False
    assert parse_guess("0")[0] is False
    assert parse_guess("50")[0] is True


@pytest.mark.parametrize(
    "raw,expected_error",
    [
        ("", "Enter a guess."),
        ("   ", "Enter a guess."),
        (None, "Enter a guess."),
        ("abc", "That is not a number."),
        ("3.5", "Enter a whole number (no decimals)."),
    ],
)
def test_existing_validation_is_unchanged(raw, expected_error):
    """The bounds fix must not have altered the pre-existing error messages."""
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == expected_error


# ---------------------------------------------------------------------------
# Regression tests for update_score.
#
# The scoring glitch: "Too High" returned current_score + 5 whenever
# attempt_number was even, so a wrong guess could RAISE the score and the
# player could farm points by deliberately guessing high on even turns.
# Separately, the win bonus subtracted 10 * (attempt_number + 1), but app.py
# increments attempts before calling, so the "+ 1" double-counted.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("attempt_number", [1, 2, 3, 4, 5, 6, 7, 8])
def test_wrong_guess_never_increases_score(attempt_number):
    """The core scoring bug: no wrong guess may ever gain points."""
    assert update_score(100, "Too High", attempt_number) < 100
    assert update_score(100, "Too Low", attempt_number) < 100


@pytest.mark.parametrize("attempt_number", [1, 2, 3, 4, 5, 6])
def test_too_high_and_too_low_cost_the_same(attempt_number):
    """
    The old code penalised "Too Low" unconditionally but "Too High" only on
    odd attempts. Guessing over and guessing under must cost identically.
    """
    assert update_score(50, "Too High", attempt_number) == update_score(
        50, "Too Low", attempt_number
    )


@pytest.mark.parametrize("outcome", ["Too High", "Too Low"])
def test_wrong_guess_costs_five(outcome):
    assert update_score(50, outcome, 1) == 45
    assert update_score(0, outcome, 4) == -5


@pytest.mark.parametrize(
    "attempt_number,expected_points",
    [(1, 90), (2, 80), (3, 70), (4, 60), (5, 50), (8, 20)],
)
def test_win_bonus_is_not_off_by_one(attempt_number, expected_points):
    """Winning on attempt 1 is worth 90, not the 80 the "+ 1" produced."""
    assert update_score(0, "Win", attempt_number) == expected_points


def test_win_bonus_is_floored_at_ten():
    """A very slow win still earns something rather than going negative."""
    assert update_score(0, "Win", 20) == 10
    assert update_score(0, "Win", 100) == 10


def test_earlier_wins_score_higher():
    scores = [update_score(0, "Win", n) for n in range(1, 9)]
    assert scores == sorted(scores, reverse=True)


def test_unknown_outcome_leaves_score_untouched():
    assert update_score(42, "Something Else", 3) == 42


# ---------------------------------------------------------------------------
# Tests for get_range_for_difficulty, which used to be a NotImplementedError
# stub in logic_utils.py while app.py kept its own private copy.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "difficulty,expected",
    [("Easy", (1, 20)), ("Normal", (1, 100)), ("Hard", (1, 50))],
)
def test_range_per_difficulty(difficulty, expected):
    assert get_range_for_difficulty(difficulty) == expected


@pytest.mark.parametrize("difficulty", ["", "Nightmare", "easy", None])
def test_unknown_difficulty_falls_back_to_one_through_one_hundred(difficulty):
    assert get_range_for_difficulty(difficulty) == (1, 100)


@pytest.mark.parametrize("difficulty", ["Easy", "Normal", "Hard"])
def test_range_is_usable_by_parse_guess(difficulty):
    """
    The two functions must agree: the top of the range returned here has to be
    accepted by parse_guess, and one past it rejected.
    """
    low, high = get_range_for_difficulty(difficulty)

    assert parse_guess(str(high), low, high)[0] is True
    assert parse_guess(str(high + 1), low, high)[0] is False
    assert parse_guess(str(low - 1), low, high)[0] is False


# ---------------------------------------------------------------------------
# Tests for the letters / blank-input fix.
#
# Two halves work together:
#   - parse_guess (logic_utils.py) DETECTS the bad input and builds the message
#   - the "if not ok" guard in app.py SURFACES it, and skips the attempts += 1
#     and history.append() that follow, so bad input costs the player nothing
# The tests below cover the first half directly, then the second half via a
# helper that mirrors app.py's submit branch.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "abc",
        "fifty",
        "twenty one",
        "abc123",
        "123abc",
        "1o0",          # letter o instead of zero
        "l2",           # lowercase L instead of one
        "1e5",          # scientific notation is not a whole number
        "0x1A",         # hex literal
        "NaN",
        "None",
        "true",
    ],
)
def test_letters_are_rejected(raw):
    """Any input containing letters must be refused, not parsed."""
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == "That is not a number."


@pytest.mark.parametrize(
    "raw",
    [
        "",             # empty submission
        " ",            # single space
        "     ",        # several spaces
        "\t",           # tab
        "\n",           # newline
        "  \t \n  ",    # mixed whitespace
        None,           # widget returned nothing at all
    ],
)
def test_blank_and_whitespace_only_input_is_rejected(raw):
    """Blank or whitespace-only submissions ask for a guess, not an error."""
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == "Enter a guess."


@pytest.mark.parametrize("raw", ["!!", "?", "-", "+", "@50", "50%", "#5", "--5"])
def test_symbols_are_rejected(raw):
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == "That is not a number."


@pytest.mark.parametrize("raw", ["5 0", "1 2 3", "10 20"])
def test_internal_whitespace_is_rejected(raw):
    """
    Surrounding whitespace is stripped, but whitespace INSIDE the number is
    not - "5 0" must not quietly become 50.
    """
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert err == "That is not a number."


@pytest.mark.parametrize("raw", ["  50  ", "\t50\n", " 50"])
def test_surrounding_whitespace_around_a_valid_number_is_tolerated(raw):
    """Padding a real guess with spaces should not punish the player."""
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is True
    assert guess_int == 50
    assert err is None


@pytest.mark.parametrize(
    "raw",
    ["abc", "", "   ", None, "!!", "3.5", "500", "0"],
)
def test_every_rejection_carries_a_message_and_no_value(raw):
    """
    The contract app.py's guard relies on: when ok is False there is always a
    message to show the player, and never a value that could reach scoring.
    """
    ok, guess_int, err = parse_guess(raw, 1, 100)

    assert ok is False
    assert guess_int is None
    assert isinstance(err, str) and err != ""


def _simulate_submit(state, raw, low=1, high=100):
    """
    Mirror of the submit branch in app.py (the "if not ok" guard and the two
    lines it protects). This copies app.py's logic rather than importing it,
    because app.py is a Streamlit script that cannot be imported in a test.
    Returns the error message, or None when the guess was accepted.
    """
    ok, guess_int, err = parse_guess(raw, low, high)

    if not ok:
        return err

    state["attempts"] += 1
    state["history"].append(guess_int)
    return None


@pytest.mark.parametrize("raw", ["abc", "", "   ", None, "!!", "fifty"])
def test_letters_and_blanks_do_not_cost_an_attempt(raw):
    """The point of the app.py fix: bad input is free, it does not burn a turn."""
    state = {"attempts": 3, "history": [10, 20, 30]}

    err = _simulate_submit(state, raw)

    assert err is not None
    assert state["attempts"] == 3, "a rejected guess must not spend an attempt"
    assert state["history"] == [10, 20, 30], "a rejected guess must not be logged"


def test_a_valid_guess_still_costs_an_attempt():
    """The guard must not block legitimate guesses along with the bad ones."""
    state = {"attempts": 3, "history": [10, 20, 30]}

    err = _simulate_submit(state, "42")

    assert err is None
    assert state["attempts"] == 4
    assert state["history"] == [10, 20, 30, 42]


def test_repeated_bad_input_never_ends_the_game():
    """
    Typing letters twenty times in a row should leave the player exactly where
    they started - this is what the fix prevents.
    """
    state = {"attempts": 0, "history": []}

    for junk in ["abc", "", "  ", None, "!!"] * 4:
        assert _simulate_submit(state, junk) is not None

    assert state["attempts"] == 0
    assert state["history"] == []


def test_decimal_check_runs_before_the_number_check():
    """
    Documents current precedence: the "." test happens first, so "abc.def"
    reports the decimal message rather than "That is not a number."
    """
    assert parse_guess("abc.def", 1, 100)[2] == "Enter a whole number (no decimals)."
    assert parse_guess("3.5", 1, 100)[2] == "Enter a whole number (no decimals)."
