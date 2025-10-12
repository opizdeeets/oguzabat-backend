import uuid
import mimetypes
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
from typing import Optional
from pydantic import BaseModel

UPLOAD_PATH_MAP = {
    "logos": "logo_path",
    "company_logos": "logo_path",  # для совместимости с вашей текущей папкой
    "project_gallery": "gallery",   # пример для проектов
    "user_avatars": "avatar_path",  # пример для пользователей
}


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


def _validate_file(upload_file: UploadFile, max_mb: int = 2) -> None:
    """
    Проверяет MIME-тип и размер файла.
    По умолчанию лимит 2 МБ, можно переопределить через max_mb.
    """
    mime_type, _ = mimetypes.guess_type(upload_file.filename)
    if mime_type not in ALLOWED_IMAGE_TYPES | ALLOWED_PDF_TYPES:
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
async def save_uploaded_file(upload_file: UploadFile, sub_dir: str, max_mb: int = 2) -> str:
    """Сохраняет один файл и возвращает относительный путь. Лимит размера можно задать через max_mb."""
    if not upload_file:
        raise HTTPException(status_code=400, detail="Файл не передан.")
    _validate_file(upload_file, max_mb=max_mb)

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


async def save_uploaded_files(upload_files: list[UploadFile], sub_dir: str, max_mb: int = 2) -> list[str]:
    """Сохраняет массив файлов и возвращает список относительных путей. Лимит размера можно задать через max_mb."""
    if not upload_files:
        return []
    saved_paths = []
    for f in upload_files:
        path = await save_uploaded_file(f, sub_dir, max_mb=max_mb)
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
    db: AsyncSession,
    entity_id: int,
    entity_in,  # Pydantic-модель или dict
    crud_update_func,
    file: Optional[UploadFile] = None,
    sub_dir: Optional[str] = None,
    file_field: Optional[str] = None
):
    """
    Универсальный метод обновления сущностей с поддержкой файлов.

    Аргументы:
    - db: AsyncSession
    - entity_id: id обновляемой записи
    - entity_in: Pydantic-модель или dict с обновляемыми полями
    - crud_update_func: функция CRUD для обновления записи
    - file: загружаемый файл (опционально)
    - sub_dir: подкаталог для файла (используется для пути)
    - file_field: имя поля модели, куда сохраняется путь (если отличается от sub_dir+"_path")
    """

    # 1️⃣ Преобразуем данные в словарь
    if isinstance(entity_in, BaseModel):
        updated_data = {k: v for k, v in entity_in.model_dump(exclude_unset=True).items() if v is not None}
    elif isinstance(entity_in, dict):
        updated_data = {k: v for k, v in entity_in.items() if v is not None}
    else:
        raise TypeError("entity_in должен быть Pydantic-моделью или dict")

    # 2️⃣ Обработка загруженного файла
    if file is not None:
        if not sub_dir:
            raise ValueError("sub_dir должен быть указан при загрузке файла")

        old_entity = await crud_update_func(db, entity_id, {})  # получить старые данные

        # Определяем поле модели для хранения пути к файлу
        old_path_attr = file_field or f"{sub_dir}_path"

        if not hasattr(old_entity, old_path_attr):
            raise ValueError(f"Нет соответствия поля модели для sub_dir='{sub_dir}'")

        # Удаляем старый файл, если есть
        old_file_path = getattr(old_entity, old_path_attr, None)
        if old_file_path:
            await delete_uploaded_file(old_file_path)

        # Сохраняем новый файл
        new_file_path = await save_uploaded_file(file, sub_dir=sub_dir)
        updated_data[old_path_attr] = new_file_path

    # 3️⃣ Обновление сущности
    try:
        updated_entity = await crud_update_func(db, entity_id, updated_data)
        if not updated_entity:
            raise HTTPException(status_code=404, detail=f"Entity with id={entity_id} not found")
        return updated_entity

    except HTTPException:
        raise
    except Exception as e:
        print(f"[update_entity] Unexpected error: {type(e).__name__} → {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


