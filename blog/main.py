from schema.response import BlogResponse
from schema.request import BlogCreateRequest, BlogUpdateRequest
from fastapi import FastAPI, status, HTTPException
from sqlalchemy import select
from database.db_connection import engine, SessionFactory
from database.orm import Base
from models import Blog

Base.metadata.create_all(bind=engine)

app = FastAPI()

# 전체 게시글 조회
@app.get(
    '/',
    response_model=list[BlogResponse],
    status_code=status.HTTP_200_OK
)
def get_blogs_handler():
    session = SessionFactory()
    try:
        stmt = select(Blog)
        blogs = session.execute(stmt).scalars().all()
        return blogs
    finally:
        session.close()

# 단일 게시글 조회
@app.get(
    '/{blog_id}',
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK
)
def get_blog_handler(blog_id: int):
    session = SessionFactory()
    try:
        stmt = select(Blog).where(Blog.id == blog_id)
        blog = session.execute(stmt).scalars().first()
        if blog:
            return blog
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found'
        )
    finally:
        session.close()

# 게시글 생성
@app.post(
    '/',
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED
)
def create_blog_handler(body: BlogCreateRequest):
    session = SessionFactory()
    try:
        blog = Blog(
            title = body.title,
            content = body.content
        )
        session.add(blog)
        session.commit()
        return blog
    finally:
        session.close()

# 게시글 수정
@app.patch(
    '/{blog_id}',
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK
)
def update_blog_handler(blog_id: int, body: BlogUpdateRequest):
    session = SessionFactory()
    try:
        stmt = select(Blog).where(Blog.id == blog_id)
        blog = session.execute(stmt).scalars().first()
        if blog:
            if body.title is not None:
                blog.title = body.title
            if body.content is not None:
                blog.content = body.content
            session.commit()
            return blog
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')
    finally:
        session.close()
    

# 게시글 삭제
@app.delete(
    '/{blog_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_blog_handler(blog_id: int):
    session = SessionFactory()
    try:
        stmt = select(Blog).where(Blog.id == blog_id)
        blog = session.execute(stmt).scalars().first()
        if blog:
            session.delete(blog)
            session.commit()
            return
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Blog not found')
    finally:
        session.close()