import argparse

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma, FAISS

from langchain_openai import OpenAIEmbeddings

from ..config import Config

def load_documents(data_dir: str) -> List[Document]:
    """Load only PDF files from `data_dir` using PyMuPDFLoader.

    This focuses the ingest process on PDFs and tags metadata accordingly.
    """
    docs: List[Document] = []
    base = Path(data_dir)

    # Only consider PDF files (recursively)
    for path in base.rglob("*.pdf"):
        loader = PyMuPDFLoader(file_path=str(path), extract_images=False)

        loaded = loader.load()
        for d in loaded:
            d.metadata |= {
                "source": path.name,
                "file_type": "pdf"
            }
        docs.extend(loaded)

    return docs

def chunk_documents(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = i

    return chunks


def build_embeddings():
    if Config.LLM_PROVIDER == "openai":
        return OpenAIEmbeddings(
            model="text-embedding-3-small"
        )
    else:
        raise ValueError("Unsupported embedding provider")

def build_vectorstore(chunks: List[Document], embeddings):
    if not chunks:
        raise ValueError("No document chunks to index. Check input files or the loader.")

    # Quick content sanity check
    texts = [c.page_content for c in chunks]
    if not any((t or "").strip() for t in texts):
        raise ValueError("All document chunks are empty — nothing to embed.")

    # Try generating a small sample embedding to detect API/config issues early
    try:
        sample_emb = embeddings.embed_documents([texts[0]])
    except Exception as e:
        raise RuntimeError(f"Embedding generation failed: {e}") from e

    if not sample_emb:
        raise ValueError("Embedding provider returned empty embeddings. Check API keys/config.")

    if Config.DB_TYPE == "chroma":
        persist_dir = "data/chroma_db"
        vs = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        # Ensure persisted DB is written to disk
        try:
            vs.persist()
        except Exception:
            # Some Chroma clients persist on creation; ignore if not available
            pass
        return vs
    
    if Config.DB_TYPE == "faiss":
        vs = FAISS.from_documents(
            documents=chunks,
            embedding=embeddings,
        )
        vs.save_local("data/faiss_db")
        return vs

def verify(vs):
    if hasattr(vs, "_collection"):
        print("Total vectors:", vs._collection.count())

    sample = vs.similarity_search(
        "sample query about workout plan",
        k=2
    )

    for d in sample:
        print("---")
        print(d.page_content[:150])
        print(d.metadata)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Ingest PDFs into Chroma vectorstore")
    parser.add_argument("--data-dir", default="data/PDF", help="Directory containing PDF files")
    args = parser.parse_args()

    docs = load_documents(args.data_dir)
    if not docs:
        raise SystemExit(f"No PDFs found in {args.data_dir}")

    chunks = chunk_documents(docs)

    embeddings = build_embeddings()
    vs = build_vectorstore(chunks, embeddings)

    verify(vs)
