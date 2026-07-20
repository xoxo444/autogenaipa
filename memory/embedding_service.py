import os
import traceback

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()


class EmbeddingService:

    def __init__(self):
        self.client = InferenceClient(
            api_key=os.getenv("HF_TOKEN")
        )

        self.model = "sentence-transformers/all-MiniLM-L6-v2"

        print("Embedding model:", self.model)

    def embed(self, text: str) -> list[float]:

        print("\n========== EMBEDDING ==========")
        print("Input:", text)

        try:
            print("Calling Hugging Face...")

            embedding = self.client.feature_extraction(
                text=text,
                model=self.model,
            )

            print("HF call completed")

            if len(embedding) > 0 and isinstance(embedding[0], list):
                embedding = embedding[0]

            embedding = [float(x) for x in embedding]

            print("Embedding dimension:", len(embedding))

            return embedding

        except Exception as e:
            print("\n========== EMBEDDING ERROR ==========")
            traceback.print_exc()
            print(type(e).__name__)
            print(e)
            raise

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]