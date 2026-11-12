from groq import AsyncGroq

import config


client = None

def get_client():
    global client
    if client is None:
        client = AsyncGroq(timeout=30.0)
    return client


SYSTEM_PROMPT = """
You are a technical documentation assistant.

Answer the user's question using ONLY the provided context.

Rules:
1. Do not use outside knowledge.
2. If the context does not contain enough information, say so.
3. Cite your sources using labels such as [1] and [2].
4. Do not invent facts, code, or citations.
5. Keep answers clear and technically accurate.
"""


def build_context(chunks, max_chars=1500):
    """Build numbered context from retrieved documentation chunks."""

    context_parts = []

    for i, chunk in enumerate(chunks, start=1):
        text = chunk["text"][:max_chars]

        context_parts.append(
            f"[{i}] File: {chunk['file']}\n"
            f"Heading: {chunk['heading']}\n"
            f"Content:\n{text}"
        )

    return "\n\n".join(context_parts)


async def generate_answer(question, chunks):
    """Generate an answer using only the retrieved documentation."""

    context = build_context(chunks)

    response = await get_client().chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\n"
                    f"Question: {question}"
                )
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()