# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

The topic that my system covers is job search strategies for master's students. This knowledge is valuable because securing a job is something that is a priority/necessity to many people and right now it is definitely more difficult to find a job for many people. 

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit - r/jobs | txt |jobs1.txt |
| 2 | Reddit - r/Resume | txt | resume2.txt |
| 3 | Reddit - r/careeradvice | txt | resume3.txt|
| 4 | Reddit - r/careerguidance | txt | careerguidance4.txt|
| 5 | Reddit - r/lifehacks | txt| lifehacks5.txt |
| 6 | Reddit - r/AskAcademia | txt |askacademia6.txt|
| 7 | Reddit - r/GradSchool | txt | gradschool7.txt|
| 8 | Reddit - r/jobsearchhacks | txt |jobsearchhacks8.txt|
| 9 | Reddit - r/jobsearchhacks | txt|jobsearchhacks9.txt|
| 10 | Reddit - r/jobs | txt |jobs10.txt |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
300 tokens
**Overlap:**
50 tokens
**Reasoning:**
The threads create valuable data so creating smaller would lead to loss of data. 
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L12-v2
**Top-k:**
5
**Production tradeoff reflection:**
Has a 512 token limit, but can only handle English queries so it may break for non english queries. It is 2x slower than the L6 model. 
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What can I do in order to secure a job as a graduate student? | Network early, apply for internships, attend career fairs, and start your job search well before graduation. |
| 2 | How can I make my resume stand out? | Tailor your resume to each job description using relevant keywords and quantify your achievements with numbers. |
| 3 | How to do well in an interview? |Research the company, use the STAR method for behavioral questions, and follow up with a thank-you email after. |
| 4 | How to make the most of grad school in order to get a job |Build relationships with professors, do internships, work on real-world projects, and start applying 6–12 months before graduation |
| 5 | Why is my resume not being reviewed? |Your resume is likely being filtered out by ATS systems due to missing keywords or not being tailored to the job posting. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Comments can get split because of the 300 chunk token size. 

2. Comments that are not useful will not get filtered out. 

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---
config:
  layout: elk
---
flowchart LR
    A["Document Ingestion<br>requests + BeautifulSoup"] --> B["Chunking<br>LangChain TextSplitter"]
    B --> C["Embedding + Vector Store<br>all-MiniLM-L6-v2 + ChromaDB"]
    C --> D["Retrieval<br>ChromaDB Similarity Search"]
    D --> E["Generation<br>GPT-4 / Claude"]

     A:::ingestion
     B:::chunking
     C:::embedding
     D:::retrieval
     E:::generation
    classDef ingestion stroke:#818cf8,fill:#eef2ff
    classDef chunking stroke:#2dd4bf,fill:#f0fdfa
    classDef embedding stroke:#a78bfa,fill:#f5f3ff
    classDef retrieval stroke:#fb923c,fill:#fff7ed
    classDef generation stroke:#e879f9,fill:#fdf4ff


---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I plan on using Claude and giving Claude my Chunking strategy section and asking it to please implement chunk_text() with the given information. 
**Milestone 4 — Embedding and retrieval:**
I plan on using Claude and giving Claude my Retrieval approach section and asking it to please implement embedding() with the given information. 
**Milestone 5 — Generation and interface:**
I plan on using Claude and giving Claude my evaluation table (the 5 questions with expected answers), my chunk metadata structure, and my retrieval output format, and asking it to implement a generate_answer()val:**

**Milestone 5 — Generation and interface:**
