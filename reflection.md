# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

# NOTES
Alphabets throw a "that's not a number" error (This Is Good) 

|---------------|-------------------|----------------------|------------------------|
| Input         | Expected Behavior | Actual Behavior      | Console Output / Error |
|-------------- |-------------------|----------------------|------------------------|
| number > 100  | Error message     | Code ran like normal | None                   |
|-------------- |-------------------|----------------------|------------------------|
| number <= 0   | Error Message     | Code ran like normal | None                   |
|---------------|-------------------|----------------------|------------------------|
| First Guess   | Attempts left -= 1| Attempts starts to   | None                   |
|               |                   | reduces on 2nd guess | None                   |
|---------------|-------------------|----------------------|------------------------|
|Attempts reduce| Attempts remain   | Attempts reduce by 1 | None                   |
|for letters and| static            | like normal          |                        |
|blank guesses  |                   |                      |                        |
|---------------|-------------------|----------------------|------------------------|
| New Game      | Attempts reset    | Attempts reset to 8  | None                   |
|               | to 7              |                      |                        | 
|---------------|-------------------|----------------------|------------------------|

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
-> Claude

- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
-> The suggestion to input 1 and 100 and low and high respectively to the parse_guess function to solve the issue
of the game not recognizing numbers outside 1-100 as errors.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
-> In my case, AI just didn't suggest a fix which I implemented. For example, the st.session_state attempts was set to 1 which made the intial game start with 7 attempts instead of 8.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
-> I ran the code again and re-checked every error.

- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
-> I put 0 and 101 as guessing numbers and got an error that the range was 1 to 100

- Did AI help you design or understand any tests? How?
-> No, I just tested based on previous bugs identified by myself.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
-> Streamlit is an alternative open-source pacakage that helps create demos for web projects with Python
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
-> Prompt Engineering without putting too much work/trust in AI

- What is one thing you would do differently next time you work with AI on a coding task?
-> Identify said problem and document it so I can easily test them with subsequent fixes.

- In one or two sentences, describe how this project changed the way you think about AI generated code.
-> AI generated code has its perks but certainly its lows. I'd prefer checking code and testing it too to be very sure of its quality before shipping.
