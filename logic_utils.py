def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # FIX: implemented the stub by moving the working version out of app.py, so
    # the app and the tests share one definition instead of a shadowed pair.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100

#FIX: Refactored parse_guess in logic_utils.py using agent mode
def parse_guess(raw: str, low: int = 1, high: int = 100):
    """
    Parse user input into an int guess within the inclusive range [low, high].

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    # FIX: a non-str raw (an int, a bool, a list) crashed on .strip() with an
    # AttributeError. Callers now get the same clean rejection as bad text.
    if not isinstance(raw, str):
        return False, None, "That is not a number."

    text = raw.strip()

    if text == "":
        return False, None, "Enter a guess."

    # FIX: int() honours Python's underscore separators, so "1_0" silently
    # parsed as 10. No player types that, so underscores are refused outright.
    if "_" in text:
        return False, None, "That is not a number."

    if "." in text:
        # FIX: every "." was refused, so "50.0" was rejected although the
        # player plainly meant 50. Whole-valued decimals now parse; genuinely
        # fractional input like 3.5 still does not.
        if "e" in text.lower():
            return False, None, "That is not a number."
        try:
            parsed = float(text)
        except ValueError:
            return False, None, "That is not a number."
        if not parsed.is_integer():
            return False, None, "Enter a whole number (no decimals)."
        value = int(parsed)
    else:
        try:
            value = int(text)
        except ValueError:
            return False, None, "That is not a number."

    # FIX: the parse used to succeed for ANY integer, so guesses like 500 or -3
    # were accepted, burned an attempt and were scored. Bounds are now checked
    # here, against the range the caller passes in for the current difficulty.
    if value < low or value > high:
        return False, None, f"Enter a number between {low} and {high}."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIX: implemented the stub by moving the real logic from app.py, dropped
    # the str/int TypeError fallback that compared numbers lexicographically,
    # and un-swapped the hints - "Too High" must tell the player to go LOWER.
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    # FIX: "Too High" awarded +5 on even attempts, so a wrong guess could raise
    # the score - both wrong outcomes now cost 5. The win bonus also had a "+ 1"
    # that double-counted, since app.py increments attempts before scoring.
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * attempt_number)

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
