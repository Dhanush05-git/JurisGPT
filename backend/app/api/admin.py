# backend/app/api/admin.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os, shutil, json
from datetime import datetime
import joblib
import shutil

# service imports
from app.services.document_loader import load_document
from app.services.chunker import chunk_text
from app.services.embedding_service import EmbeddingService

router = APIRouter(prefix="/admin")

VERSIONS_META = "backend/data/versions/metadata.json"
UPLOAD_DIR = "backend/data/uploads"
CHUNKS_DIR = "backend/data/chunks"
EMBED_DIR = "backend/embeddings/versions"
ACTIVE_FILE = "backend/data/active_version.json"

# ensure dirs exist
os.makedirs(os.path.dirname(VERSIONS_META), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHUNKS_DIR, exist_ok=True)
os.makedirs(EMBED_DIR, exist_ok=True)

def _load_versions():
    if not os.path.exists(VERSIONS_META):
        return []
    with open(VERSIONS_META, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def _save_versions(vs):
    os.makedirs(os.path.dirname(VERSIONS_META), exist_ok=True)
    with open(VERSIONS_META, "w", encoding="utf-8") as f:
        json.dump(vs, f, indent=2)

# -----------------------
# Upload multipart files
# -----------------------
@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    version_id = str(int(datetime.utcnow().timestamp()))
    dest_folder = os.path.join(UPLOAD_DIR, version_id)
    os.makedirs(dest_folder, exist_ok=True)

    stored_paths = []
    for file in files:
        safe_name = os.path.basename(file.filename)
        dest_path = os.path.join(dest_folder, safe_name)
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        stored_paths.append(dest_path)

    versions = _load_versions()
    versions.append({
        "id": version_id,
        "name": f"Upload-{version_id}",
        "files": stored_paths,
        "status": "uploaded",
        "created_at": datetime.utcnow().isoformat()
    })
    _save_versions(versions)

    return {"message": "Files uploaded", "version_id": version_id, "files": stored_paths}

# -----------------------
# Upload local (demo) copy
# -----------------------
@router.post("/upload_local")
async def upload_local(payload: dict):
    local_path = payload.get("local_path")
    name = payload.get("name", None) or os.path.basename(local_path)
    if not local_path or not os.path.exists(local_path):
        raise HTTPException(status_code=400, detail="Local path not found")

    version_id = str(int(datetime.utcnow().timestamp()))
    dest_folder = os.path.join(UPLOAD_DIR, version_id)
    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, os.path.basename(local_path))
    shutil.copy(local_path, dest_path)

    versions = _load_versions()
    versions.append({
        "id": version_id,
        "name": name,
        "files": [dest_path],
        "status": "uploaded",
        "created_at": datetime.utcnow().isoformat()
    })
    _save_versions(versions)
    return {"version_id": version_id, "path": dest_path}

# -----------------------
# List versions
# -----------------------
@router.get("/versions")
async def list_versions():
    versions = _load_versions()
    return {"versions": versions}

# -----------------------
# Process version: extract -> chunk -> save
# -----------------------
@router.post("/process/{version_id}")
async def process_version(version_id: str):
    versions = _load_versions()
    v = next((x for x in versions if x["id"] == version_id), None)
    if not v:
        raise HTTPException(status_code=404, detail="version not found")

    try:
        out_dir = os.path.join(CHUNKS_DIR, version_id)
        os.makedirs(out_dir, exist_ok=True)
        chunks_all = []

        for fpath in v.get("files", []):
            # load text using document loader that supports pdf/docx/csv/json/txt
            text = load_document(fpath)
            if not text or not text.strip():
                continue
            # chunk smartly
            chunks = chunk_text(text, chunk_size_words=200, overlap_words=50)
            # write per-file chunk file
            base = os.path.splitext(os.path.basename(fpath))[0]
            per_file_path = os.path.join(out_dir, f"{base}_chunks.txt")
            with open(per_file_path, "w", encoding="utf-8") as pf:
                pf.write("\n\n".join(chunks))
            chunks_all.extend(chunks)

        # combined chunks file
        combined_path = os.path.join(out_dir, "chunks.txt")
        with open(combined_path, "w", encoding="utf-8") as g:
            g.write("\n".join(chunks_all))

        v["status"] = "processed"
        v["chunks_count"] = len(chunks_all)
        _save_versions(versions)
        return {"status": "processed", "chunks_saved": len(chunks_all)}
    except Exception as e:
        v["status"] = "failed"
        _save_versions(versions)
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------
# Embed version: TF-IDF -> FAISS + save vectorizer/metadata
# -----------------------
@router.post("/embed/{version_id}")
async def embed_version(version_id: str):
    versions = _load_versions()
    v = next((x for x in versions if x["id"] == version_id), None)
    if not v:
        raise HTTPException(status_code=404, detail="version not found")

    chunk_file = os.path.join(CHUNKS_DIR, version_id, "chunks.txt")
    if not os.path.exists(chunk_file):
        raise HTTPException(status_code=400, detail="chunks not found; run process first")

    try:
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunks = [line.strip() for line in f.read().splitlines() if line.strip()]

        emb = EmbeddingService()
        vectors = emb.fit_transform(chunks)  # numpy float32 array

        out_dir = os.path.join(EMBED_DIR, version_id)
        os.makedirs(out_dir, exist_ok=True)
        index_path = os.path.join(out_dir, "index.faiss")
        meta_path = os.path.join(out_dir, "metadata.txt")
        vec_path = os.path.join(out_dir, "vectorizer.pkl")

        emb.save_faiss_index(vectors, chunks, index_path, meta_path)
        # save vectorizer
        emb.save_vectorizer(vec_path)

        v["status"] = "ready"
        v["embedded_at"] = datetime.utcnow().isoformat()
        _save_versions(versions)
        return {"status": "ready", "index": index_path}
    except Exception as e:
        v["status"] = "failed_embedding"
        _save_versions(versions)
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------
# Activate a version
# -----------------------
@router.post("/activate/{version_id}")
@router.post("/version/{version_id}/activate")
async def activate_version(version_id: str):
    versions = _load_versions()
    v = next((x for x in versions if x["id"] == version_id), None)

    if not v:
        raise HTTPException(status_code=404, detail="version not found")

    # ---- WRITE ACTIVE VERSION FILE ----
    cfg = {"active_version": version_id}
    os.makedirs(os.path.dirname(ACTIVE_FILE), exist_ok=True)

    with open(ACTIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f)

    # ---- UPDATE VERSION METADATA ----
    for vv in versions:
        if vv["id"] == version_id:
            vv["status"] = "active"     # NEW — show ACTIVE in UI
            vv["active"] = True
        else:
            # Everything else becomes ready/inactive
            if vv.get("status") == "active":
                vv["status"] = "ready"
            vv["active"] = False

    _save_versions(versions)

    return {
        "status": "active",
        "activated": version_id,
        "message": f"Version {version_id} is now active."
    }


# ---------------------------------
# DELETE specific version completely
# ---------------------------------
@router.delete("/version/{version_id}")
async def delete_version(version_id: str):
    versions = _load_versions()
    v = next((x for x in versions if x["id"] == version_id), None)

    if not v:
        raise HTTPException(status_code=404, detail="Version not found")

    # Load active version
    active_version = None
    if os.path.exists(ACTIVE_FILE):
        with open(ACTIVE_FILE, "r") as f:
            active_version = json.load(f).get("active_version")

    # If trying to delete active version → clear active_version
    if active_version == version_id:
        # deactivate it
        with open(ACTIVE_FILE, "w") as f:
            json.dump({"active_version": None}, f)

    # Delete upload, chunks, embeddings folders
    paths = [
        os.path.join(UPLOAD_DIR, version_id),
        os.path.join(CHUNKS_DIR, version_id),
        os.path.join(EMBED_DIR, version_id),
    ]

    for p in paths:
        if os.path.exists(p):
            shutil.rmtree(p)

    # Remove from metadata
    versions = [x for x in versions if x["id"] != version_id]
    _save_versions(versions)

    return {
        "status": "deleted",
        "version_id": version_id,
        "active_version_cleared": (active_version == version_id)
    }


@router.post("/clear_uploads")
async def clear_uploads():
    if os.path.exists(UPLOAD_DIR):
        for item in os.listdir(UPLOAD_DIR):
            path = os.path.join(UPLOAD_DIR, item)
            shutil.rmtree(path)
    return {"status": "uploads_cleared"}
