from app.services.document_loader import load_document
from app.services.chunker import chunk_text

path = "data/constitution.pdf"  # Example (replace with your file)
text = load_document(path)
chunks = chunk_text(text)

print("Document length:", len(text))
print("Chunks created:", len(chunks))
print("Sample chunk:", chunks[0][:500])
