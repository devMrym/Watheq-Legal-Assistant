import chromadb

DB_PATH = "chroma_db_watheq"  # your local folder

client = chromadb.PersistentClient(path=DB_PATH)

print("\n=== COLLECTIONS ===")
collections = client.list_collections()
print(collections)

# Try each collection and inspect it
for col in collections:
    name = col.name
    print(f"\n===== COLLECTION: {name} =====")

    collection = client.get_collection(name)

    print("COUNT:", collection.count())

    # Peek into actual stored data
    peek = collection.peek()

    print("\nSAMPLE IDS:", peek.get("ids"))
    print("\nSAMPLE DOCS:", peek.get("documents"))
    print("\nSAMPLE METADATA:", peek.get("metadatas"))