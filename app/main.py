from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
import aiofiles
import os
from pathlib import Path
from contextlib import asynccontextmanager

from rag_sdk import RAGManager
from .models import QueryRequest, QueryResponse, DocumentResponse


# Логирование переменных окружения при запуске
print("=" * 60)
print("APP MAIN - Environment Variables at startup:")
print(f"PROVIDER: {os.getenv('PROVIDER', 'NOT SET')}")
print(f"GIGA_CHAT_AUTH_KEY: {'SET' if os.getenv('GIGA_CHAT_AUTH_KEY') else 'NOT SET'}")
print(f"GIGA_CHAT_MODEL: {os.getenv('GIGA_CHAT_MODEL', 'NOT SET')}")
print(f"OLLAMA_HOST: {os.getenv('OLLAMA_HOST', 'NOT SET')}")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT SET')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT', 'NOT SET')}")
print("=" * 60)

rag_manager = RAGManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("APP MAIN - Initializing RAG Manager...")
    await rag_manager.initialize()
    print("APP MAIN - RAG Manager initialized successfully")
    yield
    print("APP MAIN - Closing RAG Manager...")
    await rag_manager.close()
    print("APP MAIN - RAG Manager closed")


app = FastAPI(title="RAG SDK API", version="1.0.0", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = Path("app/static/index.html")
    if html_path.exists():
        async with aiofiles.open(html_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    return HTMLResponse("<h1>RAG SDK</h1><p>Frontend not found</p>")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    print(f"\n[API] ========== UPLOAD REQUEST ==========")
    print(f"[API] Filename: {file.filename}")
    print(f"[API] Content-Type: {file.content_type}")
    try:
        file_path = UPLOAD_DIR / file.filename
        print(f"[API] Saving to: {file_path}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        file_size = os.path.getsize(file_path)
        print(f"[API] File saved: {file_size} bytes")
        
        document_id = await rag_manager.add_document(str(file_path), file.filename)
        
        print(f"[API] Upload successful: document_id={document_id}")
        print(f"[API] ========================================\n")
        return JSONResponse({
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "message": f"Файл {file.filename} успешно загружен и обработан"
        })
        
    except Exception as e:
        import traceback
        error_detail = f"Ошибка при загрузке файла: {str(e)}\n{traceback.format_exc()}"
        print(f"[API] ERROR: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")


@app.get("/api/documents", response_model=List[DocumentResponse])
async def get_documents():
    try:
        documents = await rag_manager.get_documents()
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении списка документов: {str(e)}")


@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int):
    try:
        document = await rag_manager.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Документ не найден")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении документа: {str(e)}")


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: int):
    print(f"\n[API] ========== DELETE REQUEST ==========")
    print(f"[API] Document ID: {document_id}")
    try:
        document = await rag_manager.get_document(document_id)
        if not document:
            print(f"[API] ERROR: Document not found")
            raise HTTPException(status_code=404, detail="Документ не найден")
        
        print(f"[API] Deleting document: {document['filename']}")
        await rag_manager.delete_document(document_id)
        
        file_path = UPLOAD_DIR / document['filename']
        if file_path.exists():
            os.remove(file_path)
            print(f"[API] Physical file deleted: {file_path}")
        
        print(f"[API] Delete successful")
        print(f"[API] ========================================\n")
        return JSONResponse({
            "success": True,
            "message": f"Документ {document['filename']} успешно удален"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении документа: {str(e)}")


@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    print(f"\n[API] ========== CHAT REQUEST ==========")
    print(f"[API] Query: {request.query}")
    print(f"[API] Document ID: {request.document_id}")
    print(f"[API] Context limit: {request.context_limit or 3}")
    try:
        if not request.query or not request.query.strip():
            print(f"[API] ERROR: Empty query")
            raise HTTPException(status_code=400, detail="Вопрос не может быть пустым")
            
        result = await rag_manager.generate_answer(
            query=request.query,
            document_id=request.document_id,
            context_limit=request.context_limit or 3
        )
        
        print(f"[API] Chat response generated successfully")
        print(f"[API] ======================================\n")
        return QueryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Ошибка при обработке запроса: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Вывод в логи
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {str(e)}")


@app.post("/api/search")
async def search(request: QueryRequest):
    print(f"\n[API] ========== SEARCH REQUEST ==========")
    print(f"[API] Query: {request.query}")
    print(f"[API] Document ID: {request.document_id}")
    print(f"[API] Limit: {request.context_limit or 5}")
    try:
        if not request.query or not request.query.strip():
            print(f"[API] ERROR: Empty query")
            raise HTTPException(status_code=400, detail="Запрос не может быть пустым")
            
        results = await rag_manager.search(
            query=request.query,
            document_id=request.document_id,
            limit=request.context_limit or 5
        )
        
        print(f"[API] Search successful: {len(results)} results")
        print(f"[API] ========================================\n")
        return JSONResponse({
            "success": True,
            "results": results
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при поиске: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

