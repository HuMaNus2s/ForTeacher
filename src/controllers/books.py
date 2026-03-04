from fastapi import APIRouter, HTTPException, Query
import json
from pathlib import Path
from typing import List, Dict, Optional

router = APIRouter(prefix="/books", tags=["books"])

DATA_PATH = Path(__file__).parent.parent / "data" / "books.json"


def load_books() -> List[Dict]:
    if not DATA_PATH.exists():
        return []
    
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("Данные в файле должны быть списком")
            return data
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка чтения файла книг: {str(e)}"
        )


def save_books(books: List[Dict]) -> None:
    try:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with DATA_PATH.open("w", encoding="utf-8") as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось сохранить файл книг: {str(e)}"
        )

@router.get("/")
async def get_books(
    sorting: Optional[str] = Query(
        None,
        description="asc (А~Я) или desc (Я~А)",
        pattern="^(asc|desc)?$"
    )
):
    books = load_books()
    
    if sorting == "asc":
        books = sorted(books, key=lambda x: x.get("title", "").lower())
    elif sorting == "desc":
        books = sorted(books, key=lambda x: x.get("title", "").lower(), reverse=True)
    
    return {
        "books": books,
        "total": len(books)
    }

@router.get("/{book_id}")
async def get_book_by_id(book_id: int):
    books = load_books()
    for book in books:
        if book.get("id") == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга с таким id не найдена")

@router.post("/", status_code=201)
async def create_book(book: Dict):
    required = {"title", "author", "genre", "price"}
    if not required.issubset(book.keys()):
        raise HTTPException(
            status_code=422,
            detail=f"Отсутствуют обязательные поля: {', '.join(required - set(book.keys()))}"
        )
    
    if not isinstance(book.get("price"), (int, float)):
        raise HTTPException(status_code=422, detail="Поле price должно быть числом")
    
    books = load_books()

    existing_ids = {b.get("id") for b in books if isinstance(b.get("id"), int)}
    new_id = max(existing_ids, default=0) + 1
    
    book["id"] = new_id
    books.append(book)
    save_books(books)
    
    return {"message": "Книга добавлена", "book": book}

@router.put("/{book_id}")
async def update_book(book_id: int, updated_data: Dict):
    books = load_books()
    
    for i, book in enumerate(books):
        if book.get("id") == book_id:
            for key in ["title", "author", "genre", "price"]:
                if key in updated_data:
                    book[key] = updated_data[key]
            
            save_books(books)
            return {"message": "Книга обновлена", "book": book}
    
    raise HTTPException(status_code=404, detail="Книга не найдена")

@router.delete("/{book_id}")
async def delete_book(book_id: int):
    books = load_books()
    original_len = len(books)
    books = [b for b in books if b.get("id") != book_id]
    
    if len(books) == original_len:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    
    save_books(books)
    return {"message": f"Книга с id={book_id} удалена"}