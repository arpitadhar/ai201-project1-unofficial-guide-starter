# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
The topic that my system covers is job search strategies for master's students. This knowledge is valuable because securing a job is something that is a priority/necessity to many people and right now it is definitely more difficult to find a job for many people. 
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit - r/jobs | website |https://www.reddit.com/r/jobs/comments/1jla9fi/why_cant_i_find_a_job_23m_and_current_grad_student/ |
| 2 | Reddit - r/Resume | website | https://www.reddit.com/r/Resume/comments/1o5fx7t/how_i_got_7_interviews_2_weeks_ago_my_resume/ |
| 3 | Reddit - r/careeradvice | website | https://www.reddit.com/r/careeradvice/comments/1k2scto/ive_reviewed_5000_resumes_heres_how_you_can_stand/|
| 4 | Reddit - r/careerguidance | website | https://www.reddit.com/r/careerguidance/comments/qg48g8/how_do_you_exactly_network_on_linkedin/ |
| 5 | Reddit - r/lifehacks | website | https://www.reddit.com/r/lifehacks/comments/18ljxsu/interview_tips_and_tricks_that_would_impress_the/ |
| 6 | Reddit - r/AskAcademia | website |https://www.reddit.com/r/AskAcademia/comments/nvy6wz/what_did_you_do_during_graduate_school_to_fully/ |
| 7 | Reddit - r/GradSchool | website | https://www.reddit.com/r/GradSchool/comments/uiw7p0/how_to_approach_a_job_during_masters_program/|
| 8 | Reddit - r/jobsearchhacks | website |https://www.reddit.com/r/jobsearchhacks/comments/1i1l4fl/what_did_you_do_differently_to_finally_get_a_job/ |
| 9 | Reddit - r/jobsearchhacks | website |https://www.reddit.com/r/jobsearchhacks/comments/1nhypmm/whats_the_fastest_way_to_find_a_job_in_2025/ |
| 10 | Reddit - r/jobs | website |https://www.reddit.com/r/jobs/comments/18wzqxe/what_job_sites_is_everyone_using/ |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
300 token
**Overlap:**
50 token 
**Why these choices fit your documents:**
The threads create valuable data so creating smaller would lead to loss of data. 
**Final chunk count:**
500 - 600 chunks
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
Why is my resume not being reviewed?
**What the system returned:**
I don't have enough information to provide you with an answer. 
**Root cause (tied to a specific pipeline stage):**
The documents focus more on how to make a good resume instead of the latter.
**What you would change to fix it:**
Include more documents/websites. 
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
