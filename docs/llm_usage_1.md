# LLM Usage Log

## 1. Explaining the formula

**Tool and model:** Claude Sonnet 5.5 (medium)

I asked it to explain the inputs and outputs of the formula for the exam-allocation problem, including the mathematical formula. This helped me understand the purpose of the formula and what each value represents.

[Conversation link](https://claude.ai/share/065ad2a3-4126-432d-82d2-3d445265b65c)

## 2. Formulating an example

**Tool and model:** Gemini Argon (low)

It helped me formulate the problem:

> In the Exam-Slot Assignment Problem, a university needs to schedule final exams for a set of courses into a limited number of time slots so that no student has two exams at the same time.

[Conversation link](https://share.gemini.google/MLmjMIIqhlqG)

## 3. Asking for OCL constraints

**Tool and model:** Gemini Argon (low)

[Conversation link](https://share.gemini.google/1LXn6OqnG3XA)

## 4. Code modifications

**Tool:** Claude Agent in PyCharm

![Screenshot of the code-modification discussion](imgs/44ee0859-fee5-4451-b532-e86407fa3587.png)

## 5. Explaining graph colouring

**Tool and model:** Claude Opus 5.5 (extra)

> It helped me form a clearer mental picture of the problem.

[Conversation link](https://claude.ai/share/fab1439d-c05f-4e1e-b875-cb1383d9b948)


# Mistakes and hallucinations

During the OCL constraints, AI suggested uniqueness constraints that I later figured out didn't work in B-OCL.
