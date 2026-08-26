'''
home_library_v0 / main.py
-----------------------------
Version 3 - ISBN 추출

예광탄 방식을 활용한 아주 얇은 코드
'''
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Book
from services.recognition import lookup_metadata, normalize_isbn
from dotenv import load_dotenv
load_dotenv()

Base.metadata.create_all(engine)

app = FastAPI(title='우리집 책장 API')


@app.get('/books/lookup')
def lookup_book(isbn: str, db: Session = Depends(get_db)):
    validated_isbn = normalize_isbn(isbn)

    if not validated_isbn:
        raise HTTPException(422, '유효한 ISBN 형식이 아닙니다.')

    existing_book = db.scalar(select(Book).where(Book.isbn == validated_isbn))
    if existing_book:
        raise HTTPException(
            409,
            f'이미 등록된 책입니다: {existing_book.title} (id={existing_book.id})',
        )

    metadata = lookup_metadata(validated_isbn)

    if not metadata:
        raise HTTPException(404, '조회된 서지정보가 없습니다.')

    book = Book(
        title=metadata['title'],
        isbn=metadata['isbn'],
        author=metadata['author'],
        publisher=metadata['publisher'],
        cover_path=None,
        recognition_status='confirmed',
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return book


@app.get('/books')
def list_books(db: Session = Depends(get_db)):
    return db.scalars(select(Book)).all()