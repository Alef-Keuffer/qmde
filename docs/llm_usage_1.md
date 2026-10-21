# LLM Usage Log

## 1. Explaining the formula

**Tool and model:** Claude Sonnet 5.5 (medium)

I asked it to explain the inputs and outputs of the formula for the exam-allocation problem, including the mathematical formula. This helped me understand the purpose of the formula and what each value represents.

[Conversation link](https://claude.ai/share/065ad2a3-4126-432d-82d2-3d445265b65c)

## 2. Formulating an example

- **used by:** Alef
- **Tool/Model:** Gemini Argon (low)
- [Conversation link](https://share.gemini.google/MLmjMIIqhlqG)

It helped me formulate and understand the problem. This is the most important insight I got at the time:

> In the Exam-Slot Assignment Problem, a university needs to schedule final exams for a set of courses into a limited number of time slots so that no student has two exams at the same time.


## 3. Asking for OCL constraints

- **Tool/Model:** Gemini Argon (low)
- [Conversation link](https://share.gemini.google/1LXn6OqnG3XA)

I got the suggestion of a few constraints. This led to some trouble later which is described in the [report](./report_1.md) and at [hallucinations](#mistakes-and-hallucinations).

## 4. Code modifications

- **used by:** Alef
- **Tool:** Claude Agent in PyCharm

I managed to get uniqueness OCL constraints working locally. This is referenced in the [report](./report_1.md)

![Screenshot of the code-modification discussion](imgs/44ee0859-fee5-4451-b532-e86407fa3587.png)

## 5. Explaining graph colouring

**Tool and model:** Claude Opus 5.5 (extra)

> It helped me form a clearer mental picture of the problem.

[Conversation link](https://claude.ai/share/fab1439d-c05f-4e1e-b875-cb1383d9b948)

## 6. Asking for references

- **used by:** Alef
- **Tool/Model:** Gemini 3.1 Pro (High)
- [Conversation Link](https://share.gemini.google/znTtRxN5Zh1R)

> I'm working on an exam-slot assignment problem. I want to see examples of translating the problem into QUBO. Give me some references
> 
> (prompt)

From this interaction I got this reference which I found useful:

- "Hybrid Quantum Annealing for Large-Scale Exam Scheduling" (Zhou et al., 2025)


# Mistakes and hallucinations

During the OCL constraints, AI suggested uniqueness constraints that I later figured out didn't work in B-OCL.

Also, I had trouble because the AI tried providing constraints that didn't work in B-OCL (B-OCL is not a full implementation of OCL and some notation is different).
