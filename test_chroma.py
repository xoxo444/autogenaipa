import chromadb
import traceback

print("1")

client = chromadb.PersistentClient(path="./memory/chroma_db")
print("2")

collection = client.get_or_create_collection("assistant_memory")
print("3")

try:
    print("COUNT")
    print(collection.count())
    print("COUNT DONE")
except Exception:
    traceback.print_exc()

print("4")

try:
    print("ADD")
    collection.add(
        ids=["1"],
        documents=["hello"],
        embeddings=[[0.0] * 384],
    )
    print("ADD DONE")
except Exception:
    traceback.print_exc()

print("5")

try:
    print("QUERY")
    result = collection.query(
        query_embeddings=[[0.0] * 384],
        n_results=1,
    )
    print(result)
    print("QUERY DONE")
except Exception:
    traceback.print_exc()

print("6")