from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import uuid
import os
import shutil

from ..config import get_settings
from ..database import get_db, Document
from ..services import DocumentProcessor, VectorStoreService
from ..models import DocumentResponse

router = APIRouter(prefix="/documents", tags=["Documents"])
settings = get_settings()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process a document (Excel, CSV, PDF, TXT)."""
    # Validate file extension
    extension = Path(file.filename).suffix.lower()
    if extension not in DocumentProcessor.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}. Supported: {DocumentProcessor.SUPPORTED_EXTENSIONS}",
        )

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size = settings.max_file_size_mb * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
        )

    # Create upload directory if not exists
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Save file
    document_id = str(uuid.uuid4())
    file_path = Path(settings.upload_dir) / f"{document_id}{extension}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Process document
        processor = DocumentProcessor()
        products = processor.process_file(file_path)

        if not products:
            raise HTTPException(status_code=400, detail="No products found in file")

        # Store in vector database
        vector_store = VectorStoreService()
        vector_store.add_products(products, document_id)

        # Upsert products into SQLite (Dynamic Data)
        from ..database import Product, get_sl_time
        
        for p in products:
            p_name = p.get("product_name", "").strip()
            p_variant = p.get("variant", "").strip()
            
            # Create composite ID: "ProductName_Variant" or just "ProductName"
            if p_variant:
                p_id = f"{p_name}_{p_variant}"
            else:
                p_id = p_name
            
            # Normalize ID for consistency
            p_id = p_id.lower().replace(" ", "_")
                
            # Check if exists
            existing_product = db.query(Product).filter(Product.id == p_id).first()
            
            if existing_product:
                # Update
                existing_product.price_lkr = p.get("price_lkr", 0.0)
                existing_product.available = p.get("available", "Yes")
                existing_product.last_updated = get_sl_time()
            else:
                # Create
                new_product = Product(
                    id=p_id,
                    product_name=p_name,
                    variant=p_variant,
                    price_lkr=p.get("price_lkr", 0.0),
                    available=p.get("available", "Yes"),
                )
                db.add(new_product)
        
        # Save to database (Document record)
        doc = Document(
            id=document_id,
            filename=file.filename,
            file_type=extension,
            file_path=str(file_path),
            product_count=len(products),
            status="processed",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        return DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            product_count=doc.product_count,
            uploaded_at=doc.uploaded_at,
            status=doc.status,
        )

    except Exception as e:
        # Cleanup on error
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            file_type=doc.file_type,
            product_count=doc.product_count,
            uploaded_at=doc.uploaded_at,
            status=doc.status,
        )
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get a specific document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        product_count=doc.product_count,
        uploaded_at=doc.uploaded_at,
        status=doc.status,
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document and its vectors."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete from vector store
    vector_store = VectorStoreService()
    vector_store.delete_by_document_id(document_id)

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Delete from database
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully", "id": document_id}


@router.get("/stats/collection")
async def get_collection_stats():
    """Get vector collection statistics."""
    vector_store = VectorStoreService()
    return vector_store.get_collection_info()
