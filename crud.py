from fastapi import HTTPException, status, UploadFile, File
from models import OCRText
from bson import ObjectId
from config import ocr_text_collection
from database import database
from langdetect import detect
import shutil
import models
import pymupdf as fitz
import pytesseract
import os


UPLOAD_DIR = "./uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


async def get_db_collection(collection_name: str):
    collection = database.get_collection(collection_name)
    if collection is None:
        raise HTTPException(
            detail="No collection found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return collection


async def create_ocr_document(ocr_document: OCRText) -> ObjectId:
    collection = await get_db_collection(ocr_text_collection)
    result = await collection.insert_one(ocr_document.dict(by_alias=True))
    return result.inserted_id


def extract_text_from_pdf(file_path: str) -> str:
    try:
        doc = fitz.open(file_path)
        text = ""

        for page_num in range(len(doc)):
            page = doc[page_num]
            text += page.get_text("text")

        return text
    finally:
        doc.close()


def extract_text_from_image(file_path: str) -> str:
    return pytesseract.image_to_string(file_path)


async def process_ocr_func(file: UploadFile = File(...)):
    try:
        file_ext = file.filename.split(".")[-1].lower()

        if file_ext not in ("png", "jpg", "jpeg", "pdf"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PNG, JPG, and PDF are supported.",
            )

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file_ext == "pdf":
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_from_image(file_path)

        detected_language = detect(extracted_text)

        os.remove(file_path)

        return {
            "extracted_text": extracted_text,
            "detected_language": detected_language,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR service error: {str(e)}")


async def update_ocr_text_fragment(
    document_id: str, original_text: str, updated_text: str
) -> bool:
    try:
        document_id = ObjectId(document_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    collection = await get_db_collection(ocr_text_collection)
    ocr_document = await collection.find_one({"_id": document_id})

    if not ocr_document:
        raise HTTPException(status_code=404, detail="Document not found")

    updated_recognized_text = ocr_document["recognized_text"].replace(
        original_text, updated_text
    )

    result = await collection.update_one(
        {"_id": document_id}, {"$set": {"recognized_text": updated_recognized_text}}
    )

    return result.modified_count > 0
