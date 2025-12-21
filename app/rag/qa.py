from app.rag.retriever import Retriever
from app.llm.factory import get_llm
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.schemas import OUTPUT_SCHEMA

def generate_plan(user_profile: dict, request: str):
    retriever = Retriever()

    expanded_query = f"""
    {request}
    diet={user_profile.get("diet")}
    calories={user_profile.get("calorie_target")}
    equipment={user_profile.get("equipment")}
    """

    filters = {
        "type": "recipe",
        "tags": {
            "diet": user_profile.get("diet")
        }
    }

    docs = retriever.retrieve(
        expanded_query,
        k=6,
        filters=filters
    )

    context = "\n\n".join(
        f"[{d['metadata'].get('source')}]\n{d['page_content']}"
        for d in docs
    )

    prompt = f"""
    {SYSTEM_PROMPT}

    Context:
    {context}

    User profile:
    {user_profile}

    Task:
    {request}

    {OUTPUT_SCHEMA}
    """

    llm = get_llm()
    response = llm.chat(SYSTEM_PROMPT, prompt)

    return {
        "result": response,
        "sources": list({
            d["metadata"].get("source") for d in docs
        })
    }


def answer_query(query: str, user_profile: dict | None = None, k: int = 5, filters: dict | None = None):
    """Run a simple RAG QA: retrieve top documents and ask the LLM to answer with sources.

    Returns dict: {"answer": str, "sources": [..]} suitable for agent responses.
    """
    retriever = Retriever()

    expanded_query = query
    if user_profile:
        # Allow lightweight personalization in the query
        expanded_query = f"{query}\nprofile={user_profile}"

    docs = retriever.retrieve(expanded_query, k=k, filters=filters)

    context = "\n\n".join(
        f"[{d['metadata'].get('source')}]\n{d['page_content']}"
        for d in docs
    )

    prompt = f"""
    {SYSTEM_PROMPT}

    Context:
    {context}

    Question:
    {query}

    Answer concisely and cite sources in square brackets, e.g. [filename.pdf].
    """

    llm = get_llm()
    answer = llm.chat(SYSTEM_PROMPT, prompt)

    return {
        "answer": answer,
        "sources": list({d["metadata"].get("source") for d in docs})
    }
