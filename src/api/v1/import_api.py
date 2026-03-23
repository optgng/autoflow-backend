"""Import endpoint with file validation (SEC-06)."""
from fastapi import APIRouter, File, HTTPException, UploadFile, status

router = APIRouter(prefix="/import", tags=["Import"])

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME = {"application/pdf"}


def _validate_pdf(content: bytes) -> None:
    """SEC-06: Basic PDF header + no embedded JS check."""
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File does not appear to be a valid PDF",
        )
    if b"/JS" in content or b"/JavaScript" in content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PDF contains potentially dangerous content",
        )


@router.post("/pdf")
async def import_pdf(file: UploadFile = File(...)) -> dict:
    """Import Sberbank PDF statement."""
    # SEC-06: MIME type check
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are accepted",
        )

    content = await file.read()

    # SEC-06: Size check
    if len(content) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="PDF file exceeds 10 MB limit",
        )

    _validate_pdf(content)

    # TODO: hand off to import_service as background task
    return {"status": "accepted", "size_bytes": len(content)}
