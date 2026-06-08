import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq

groq_client = Groq()
# Load tokenizer matching your embedding model
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L12-v2")


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))

def chunk_text(filepath: str, chunk_size: int = 300, overlap: int = 50) -> list[dict]:
    """
    Reads a .txt file and splits it into chunks.
    
    Args:
        filepath:   path to the .txt file (e.g. 'jobs1.txt')
        chunk_size: max tokens per chunk (default 300)
        overlap:    token overlap between chunks (default 50)
    
    Returns:
        List of dicts with 'text' and 'metadata' keys
    """

    # --- 1. Read the file ---
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # --- 2. Derive metadata from filename ---
    filename = os.path.basename(filepath)
    source_map = {
        "jobs1.txt":           {"subreddit": "r/jobs",           "thread": 1},
        "resume2.txt":         {"subreddit": "r/Resume",         "thread": 2},
        "resume3.txt":         {"subreddit": "r/careeradvice",   "thread": 3},
        "careerguidance4.txt": {"subreddit": "r/careerguidance", "thread": 4},
        "lifehacks5.txt":      {"subreddit": "r/lifehacks",      "thread": 5},
        "askacademia6.txt":    {"subreddit": "r/AskAcademia",    "thread": 6},
        "gradschool7.txt":     {"subreddit": "r/GradSchool",     "thread": 7},
        "jobsearchhacks8.txt": {"subreddit": "r/jobsearchhacks", "thread": 8},
        "jobsearchhacks9.txt": {"subreddit": "r/jobsearchhacks", "thread": 9},
        "jobs10.txt":          {"subreddit": "r/jobs",           "thread": 10},
    }
    metadata_base = source_map.get(filename, {"subreddit": "unknown", "thread": 0})

    # --- 3. Split into chunks ---
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=count_tokens,       # token-based, not character-based
        separators=["\n\n", "\n", ". ", " "]
    )
    raw_chunks = splitter.split_text(raw_text)

    # --- 4. Attach metadata to every chunk ---
    chunks = []
    for i, chunk in enumerate(raw_chunks):
        chunks.append({
            "text": chunk.strip(),
            "metadata": {
                "source":    filename,
                "subreddit": metadata_base["subreddit"],
                "thread":    metadata_base["thread"],
                "chunk_id":  i,
                "tokens":    count_tokens(chunk)
            }
        })

    return chunks


files = [
    "jobs1.txt", "resume2.txt", "resume3.txt", "careerguidance4.txt",
    "lifehacks5.txt", "askacademia6.txt", "gradschool7.txt",
    "jobsearchhacks8.txt", "jobsearchhacks9.txt", "jobs10.txt"
]

all_chunks = []
for file in files:
    chunks = chunk_text(file)
    all_chunks.extend(chunks)
    print(f"{file}: {len(chunks)} chunks")

print(f"\nTotal chunks: {len(all_chunks)}")

assert all(c["metadata"]["tokens"] <= 300 for c in all_chunks), "Chunk too large"
assert all(len(c["text"]) > 0 for c in all_chunks), "Empty chunk found"
assert len(set(c["metadata"]["source"] for c in all_chunks)) == 10, "Missing files"
print("All checks passed")

  # --- Print 5 representative chunks for inspection ---
import random

print("=" * 60)
print("CHUNK INSPECTION — 5 REPRESENTATIVE CHUNKS")
print("=" * 60)

# Pick 5 chunks spread across the corpus, not just the first 5
step = len(all_chunks) // 5
sample_indices = [i * step for i in range(5)]

for rank, idx in enumerate(sample_indices, 1):
    chunk = all_chunks[idx]
    text = chunk["text"]
    tokens = chunk["metadata"]["tokens"]
    source = chunk["metadata"]["source"]
    subreddit = chunk["metadata"]["subreddit"]

    print(f"\nChunk {rank} of 5")
    print(f"Source:   {source} ({subreddit})")
    print(f"Tokens:   {tokens}")
    print(f"chunk_id: {chunk['metadata']['chunk_id']}")
    print(f"\nText:\n{text}")

    # --- Standalone quality check ---
    words = text.split()
    has_verb = any(w.lower() in [
        "is", "are", "was", "were", "have", "has", "do", "does",
        "can", "should", "need", "get", "make", "use", "apply",
        "start", "try", "found", "said", "told", "went"
    ] for w in words)

    if tokens < 30:
        verdict = "⚠️  BAD  — too short, likely a fragment"
    elif not has_verb:
        verdict = "⚠️  BAD  — may be a fragment, no clear action or statement"
    elif tokens < 60:
        verdict = "⚠️  WEAK — short, may lack full context"
    else:
        verdict = "✅ GOOD — sufficient length and likely self-contained"

    print(f"\nVerdict: {verdict}")
    print("-" * 60)


# --- Embedding ---
def embed_chunks(chunks: list[dict]):
    """
    Takes chunks from chunk_text() and stores them in a Chroma vector DB.
    
    Args:
        chunks: list of dicts with 'text' and 'metadata' keys
    
    Returns:
        vectorstore: Chroma vectorstore ready for retrieval
    """
    print("\nLoading embedding model (all-MiniLM-L12-v2)...")
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L12-v2"
    )

    texts     = [c["text"]     for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embedder,
        metadatas=metadatas,
        persist_directory="./chroma_db"
    )

    print(f"Stored {len(texts)} chunks in ChromaDB")
    return vectorstore


# --- Retrieval ---
def retrieve(vectorstore, query: str, k: int = 5) -> list[dict]:
    """
    Retrieves top-k most relevant chunks for a given query.
    
    Args:
        vectorstore: Chroma vectorstore from embed_chunks()
        query:       user question as a string
        k:           number of chunks to retrieve (default 5)
    
    Returns:
        List of dicts with 'text', 'score', and 'metadata' keys
    """
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": k,
            "score_threshold": 0.50
        }
    )

    results = retriever.invoke(query)

    retrieved = []
    for doc in results:
        retrieved.append({
            "text":     doc.page_content,
            "metadata": doc.metadata
        })

    return retrieved


# --- Run embedding + retrieval ---
if __name__ == "__main__":

    # -- reuse all_chunks from chunking stage --
    files = [
        "jobs1.txt", "resume2.txt", "resume3.txt", "careerguidance4.txt",
        "lifehacks5.txt", "askacademia6.txt", "gradschool7.txt",
        "jobsearchhacks8.txt", "jobsearchhacks9.txt", "jobs10.txt"
    ]

    all_chunks = []
    for file in files:
        chunks = chunk_text(file)
        all_chunks.extend(chunks)

    # -- embed --
    vectorstore = embed_chunks(all_chunks)

    # -- test retrieval with your 5 eval questions --
    eval_questions = [
        "How to I make linkedin connections?",
        "How can I make my resume stand out?",
        "How to do well in an interview?",
        "How to make the most of grad school in order to get a job?",
        "Why is my resume not being reviewed?"
    ]

    for question in eval_questions:
        print("\n" + "=" * 60)
        print(f"Query: {question}")
        print("=" * 60)

        results = retrieve(vectorstore, question, k=5)

        if not results:
            print("No results above score threshold")
            continue

        for i, r in enumerate(results, 1):
            print(f"\nResult {i}")
            print(f"Source:   {r['metadata'].get('source')} ({r['metadata'].get('subreddit')})")
            print(f"Tokens:   {r['metadata'].get('tokens')}")
            print(f"Text:\n{r['text']}")
            print("-" * 60)

def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    """
    Takes a query and retrieved chunks and generates a grounded answer.

    Args:
        query:             user question as a string
        retrieved_chunks:  list of dicts from retrieve()

    Returns:
        Generated answer as a string
    """
    # Build context from retrieved chunks
    context = ""
    for i, chunk in enumerate(retrieved_chunks, 1):
        source = chunk["metadata"].get("source", "unknown")
        context += f"[{i}] ({source})\n{chunk['text']}\n\n"

    prompt = f"""You are a career advisor helping graduate students find jobs.
Answer the question below using ONLY the context provided.
If the context does not contain enough information, say "I don't have enough information to answer that."

Context:
{context}

Question: {query}

Answer in 2-3 sentences, grounded in the context above."""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# --- Evaluation ---
eval_questions = [
    {
        "question": "What can I do in order to secure a job as a graduate student?",
        "expected": "Network early, apply for internships, attend career fairs, and start your job search well before graduation."
    },
    {
        "question": "How can I make my resume stand out?",
        "expected": "Tailor your resume to each job description using relevant keywords and quantify your achievements with numbers."
    },
    {
        "question": "How to do well in an interview?",
        "expected": "Research the company, use the STAR method for behavioral questions, and follow up with a thank-you email after."
    },
    {
        "question": "How to make the most of grad school in order to get a job?",
        "expected": "Build relationships with professors, do internships, work on real-world projects, and start applying 6-12 months before graduation."
    },
    {
        "question": "Why is my resume not being reviewed?",
        "expected": "Your resume is likely being filtered out by ATS systems due to missing keywords or not being tailored to the job posting."
    }
]


url_map = {
    "jobs1.txt":           "https://www.reddit.com/r/jobs/comments/1jla9fi/why_cant_i_find_a_job_23m_and_current_grad_student/",
    "resume2.txt":         "https://www.reddit.com/r/Resume/comments/1o5fx7t/how_i_got_7_interviews_2_weeks_ago_my_resume/",
    "resume3.txt":         "https://www.reddit.com/r/careeradvice/comments/1k2scto/ive_reviewed_5000_resumes_heres_how_you_can_stand/",
    "careerguidance4.txt": "https://www.reddit.com/r/careerguidance/comments/qg48g8/how_do_you_exactly_network_on_linkedin/",
    "lifehacks5.txt":      "https://www.reddit.com/r/lifehacks/comments/18ljxsu/interview_tips_and_tricks_that_would_impress_the/",
    "askacademia6.txt":    "https://www.reddit.com/r/AskAcademia/comments/nvy6wz/what_did_you_do_during_graduate_school_to_fully/",
    "gradschool7.txt":     "https://www.reddit.com/r/GradSchool/comments/uiw7p0/how_to_approach_a_job_during_masters_program/",
    "jobsearchhacks8.txt": "https://www.reddit.com/r/jobsearchhacks/comments/1i1l4fl/what_did_you_do_differently_to_finally_get_a_job/",
    "jobsearchhacks9.txt": "https://www.reddit.com/r/jobsearchhacks/comments/1nhypmm/whats_the_fastest_way_to_find_a_job_in_2025/",
    "jobs10.txt":          "https://www.reddit.com/r/jobs/comments/18wzqxe/what_job_sites_is_everyone_using/",
}
if __name__ == "__main__":

    # -- reuse all_chunks from chunking stage --
    files = [
        "jobs1.txt", "resume2.txt", "resume3.txt", "careerguidance4.txt",
        "lifehacks5.txt", "askacademia6.txt", "gradschool7.txt",
        "jobsearchhacks8.txt", "jobsearchhacks9.txt", "jobs10.txt"
    ]

    all_chunks = []
    for file in files:
        chunks = chunk_text(file)
        all_chunks.extend(chunks)

    # -- embed --
    vectorstore = embed_chunks(all_chunks)

    # -- run evaluation --
    print("\n" + "=" * 60)
    print("EVALUATION — 5 QUESTIONS")
    print("=" * 60)

    for i, item in enumerate(eval_questions, 1):
        question = item["question"]
        ##expected = item["expected"]

        # Retrieve
        results = retrieve(vectorstore, question, k=5)

        # Generate
        generated = generate_answer(question, results)

        print(f"\nQ{i}: {question}")
        print(f"\nExpected:  {expected}")
        print(f"\nGenerated: {generated}")
        print(f"\nSources:")
        for r in results:
            print(f"  - {r['metadata'].get('source')} ({r['metadata'].get('subreddit')})")
        print("-" * 60)
