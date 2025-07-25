from typing import Any, List, Optional

from pydantic import PrivateAttr

from semantic_router.encoders.base import DenseEncoder


class LocalEncoder(DenseEncoder):
    """Local encoder using sentence-transformers for efficient local embeddings."""

    name: str = "BAAI/bge-small-en-v1.5"
    type: str = "local"
    device: Optional[str] = None
    normalize_embeddings: bool = True
    batch_size: int = 32
    _model: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "Please install sentence-transformers to use LocalEncoder. "
                "You can install it with: `pip install semantic-router[local]`"
            )
        self._model = SentenceTransformer(self.name)
        if self.device:
            self._model.to(self.device)
        else:
            # Auto-detect device
            import torch

            if torch.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
            self._model.to(self.device)

    def __call__(self, docs: List[str]) -> List[List[float]]:
        result = self._model.encode(
            docs,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize_embeddings,
            device=self.device,
        )
        return result.tolist()  # type: ignore[attr-defined]
