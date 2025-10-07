import uuid
import shutil
import mimetypes
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
import aiofiles
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# ---------------- КОНФИГУРАЦИЯ ----------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # корень проекта
UPLOAD_ROOT = BASE_DIR / "uploads"
UPLOAD_ROOT.mkdir(exist_ok=True, parents=True)

# MIME-типы и лимиты
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_PDF_TYPES = {"application/pdf"}
IMAGE_MAX_MB = 2
PDF_MAX_MB = 10

# ---------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------------
async def _save_file(upload_file: UploadFile, destination: Path) -> None:
    """Асинхронно сохраняет файл на диск."""
    upload_file.file.seek(0)
    async with aiofiles.open(destination, "wb") as buffer:
        while True:
            chunk = await upload_file.read(1024 * 64)
            if not chunk:
                break
            await buffer.write(chunk)

def _validate_file(upload_file: UploadFile) -> None:
    """Проверяет MIME-тип и размер файла в зависимости от типа."""
    mime_type, _ = mimetypes.guess_type(upload_file.filename)
    if mime_type in ALLOWED_IMAGE_TYPES:
        max_mb = IMAGE_MAX_MB
    elif mime_type in ALLOWED_PDF_TYPES:
        max_mb = PDF_MAX_MB
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат файла ({mime_type or 'неизвестен'}). "
                   f"Разрешены: {', '.join(ALLOWED_IMAGE_TYPES | ALLOWED_PDF_TYPES)}"
        )

    upload_file.file.seek(0, 2)
    size = upload_file.file.tell()
    upload_file.file.seek(0)
    if size > max_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Файл слишком большой. Максимум {max_mb} МБ для {mime_type.split('/')[0]}"
        )

# ---------------- ОСНОВНЫЕ ФУНКЦИИ ----------------
async def save_uploaded_file(upload_file: UploadFile, sub_dir: str) -> str:
    """Сохраняет один файл и возвращает относительный путь."""
    if not upload_file:
        raise HTTPException(status_code=400, detail="Файл не передан.")
    _validate_file(upload_file)

    upload_path = UPLOAD_ROOT / sub_dir
    upload_path.mkdir(parents=True, exist_ok=True)

    file_ext = Path(upload_file.filename).suffix or ".dat"
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_path / unique_filename

    try:
        await _save_file(upload_file, file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения файла: {e}")

    return str(file_path.relative_to(BASE_DIR))

async def save_uploaded_files(upload_files: list[UploadFile], sub_dir: str) -> list[str]:
    """Сохраняет массив файлов (для галереи) и возвращает список относительных путей."""
    if not upload_files:
        return []
    saved_paths = []
    for f in upload_files:
        path = await save_uploaded_file(f, sub_dir)
        saved_paths.append(path)
    return saved_paths

async def delete_uploaded_file(file_url: str) -> None:
    """Удаляет один файл безопасно."""
    if not file_url:
        return
    file_path = BASE_DIR / file_url
    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except Exception as e:
            print(f"[Warning] Не удалось удалить файл {file_path}: {e}")

async def replace_uploaded_file(old_file_url: str, new_file: UploadFile | None, sub_dir: str) -> str:
    """Заменяет старый файл новым."""
    if new_file is None:
        return old_file_url
    await delete_uploaded_file(old_file_url)
    return await save_uploaded_file(new_file, sub_dir)

async def update_entity(
    db, entity_id: int, entity_in, crud_update_func,
    file: UploadFile = None, file_sub_dir: str = None
):
    """Универсальное обновление сущности с поддержкой файла."""
    updated_data = entity_in.dict(exclude_unset=True)

    if file is not None and file_sub_dir is not None:
        new_file_path = await save_uploaded_file(file, file_sub_dir)
        old_entity = await crud_update_func(db, entity_id, {})  # старый объект
        old_path_attr = file_sub_dir + "_path"
        if old_entity and getattr(old_entity, old_path_attr, None):
            await delete_uploaded_file(getattr(old_entity, old_path_attr))
        updated_data[old_path_attr] = new_file_path

    try:
        updated_entity = await crud_update_func(db, entity_id, updated_data)
        if not updated_entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found")
        return updated_entity
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate or invalid fields")
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        print("Unexpected error in update_entity:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
