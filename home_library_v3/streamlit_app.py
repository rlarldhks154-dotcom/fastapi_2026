'''
home_library_v2 / streamlit_app.py
-----------------------------
중복 등록 시 안내 메시지로 표시
'''
import os
import requests
import streamlit as st

API = os.getenv('API_URL', 'http://localhost:8000')


def show_response(r: requests.Response):
    if r.ok:
        st.success(f'등록됨: {r.json()["title"]}')
        return

    if r.status_code == 409:
        existing = r.json()['detail']['existing_book']
        st.info(
            f'📚 이미 서재에 있는 책이에요!\n\n'
            f'**{existing["title"]}**\n\n'
            f'저자: {existing["author"] or "정보 없음"}  \n'
            f'출판사: {existing["publisher"] or "정보 없음"}'
        )
        return

    detail = r.json().get('detail', '')
    st.error(f'실패 ({r.status_code}): {detail}')


st.title('우리집 책장 (개발 중)')

st.header('1단계: ISBN으로 빠르게 등록해보기')

isbn_input = st.text_input('ISBN 입력 (예: 9791190090018)')

if st.button('조회 후 등록'):
    if not isbn_input:
        st.warning('ISBN을 입력해주세요!')
    else:
        r = requests.get(f'{API}/books/lookup', params={'isbn': isbn_input})
        show_response(r)

st.divider()

st.header('2단계: ISBN + 표지 사진 함께 등록하기')

with st.form('register_form'):
    form_isbn = st.text_input('ISBN 입력')
    form_image = st.file_uploader('표지 사진')
    submitted = st.form_submit_button('등록하기')

if submitted:
    if not form_isbn:
        st.warning('ISBN을 입력해주세요!')
    elif form_image is None:
        st.warning('표지 사진을 선택해주세요!')
    else:
        r = requests.post(
            f'{API}/books/register',
            data={'isbn': form_isbn},
            files={'image': (form_image.name, form_image.getvalue(), form_image.type)},
        )
        show_response(r)

st.divider()

st.subheader('등록된 책')
for book in requests.get(f'{API}/books').json():
    st.write(f'{book["title"]} ({book["recognition_status"]})')