from fastapi import FastAPI, Header, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from bson import ObjectId
import json

app = FastAPI()

# ========== KONFIGURASI HARDCODED ==========
# GANTI DENGAN DATA MONGODB ANDA!
MONGO_URI = "mongodb+srv://galeh:galeh@cluster0.1jalbd6.mongodb.net/?retryWrites=true&w=majority"
MY_SECRET_TOKEN = "frapidata"
# ===========================================

# Koneksi MongoDB
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()

# Helper untuk konversi ObjectId
def parse_json(data):
    """Convert MongoDB documents to JSON serializable"""
    if isinstance(data, list):
        return [parse_json(item) for item in data]
    if isinstance(data, dict):
        if "_id" in data and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        return {k: parse_json(v) for k, v in data.items()}
    return data

# ==================== 1. CREATE / INSERT ====================
@app.post("/{database}/{collection}/insert")
async def insert_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None)
):
    """Insert satu dokumen baru ke collection"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON tidak valid")
    
    document = body.get("document")
    if not document:
        raise HTTPException(status_code=400, detail="Document tidak boleh kosong")
    
    # Tambahkan timestamp
    document["created_at"] = datetime.now(timezone.utc).isoformat()
    document["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Pilih database dan collection
    db_client = client[database]
    collection_obj = db_client[collection]
    
    result = await collection_obj.insert_one(document)
    
    return {
        "status": "success",
        "inserted_id": str(result.inserted_id),
        "message": "Data berhasil diinsert"
    }

@app.post("/{database}/{collection}/insert-many")
async def insert_many_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None)
):
    """Insert banyak dokumen sekaligus"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON tidak valid")
    
    documents = body.get("documents")
    if not documents or not isinstance(documents, list):
        raise HTTPException(status_code=400, detail="Documents harus berupa array")
    
    # Tambahkan timestamp ke setiap dokumen
    for doc in documents:
        doc["created_at"] = datetime.now(timezone.utc).isoformat()
        doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    db_client = client[database]
    collection_obj = db_client[collection]
    
    result = await collection_obj.insert_many(documents)
    
    return {
        "status": "success",
        "inserted_ids": [str(id) for id in result.inserted_ids],
        "count": len(result.inserted_ids),
        "message": f"{len(result.inserted_ids)} data berhasil diinsert"
    }

# ==================== 2. READ / FIND ====================
@app.get("/{database}/{collection}/find")
async def find_data(
    database: str,
    collection: str,
    filter: str = None,
    limit: int = 100,
    x_api_token: str = Header(None)
):
    """Mencari dokumen dengan filter tertentu"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    # Parse filter
    filter_dict = {}
    if filter:
        try:
            filter_dict = json.loads(filter)
        except:
            raise HTTPException(status_code=400, detail="Filter format invalid")
    
    db_client = client[database]
    collection_obj = db_client[collection]
    
    cursor = collection_obj.find(filter_dict).limit(limit)
    documents = await cursor.to_list(length=limit)
    
    # Convert ObjectId ke string
    documents = parse_json(documents)
    
    return {
        "status": "success",
        "count": len(documents),
        "data": documents
    }

@app.get("/{database}/{collection}/{id}")
async def find_by_id(
    database: str,
    collection: str,
    id: str,
    x_api_token: str = Header(None)
):
    """Mencari dokumen berdasarkan ID"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    try:
        object_id = ObjectId(id)
    except:
        raise HTTPException(status_code=400, detail="ID format tidak valid")
    
    db_client = client[database]
    collection_obj = db_client[collection]
    
    document = await collection_obj.find_one({"_id": object_id})
    
    if not document:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    
    document = parse_json(document)
    
    return {
        "status": "success",
        "data": document
    }

# ==================== 3. UPDATE ====================
@app.post("/{database}/{collection}/upsert")
async def upsert_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None)
):
    """Update jika ada, Insert jika tidak ada (UPSERT)"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON tidak valid")
    
    filter_data = body.get("filter")
    payload_data = body.get("data")
    
    if not filter_data:
        raise HTTPException(status_code=400, detail="Filter tidak boleh kosong")
    if not payload_data:
        raise HTTPException(status_code=400, detail="Data tidak boleh kosong")
    
    # Handle ObjectId di filter
    if "_id" in filter_data and isinstance(filter_data["_id"], str):
        filter_data["_id"] = ObjectId(filter_data["_id"])
    
    db_client = client[database]
    collection_obj = db_client[collection]
    
    update_data = {
        "$set": {
            **payload_data,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    result = await collection_obj.update_one(
        filter_data,
        update_data,
        upsert=True
    )
    
    return {
        "status": "success",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "upserted_id": str(result.upserted_id) if result.upserted_id else None,
        "message": "Data berhasil diupsert"
    }

@app.put("/{database}/{collection}/update")
async def update_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None)
):
    """Update dokumen yang sudah ada (tanpa upsert)"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON tidak valid")
    
    filter_data = body.get("filter")
    payload_data = body.get("data")
    
    if not filter_data:
        raise HTTPException(status_code=400, detail="Filter tidak boleh kosong")
    if not payload_data:
        raise HTTPException(status_code=400, detail="Data tidak boleh kosong")
    
    # Handle ObjectId di filter
    if "_id" in filter_data and isinstance(filter_data["_id"], str):
        filter_data["_id"] = ObjectId(filter_data["_id"])
    
    db_client = client[database]
    collection_obj = db_client[collection]
    
    update_data = {
        "$set": {
            **payload_data,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    }
    
    result = await collection_obj.update_one(filter_data, update_data)
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    
    return {
        "status": "success",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count,
        "message": "Data berhasil diupdate"
    }

# ==================== 4. DELETE ====================
@app.delete("/{database}/{collection}/delete")
async def delete_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None)
):
    """Menghapus satu dokumen berdasarkan filter"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON tidak valid")
    
    filter_data = body.get("filter")
    
    if not filter_data:
        raise HTTPException(status_code=400, detail="Filter tidak boleh kosong")
    
    # Handle ObjectId di filter
    if "_id" in filter_data and isinstance(filter_data["_id"], str):
        filter_data["_id"] = ObjectId(filter_data["_id"])
    
    db_client = client[database]
    collection_obj = db_client[collection]
    
    result = await collection_obj.delete_one(filter_data)
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    
    return {
        "status": "success",
        "deleted_count": result.deleted_count,
        "message": "Data berhasil dihapus"
    }

@app.delete("/{database}/{collection}/delete-many")
async def delete_many_data(
    database: str,
    collection: str,
    request: Request,
    x_api_token: str = Header(None)
):
    """Menghapus banyak dokumen berdasarkan filter"""
    if x_api_token != MY_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Token salah!")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="JSON tidak valid")
    
    filter_data = body.get("filter", {})
    
    # PERINGATAN: filter kosong akan menghapus SEMUA data!
    if not filter_data:
        raise HTTPException(status_code=400, detail="Filter tidak boleh kosong untuk keamanan. Gunakan {} jika ingin hapus semua")
    
    db_client = client[database]
    collection_obj = db_client[collection]
    
    result = await collection_obj.delete_many(filter_data)
    
    return {
        "status": "success",
        "deleted_count": result.deleted_count,
        "message": f"{result.deleted_count} data berhasil dihapus"
    }

# ==================== HEALTH CHECK ====================
@app.get("/")
async def health_check():
    # Test koneksi MongoDB
    try:
        await client.admin.command('ping')
        mongo_status = "connected"
    except:
        mongo_status = "disconnected"
    
    return {
        "status": "API ONLINE - FULL CRUD",
        "service": "running",
        "mongodb": mongo_status,
        "endpoints": {
            "create": ["POST /{database}/{collection}/insert", "POST /{database}/{collection}/insert-many"],
            "read": ["GET /{database}/{collection}/find", "GET /{database}/{collection}/{id}"],
            "update": ["POST /{database}/{collection}/upsert", "PUT /{database}/{collection}/update"],
            "delete": ["DELETE /{database}/{collection}/delete", "DELETE /{database}/{collection}/delete-many"]
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Tutup koneksi MongoDB saat aplikasi berhenti"""
    client.close()
