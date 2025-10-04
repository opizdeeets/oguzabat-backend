import uuid
from pathlib import Path
from fastapi import UploadFile
import aiofiles

# ---------------- КОНФИГУРАЦИЯ ----------------
# BASE_DIR теперь всегда указывает на корень проекта, а не на папку app
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # .../oguzabat
UPLOAD_ROOT = BASE_DIR / "uploads"
UPLOAD_ROOT.mkdir(exist_ok=True, parents=True)

# ---------------- СОХРАНЕНИЕ ФАЙЛА ----------------
async def save_upload_file(upload_file: UploadFile, sub_dir: str = "portfolio") -> str:
    """
    Сохраняет UploadFile в поддиректорию uploads/<sub_dir> и генерирует уникальное имя.
    Возвращает относительный URL для фронта, безопасный для базы данных.
    """
    # Создаём директорию uploads/<sub_dir>
    upload_path = UPLOAD_ROOT / sub_dir
    upload_path.mkdir(parents=True, exist_ok=True)

    # Получаем расширение файла и создаём уникальное имя
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = upload_path / unique_filename

    # Записываем файл на диск асинхронно
    # На всякий случай перематываем внутренний файл в начало (если он был прочитан ранее)
    try:
        # UploadFile.file — это обычно SpooledTemporaryFile с sync seek
        upload_file.file.seek(0)
    except Exception:
        # В редких случаях объект может не иметь .file/seak — игнорируем
        pass

    print(f"Saving upload file '{upload_file.filename}' to '{file_path}'")
    async with aiofiles.open(file_path, "wb") as out_file:
        while True:
            chunk = await upload_file.read(1024)
            if not chunk:
                break
            await out_file.write(chunk)

    # Возвращаем путь, который можно хранить в БД и отдавать фронту
    # Пример: 'uploads/portfolio/<uuid>.jpg'
    return str(file_path.relative_to(BASE_DIR))

# ---------------- УДАЛЕНИЕ ФАЙЛА ----------------
async def delete_upload_file(file_url: str) -> None:
    """
    Удаляет файл по относительному пути относительно BASE_DIR.
    """
    file_path = BASE_DIR / file_url
    if file_path.exists() and file_path.is_file():
        try:
            file_path.unlink()
        except Exception as e:
            print(f"Warning: failed to delete file {file_path}: {e}")
