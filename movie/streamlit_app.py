'''
streamlit_app.py - Movie API 프론트엔드
'''
import requests
import streamlit as st

API_BASE = 'http://127.0.0.1:8000'

st.set_page_config(page_title='영화 박스오피스', page_icon='🎬')
st.title('🎬 영화 박스오피스')

tab_list, tab_add, tab_manage = st.tabs(['목록', '등록', '수정/삭제'])

# ===================== 목록 (조회) =====================
with tab_list:
    col1, col2, col3 = st.columns(3)
    keyword = col1.text_input('영화명 검색')
    genre = col2.text_input('장르')
    nation = col3.text_input('국가')

    if 'page' not in st.session_state:
        st.session_state.page = 0

    PAGE_SIZE = 12
    params = {'limit': PAGE_SIZE, 'offset': st.session_state.page * PAGE_SIZE}
    if keyword:
        params['keyword'] = keyword
    if genre:
        params['genre'] = genre
    if nation:
        params['nation'] = nation

    res = requests.get(f'{API_BASE}/movies', params=params)
    data = res.json() if res.status_code == 200 else {'total': 0, 'items': []}
    movies, total = data['items'], data['total']
    total_pages = max(1, -(-total // PAGE_SIZE))

    st.caption(f'전체 {total}개 · {st.session_state.page + 1} / {total_pages} 페이지')

    for m in movies:
        st.write(f'**{m["movie_nm"]}** · {m.get("open_dt") or "개봉일 미상"} · {m.get("genre") or "-"} · {m.get("nation") or "-"}')

    nav1, nav2, nav3 = st.columns([1, 2, 1])
    if nav1.button('◀ 이전', disabled=st.session_state.page == 0):
        st.session_state.page -= 1
        st.rerun()
    jump = nav2.number_input('페이지 이동', 1, total_pages, st.session_state.page + 1, label_visibility='collapsed')
    if nav2.button('이동'):
        st.session_state.page = jump - 1
        st.rerun()
    if nav3.button('다음 ▶', disabled=st.session_state.page + 1 >= total_pages):
        st.session_state.page += 1
        st.rerun()

# ===================== 등록 (추가) =====================
with tab_add:
    with st.form('add_form', clear_on_submit=True):
        movie_cd = st.text_input('영화 코드 *')
        movie_nm = st.text_input('영화명 *')
        open_dt = st.text_input('개봉일 (YYYYMMDD)')
        genre_in = st.text_input('장르')
        nation_in = st.text_input('국가')
        directors_in = st.text_input('감독 (쉼표 구분)')
        actors_in = st.text_input('배우 (쉼표 구분)')
        submitted = st.form_submit_button('등록')

    if submitted:
        if not movie_cd or not movie_nm:
            st.error('영화 코드와 영화명은 필수입니다.')
        else:
            body = {
                'movie_cd': movie_cd, 'movie_nm': movie_nm,
                'open_dt': open_dt or None, 'genre': genre_in or None, 'nation': nation_in or None,
                'directors': [n.strip() for n in directors_in.split(',') if n.strip()],
                'actors': [n.strip() for n in actors_in.split(',') if n.strip()],
            }
            res = requests.post(f'{API_BASE}/movies', json=body)
            if res.status_code == 201:
                st.success('등록 완료')
            else:
                st.error(res.json().get('detail', '등록 실패'))

# ===================== 수정/삭제 =====================
with tab_manage:
    search = st.text_input('수정/삭제할 영화 검색')

    if search:
        res = requests.get(f'{API_BASE}/movies', params={'keyword': search, 'limit': 20})
        movies = res.json()['items'] if res.status_code == 200 else []

        for m in movies:
            c1, c2, c3 = st.columns([4, 1, 1])
            c1.write(f'{m["movie_nm"]} ({m.get("open_dt") or "-"})')

            if c2.button('수정', key=f'e_{m["movie_cd"]}'):
                st.session_state.editing = m['movie_cd']
                st.rerun()

            if c3.button('삭제', key=f'd_{m["movie_cd"]}'):
                requests.delete(f'{API_BASE}/movies/{m["movie_cd"]}')
                st.success('삭제됨')
                st.rerun()

            if st.session_state.get('editing') == m['movie_cd']:
                with st.form(f'edit_{m["movie_cd"]}'):
                    new_nm = st.text_input('영화명', m['movie_nm'])
                    new_genre = st.text_input('장르', m.get('genre') or '')
                    save = st.form_submit_button('저장')
                if save:
                    requests.patch(f'{API_BASE}/movies/{m["movie_cd"]}', json={'movie_nm': new_nm, 'genre': new_genre})
                    st.session_state.editing = None
                    st.success('수정됨')
                    st.rerun()