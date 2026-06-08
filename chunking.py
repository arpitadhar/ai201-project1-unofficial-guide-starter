import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq

groq_client = Groq()
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L12-v2")


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


def chunk_text(filepath: str, chunk_size: int = 300, overlap: int = 50) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()

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

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=count_tokens,
        separators=["\n\n", "\n", ". ", " "]
    )
    raw_chunks = splitter.split_text(raw_text)

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


def embed_chunks(chunks: list[dict], persist_dir: str = "./chroma_db"):
    """Embeds chunks into ChromaDB, or loads existing DB if already built."""
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L12-v2"
    )

    # Reuse existing DB instead of re-embedding every time
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("Loading existing ChromaDB...")
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=embedder
        )

    print("\nLoading embedding model...")
    texts     = [c["text"]     for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    print(f"Embedding {len(texts)} chunks...")
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embedder,
        metadatas=metadatas,
        persist_directory=persist_dir
    )
    print(f"Stored {len(texts)} chunks in ChromaDB")
    return vectorstore


def retrieve(vectorstore, query: str, k: int = 5) -> list[dict]:
    """Retrieves top-k relevant chunks. Uses low threshold so results aren't filtered out."""
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": k,
            "score_threshold": 0.20  #  Was 0.50 — too high, returned nothing
        }
    )

    results = retriever.invoke(query)

    # Fallback: if still no results, do plain similarity search
    if not results:
        print("No results above threshold, falling back to plain similarity search")
        results = vectorstore.similarity_search(query, k=k)

    return [{"text": doc.page_content, "metadata": doc.metadata} for doc in results]


def generate_answer(query: str, retrieved_chunks: list[dict]) -> str:
    if not retrieved_chunks:
        return "I don't have enough information to answer that."

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
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# All run-once setup is now inside __main__ — safe to import from app.py
if __name__ == "__main__":
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

    vectorstore = embed_chunks(all_chunks)

    eval_questions = [
        "How do I make LinkedIn connections?",
        "How can I make my resume stand out?",
        "How to do well in an interview?",
        "How to make the most of grad school to get a job?",
        "Why is my resume not being reviewed?"
    ]

    for question in eval_questions:
        print("\n" + "=" * 60)
        print(f"Query: {question}")
        results = retrieve(vectorstore, question, k=5)
        answer = generate_answer(question, results)
        print(f"Answer: {answer}")
        for r in results:
            print(f"  - {r['metadata'].get('source')} ({r['metadata'].get('subreddit')})")
