from memory.embedding_service import EmbeddingService

emb = EmbeddingService()

v = emb.embed("Hello world")

print(type(v))
print(len(v))
print(v[:5])