import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


# =========================
# 1. 创建大模型客户端
# =========================

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN")
)


# =========================
# 2. 读取中文 Wiki 页面
# =========================

def load_wiki_page(url):
    """
    从 Wiki 页面中抓取正文文本
    """

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    # 删除无用标签
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    # 提取纯文本
    text = soup.get_text(separator="\n")

    # 清洗空行
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    return "\n".join(lines)


# =========================
# 3. 文档切块
# =========================

def split_text(text, chunk_size=500, overlap=80):
    """
    把长文本切成多个 chunk

    chunk_size: 每个 chunk 的最大长度
    overlap: 相邻 chunk 之间保留一点重叠内容，避免信息被切断
    """

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks


# =========================
# 4. 中文简易检索
# =========================

def retrieve(query, chunks, top_k=3):
    """
    根据用户问题，从 chunks 中找出最相关的内容

    这里先用中文字符匹配做简化版检索。
    后面可以升级成 jieba 分词 / embedding 检索。
    """

    scored_chunks = []

    for chunk in chunks:
        score = 0

        for char in query:
            if char.strip() and char in chunk:
                score += 1

        scored_chunks.append((score, chunk))

    # 按分数从高到低排序
    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    # 只返回分数大于 0 的前 top_k 个 chunk
    return [chunk for score, chunk in scored_chunks[:top_k] if score > 0]


# =========================
# 5. 调用大模型回答
# =========================

def ask_llm(question, context):
    """
    把检索到的 Wiki 内容和用户问题一起交给模型
    """

    prompt = f"""
你是一个中文游戏 Wiki 问答助手。

请你只根据下面提供的 Wiki 内容回答用户问题。
如果 Wiki 内容中没有答案，请回答：根据提供的资料，我不知道。

要求：
1. 回答要简洁清楚。
2. 不要编造 Wiki 内容中不存在的信息。
3. 如果可以，请用中文回答。

Wiki 内容：
{context}

用户问题：
{question}

回答：
"""

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# =========================
# 6. 主程序
# =========================

if __name__ == "__main__":
    url = input("请输入中文 Wiki 页面 URL：")

    print("\n正在读取 Wiki 页面...")
    document = load_wiki_page(url)

    print("正在切分文本...")
    chunks = split_text(document)

    print(f"切分完成，共生成 {len(chunks)} 个 chunks。")

    while True:
        question = input("\n请输入你的问题，输入 exit 退出：")

        if question.lower() in ["exit", "quit"]:
            print("程序已退出。")
            break

        relevant_chunks = retrieve(question, chunks)

        if not relevant_chunks:
            print("没有找到相关 Wiki 内容。")
            continue

        context = "\n\n".join(relevant_chunks)

        answer = ask_llm(question, context)

        print("\n========== 模型回答 ==========")
        print(answer)