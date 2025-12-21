from typing import Dict, Any, List

from langchain_community.vectorstores import Chroma, FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from ..config import Config


def _metadata_bonus(metadata: Dict, filters: Dict) -> float:
    bonus = 0.0
    for k, v in filters.items():
        if k not in metadata:
            continue

        if isinstance(v, dict) and isinstance(metadata[k], dict):
            bonus += sum(
                1 for kk, vv in v.items()
                if metadata[k].get(kk) == vv
            )
        elif metadata[k] == v:
            bonus += 1

    return bonus


class Retriever:
    def __init__(self):
        self.embeddings = (
            OpenAIEmbeddings(model="text-embedding-3-small")
            if Config.EMBEDDING_PROVIDER == "openai"
            else HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                encode_kwargs={"normalize_embeddings": True}
            )
        )

        # Use project data paths
        if Config.DB_TYPE == "chroma":
            self.vs = Chroma(
                persist_directory="data/chroma_db",
                embedding_function=self.embeddings
            )
        else:
            self.vs = FAISS.load_local(
                "data/faiss_db",
                self.embeddings,
                allow_dangerous_deserialization=True
            )

    def retrieve(
        self,
        query: str,
        k: int = 5,
        filters: Dict[str, Any] | None = None
    ) -> List[Dict]:
        raw = self.vs.similarity_search_with_relevance_scores(
            query,
            k=k * 2,
            filter=filters if isinstance(self.vs, Chroma) else None
        )

        results: List[Dict] = []
        for doc, score in raw:
            bonus = _metadata_bonus(doc.metadata, filters or {})
            results.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata,
                "score": score + 0.1 * bonus
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]
