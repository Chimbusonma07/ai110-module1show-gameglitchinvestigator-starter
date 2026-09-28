# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

All 144 tests pass. Run with: `python -m pytest tests/test_game_logic.py -q`

| Edge Case                 | Prompt Used                                | AI-Suggested Test                                | Did It Pass?                  | Your Reasoning                                   |
|---------------------------|--------------------------------------------|--------------------------------------------------|-------------------------------|--------------------------------------------------|
| number > 100              | Generate a pytest case targeting this bug  | `test_guess_above_high_is_rejected`              | Failed before fix, passes now | parse_guess checked format but never bounds      |
| number <= 0               | Same prompt                                | `test_guess_below_low_is_rejected`               | Failed before fix, passes now | Same root cause at the low end of the range      |
| Boundaries 1 and 100      | Same prompt                                | `test_in_range_guesses_still_accepted`           | Passed                        | Range must be inclusive, no off-by-one           |
| Letters and blank guesses | Write test cases for the blank/letter fix  | `test_letters_and_blanks_do_not_cost_an_attempt` | Passed                        | Bad input must not reduce attempts or be logged  |
| check_guess return value  | Explain why these tests fail and fix it    | Unpack `outcome, message = check_guess(50, 50)`  | Test itself was wrong         | Function returns a tuple, not a plain string     |
| Too High on even attempt  | Are the remaining stubs worth changing?    | `test_wrong_guess_never_increases_score`         | Failed before fix, passes now | Wrong guess added +5 points on even attempts     |
| Underscores, e.g. 1 _ 0   | Any edge cases left, e.g. decimals?        | `test_underscore_separators_are_rejected`        | Failed before fix, passes now | Python int() allows underscores, so it read 10   |
| Decimals, e.g. 50.0       | Same prompt                                | `test_whole_valued_decimals_are_accepted`        | Failed before fix, passes now | The "." check rejected 50.0 along with 3.5       |
| Decimals, e.g. 3.5        | Same prompt                                | `test_fractional_decimals_are_still_rejected`    | Passed                        | Real fractions must stay invalid after that fix  |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
