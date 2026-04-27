import os
from openai import OpenAI

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN")
)

# 1. 准备本地文档
document = """
LangChain is a framework for developing applications powered by large language models.
It provides tools for prompt management, chains, agents, memory, and retrieval.

RAG means Retrieval-Augmented Generation.
It allows a language model to answer questions using external documents.
The basic process of RAG is: split documents, retrieve relevant chunks, and generate answers.

Agents can use tools to solve tasks.
A tool is usually a function that the language model can call.
For example, an agent can use a calculator tool or a search tool.

Memory allows a chatbot to remember previous conversations.
Without memory, each interaction is independent.
"""

# 2. 文档切块
def split_text(text, chunk_size=180):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks


# 3. 简单关键词检索
def retrieve(query, chunks, top_k=2):
    query_words = query.lower().split()

    scored_chunks = []

    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = 0

        for word in query_words:
            if word in chunk_lower:
                score += 1

        scored_chunks.append((score, chunk))

    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    return [chunk for score, chunk in scored_chunks[:top_k] if score > 0]


# 4. 调用 LLM 生成回答
def ask_llm(question, context):
    prompt = f"""
You are a helpful AI assistant.

Answer the user's question based only on the context below.
If the answer is not in the context, say "I don't know based on the given context."

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# 5. 主程序
if __name__ == "__main__":
    chunks = split_text(document)

    while True:
        question = input("\nAsk a question: ")

        if question.lower() in ["exit", "quit"]:
            break

        relevant_chunks = retrieve(question, chunks)

        if not relevant_chunks:
            print("No relevant context found.")
            continue

        context = "\n\n".join(relevant_chunks)

        answer = ask_llm(question, context)

        print("\nRetrieved Context:")
        print(context)

        print("\nAnswer:")
        print(answer)