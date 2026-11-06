from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from contextlib import asynccontextmanager
import json
import os

# ========== KONFIGURASI ==========
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://galeh:galeh@cluster0.1jalbd6.mongodb.net/?retryWrites=true&w=majority",
)
MY_SECRET_TOKEN = os.getenv("MY_SECRET_TOKEN", "frapidata")

if not MONGO_URI:
    raise RuntimeError("Environment variable MONGO_URI wajib diset!")
if not MY_SECRET_TOKEN:
    raise RuntimeError("Environment variable MY_SECRET_TOKEN wajib diset!")
# =================================

client = AsyncIOMotorClient(MONGO_URI)


# ==================== INDEX CONFIG ====================
# Format: { database: { collection: [ (keys, options) ] } }
# Aman dijalankan berulang — index yang sudah ada akan di-skip.
# =====================================================
INDEX_CONFIG = {
    "tebakgambar": {
        "game_sessions": [
            ({"chat_id": 1}, {"name": "chat_id_idx"}),
            ({"started_at": -1}, {"name": "started_at_idx"}),
        ],
        "bot_groups": [
            ({"chat_id": 1}, {"name": "chat_id_idx", "unique": True}),
        ],
    },
    "tebakkata": {
        "game_sessions": [
            ({"chat_id": 1}, {"name": "chat_id_idx"}),
            ({"started_at": -1}, {"name": "started_at_idx"}),
        ],
        "bot_groups": [
            ({"chat_id": 1}, {"name": "chat_id_idx", "unique": True}),
        ],
    },
    # Tambah database lain di sini kalau perlu
    # "susunkata": {
    #     "game_sessions": [
    #         ({"chat_id": 1}, {"name": "chat_id_idx"}),
    #     ],
    #     "bot_groups": [
    #         ({"chat_id": 1}, {"name": "chat_id_idx", "unique": True}),
    #     ],
    # },
}


async def ensure_indexes():
    """Buat index untuk semua collection yang terdaftar di INDEX_CONFIG.
    Idempotent — aman dijalankan berulang saat startup."""
    total_created = 0
    total_skipped = 0

    for db_name, collections in INDEX_CONFIG.items():
        for coll_name, indexes in collections.items():
            collection = client[db_name][coll_name]

            try:
                existing = await collection.index_information()
                existing_names = set(existing.keys())
            except Exception:
                existing_names = set()

            for keys, options in indexes:
                idx_name = options.get("name", f"{'_'.join(keys.keys())}_idx")

                if idx_name in existing_names:
                    print(f"⏭️  [{db_name}.{coll_name}] index '{idx_name}' sudah ada")
                    total_skipped += 1
                    continue

                try:
                    created = await collection.create_index(
                        list(keys.items()),
                        name=idx_name,
                        background=True,
                        **{k: v for k, v in options.items() if k != "name"},
                    )
                    print(f"✅ [{db_name}.{coll_name}] index '{created}' dibuat")
                    total_created += 1
                except Exception as e:
                    print(f"⚠️  [{db_name}.{coll_name}] gagal buat '{idx_name}': {e}")

    print(f"📊 Index summary: {total_created} dibuat, {total_skipped} sudah ada")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ping MongoDB
    try:
        await client.admin.command("ping")
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"⚠️  MongoDB ping failed: {e}")

    # 2. Auto-create indexes
    print("🔧 Memastikan index MongoDB...")
    try:
        await ensure_indexes()
    except Exception as e:
        print(f"⚠️  Gagal setup index: {e}")

    yield

    client.close()
    print("🔌 MongoDB connection closed")


app = FastAPI(title="MongoDB CRUD API", lifespan=lifespan)

# ========== CORS ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =========================


# ========== Helper ==========
def parse_json(data):
    """Convert MongoDB documents to JSON serializable"""
    if isinstance(data, list):
        return [parse_json(item) for item in data]
    if isinstance(data, dict):
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        return {k: parse_json(v) for k, v in data.items()}
    return data


def _convert_id_in_filter(filter_data):
    """Konversi `_id` (string) di filter ke ObjectId, validasi format."""
    if not isinstance(filter_data, dict):
        raise HTTPException(status_code=400, detail="Filter harus berupa object JSON")
    if "_id" in filter_data and isinstance(filter_data["_id"], str):
        try:
            filter_data["_id"] = ObjectId(filter_data["_id"])
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail=f"ID tidak valid: {filter_data['_id']}",
            )
    return filter_data


def _auth(x_api_token):
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")


# ==================== 1. CREATE / INSERT ====================
@app.post("/{database}/{collection}/insert")
async def insert_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None),
):
    """Insert satu dokumen baru ke collection"""
    _auth(x_api_token)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON tidak valid")

    document = body.get("document")
    if not document or not isinstance(document, dict):
        raise HTTPException(status_code=400, detail="Document harus berupa object")

    document["created_at"] = datetime.now(timezone.utc).isoformat()
    document["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await client[database][collection].insert_one(document)

    return {
        "status": "success",
        "inserted_id": str(result.inserted_id),
        "message": "Data berhasil diinsert",
    }


@app.post("/{database}/{collection}/insert-many")
async def insert_many_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None),
):
    """Insert banyak dokumen sekaligus"""
    _auth(x_api_token)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON tidak valid")

    documents = body.get("documents")
    if not documents or not isinstance(documents, list):
        raise HTTPException(status_code=400, detail="Documents harus berupa array")

    now = datetime.now(timezone.utc).isoformat()
    for doc in documents:
        doc["created_at"] = now
        doc["updated_at"] = now

    result = await client[database][collection].insert_many(documents)

    return {
        "status": "success",
        "inserted_ids": [str(i) for i in result.inserted_ids],
        "count": len(result.inserted_ids),
        "message": f"{len(result.inserted_ids)} data berhasil diinsert",
    }


# ==================== 2. READ / FIND ====================
@app.get("/{database}/{collection}/find")
async def find_data(
    database: str,
    collection: str,
    filter: str = None,
    limit: int = 100,
    x_api_token: str = Header(None),
):
    """Mencari dokumen dengan filter tertentu"""
    _auth(x_api_token)

    filter_dict = {}
    if filter:
        try:
            filter_dict = json.loads(filter)
        except Exception:
            raise HTTPException(status_code=400, detail="Filter format invalid")

    filter_dict = _convert_id_in_filter(filter_dict)

    cursor = client[database][collection].find(filter_dict).limit(limit)
    documents = await cursor.to_list(length=limit)
    documents = parse_json(documents)

    return {"status": "success", "count": len(documents), "data": documents}


@app.get("/{database}/{collection}/count")
async def count_data(
    database: str,
    collection: str,
    filter: str = None,
    x_api_token: str = Header(None),
):
    """Hitung jumlah dokumen (tanpa transfer data). Sangat cepat dengan index."""
    _auth(x_api_token)

    filter_dict = {}
    if filter:
        try:
            filter_dict = json.loads(filter)
        except Exception:
            raise HTTPException(status_code=400, detail="Filter format invalid")

    filter_dict = _convert_id_in_filter(filter_dict)
    count = await client[database][collection].count_documents(filter_dict)

    return {"status": "success", "count": count}


@app.get("/{database}/{collection}/{id}")
async def find_by_id(
    database: str,
    collection: str,
    id: str,
    x_api_token: str = Header(None),
):
    """Mencari dokumen berdasarkan ID"""
    _auth(x_api_token)

    try:
        object_id = ObjectId(id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID format tidak valid")

    document = await client[database][collection].find_one({"_id": object_id})

    if not document:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    return {"status": "success", "data": parse_json(document)}


# ==================== 3. UPDATE ====================
@app.post("/{database}/{collection}/upsert")
async def upsert_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None),
):
    """Update jika ada, insert jika tidak ada"""
    _auth(x_api_token)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON tidak valid")

    filter_data = body.get("filter")
    payload_data = body.get("data")

    if not filter_data:
        raise HTTPException(status_code=400, detail="Filter tidak boleh kosong")
    if not payload_data:
        raise HTTPException(status_code=400, detail="Data tidak boleh kosong")

    filter_data = _convert_id_in_filter(filter_data)

    update_data = {
        "$set": {
            **payload_data,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    }

    result = await client[database][collection].update_one(
        filter_data, update_data, upsert=True
    )

    return {
        "status": "success",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        "message": "Data berhasil diupsert",
    }


@app.put("/{database}/{collection}/update")
async def update_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None),
):
    """Update dokumen yang sudah ada (tanpa upsert)"""
    _auth(x_api_token)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON tidak valid")

    filter_data = body.get("filter")
    payload_data = body.get("data")

    if not filter_data:
        raise HTTPException(status_code=400, detail="Filter tidak boleh kosong")
    if not payload_data:
        raise HTTPException(status_code=400, detail="Data tidak boleh kosong")

    filter_data = _convert_id_in_filter(filter_data)

    update_data = {
        "$set": {
            **payload_data,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    }

    result = await client[database][collection].update_one(filter_data, update_data)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    return {
        "status": "success",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "message": "Data berhasil diupdate",
    }


# ==================== 4. DELETE ====================
@app.delete("/{database}/{collection}/delete")
async def delete_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None),
):
    """Hapus satu dokumen berdasarkan filter"""
    _auth(x_api_token)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON tidak valid")

    filter_data = body.get("filter")
    if not filter_data:
        raise HTTPException(status_code=400, detail="Filter tidak boleh kosong")

    filter_data = _convert_id_in_filter(filter_data)

    result = await client[database][collection].delete_one(filter_data)

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

    return {
        "status": "success",
        "deleted_count": result.deleted_count,
        "message": "Data berhasil dihapus",
    }


@app.delete("/{database}/{collection}/delete-many")
async def delete_many_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None),
):
    """Hapus banyak dokumen berdasarkan filter"""
    _auth(x_api_token)

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON tidak valid")

    # Field 'filter' wajib ada. Gunakan {} untuk hapus SEMUA.
    if "filter" not in body:
        raise HTTPException(
            status_code=400,
            detail="Field 'filter' wajib ada. Gunakan {} untuk hapus SEMUA data.",
        )

    filter_data = body["filter"]
    filter_data = _convert_id_in_filter(filter_data)

    result = await client[database][collection].delete_many(filter_data)

    return {
        "status": "success",
        "deleted_count": result.deleted_count,
        "message": f"{result.deleted_count} data berhasil dihapus",
    }


# ==================== HEALTH CHECK ====================
@app.get("/")
async def health_check():
    try:
        await client.admin.command("ping")
        mongo_status = "connected"
    except Exception:
        mongo_status = "disconnected"

    return {
        "status": "API ONLINE - FULL CRUD",
        "service": "running",
        "mongodb": mongo_status,
        "endpoints": {
            "create": [
                "POST /{database}/{collection}/insert",
                "POST /{database}/{collection}/insert-many",
            ],
            "read": [
                "GET /{database}/{collection}/find",
                "GET /{database}/{collection}/count",
                "GET /{database}/{collection}/{id}",
            ],
            "update": [
                "POST /{database}/{collection}/upsert",
                "PUT /{database}/{collection}/update",
            ],
            "delete": [
                "DELETE /{database}/{collection}/delete",
                "DELETE /{database}/{collection}/delete-many",
            ],
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ==================== ADMIN: INDEX MANAGEMENT ====================
@app.post("/admin/ensure-indexes")
async def admin_ensure_indexes(x_api_token: str = Header(None)):
    """Trigger manual pembuatan index tanpa perlu restart app."""
    _auth(x_api_token)
    await ensure_indexes()

    result = {}
    for db_name, collections in INDEX_CONFIG.items():
        result[db_name] = {}
        for coll_name in collections.keys():
            try:
                info = await client[db_name][coll_name].index_information()
                result[db_name][coll_name] = list(info.keys())
            except Exception as e:
                result[db_name][coll_name] = f"error: {str(e)}"

    return {"status": "success", "indexes": result}


@app.get("/admin/list-indexes")
async def admin_list_indexes(x_api_token: str = Header(None)):
    """Lihat semua index yang terpasang (read-only)."""
    _auth(x_api_token)
    result = {}
    for db_name, collections in INDEX_CONFIG.items():
        result[db_name] = {}
        for coll_name in collections.keys():
            try:
                info = await client[db_name][coll_name].index_information()
                result[db_name][coll_name] = {}
                for name, spec in info.items():
                    result[db_name][coll_name][name] = {
                        "keys": spec.get("key"),
                    }
            except Exception as e:
                result[db_name][coll_name] = f"error: {str(e)}"
    return {"status": "success", "indexes": result}
