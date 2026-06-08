import gradio as gr
from chunking import generate_answer, retrieve, embed_chunks, chunk_text

# Load vectorstore once at startup
files = [
    "jobs1.txt", "resume2.txt", "resume3.txt", "careerguidance4.txt",
    "lifehacks5.txt", "askacademia6.txt", "gradschool7.txt",
    "jobsearchhacks8.txt", "jobsearchhacks9.txt", "jobs10.txt"
]
all_chunks = []
for file in files:
    all_chunks.extend(chunk_text(file))

vectorstore = embed_chunks(all_chunks)

def handle_query(question):
    results = retrieve(vectorstore, question, k=5)
    answer = generate_answer(question, results)
    sources = "\n".join(
        f"• {r['metadata'].get('source')} ({r['metadata'].get('subreddit')})"
        for r in results
    )
    return answer, sources

with gr.Blocks() as demo:
    inp = gr.Textbox(label="Your question")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()
