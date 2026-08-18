from dataclasses import dataclass

from django.conf import settings
from pgvector.django import CosineDistance

from apps.documents.models import Document, DocumentChunk
from apps.documents.services.embeddings import embed_texts


@dataclass(frozen=True)
class RetrievedChunk:
    """A chunk accepted as relevant for a user question."""

    content: str
    source_label: str
    distance: float
    document_id: int
    chunk_index: int


def retrieve_relevant_chunks(
    question: str,
    *,
    category: str | None = None,
    limit: int | None = None,
) -> list[RetrievedChunk]:
    """Return only chunks whose cosine distance passes the relevance threshold.

    Cosine distance ranges from 0 (most similar) to 2 (least similar). A lower
    value is therefore better; chunks above ``RAG_MAX_COSINE_DISTANCE`` are
    discarded before the generation layer can use them.
    """
    normalized_question = question.strip()
    if not normalized_question:
        return []

    question_embedding = embed_texts([normalized_question])[0]
    result_limit = limit if limit is not None else settings.RAG_RETRIEVAL_K
    if result_limit <= 0:
        raise ValueError("O limite de resultados deve ser maior que zero.")

    chunks = DocumentChunk.objects.filter(
        document__status=Document.Status.READY,
        embedding__isnull=False,
    )
    if category:
        chunks = chunks.filter(document__category__iexact=category.strip())

    relevant_chunks = (
        chunks.annotate(distance=CosineDistance("embedding", question_embedding))
        .filter(distance__lte=settings.RAG_MAX_COSINE_DISTANCE)
        .select_related("document")
        .order_by("distance")[:result_limit]
    )

    return [
        RetrievedChunk(
            content=chunk.content,
            source_label=chunk.source_label,
            distance=float(chunk.distance),
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
        )
        for chunk in relevant_chunks
    ]
