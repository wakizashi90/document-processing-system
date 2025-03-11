from fastapi import FastAPI, UploadFile, File, HTTPException
import models
import crud


app = FastAPI()


@app.post("/process-ocr")
async def process_ocr(file: UploadFile = File(...)):
    return await crud.process_ocr_func(file)


@app.patch("/update-ocr-text")
async def update_ocr_text(update_request: models.OCRUpdateRequest):
    try:
        update_successful = await crud.update_ocr_text_fragment(
            document_id=update_request.document_id,
            original_text=update_request.original_text,
            updated_text=update_request.updated_text
        )

        if not update_successful:
            raise HTTPException(status_code=404, detail="Failed to update document")

        return {"message": "OCR text updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating OCR text: {str(e)}")
