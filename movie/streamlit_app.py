'''
========================================================================================
streamlit_app.py

Movie API(FastAPI)를 호출해서 화면으로 보여주는 프론트엔드
FastAPI는 계속 uvicorn으로 실행 중이어야 하고, Streamlit도 별도로 streamlit run 실행 필요
========================================================================================
'''
import streamlit as st
import requests

API_BASE = 'http://127.0.0.1:8000'

st.set_page_config(
    page_title='영화 박스오피스 조회',
    page_icon='🎬',
    layout='wide',
)

st.markdown('''
<style>
.movie-card {
    padding: 14px 18px;
    border-radius: 12px;
    margin-bottom: 10px;
    border: 1px solid #e6e6e6;
    background-color: #fff;
}
.movie-title {
    font-size: 18px;
    font-weight: 700;
}
.movie-meta {
    color: #666;
    font-size: 13px;
}
</style>
''', unsafe_allow_html=True)

# -----------------------------------------------------------------------------------------
# 세션 상태 초기화 (선택된 영화 상세보기용)
# -----------------------------------------------------------------------------------------
if 'selected_movie_cd' not in st.session_state:
    st.session_state.selected_movie_cd = None


def extract_error_message(res: requests.Response, fallback: str) -> str:
    """FastAPI 에러 응답에서 사람이 읽을 수 있는 메시지만 뽑아낸다."""
    try:
        detail = res.json().get('detail', fallback)
    except requests.exceptions.JSONDecodeError:
        return f'서버 오류 (status {res.status_code}). uvicorn 터미널을 확인해주세요.'

    if isinstance(detail, list):
        messages = []
        for err in detail:
            msg = err.get('msg', '') if isinstance(err, dict) else str(err)
            msg = msg.replace('Value error, ', '')
            messages.append(msg)
        return '\n'.join(messages) if messages else fallback

    return str(detail)


def check_server() -> bool:
    try:
        requests.get(f'{API_BASE}/movies', params={'limit': 1}, timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        return False


# -----------------------------------------------------------------------------------------
# 서버 연결 확인
# -----------------------------------------------------------------------------------------
if not check_server():
    st.error('FastAPI 서버에 연결할 수 없습니다. `uv run uvicorn main:app --reload`로 서버를 먼저 실행해주세요.')
    st.stop()

# -----------------------------------------------------------------------------------------
# 상단 헤더
# -----------------------------------------------------------------------------------------
st.title('🎬 영화 박스오피스 조회')
st.caption('KOBIS 영화 상세정보 데이터 기반')

tab_list, tab_add, tab_manage = st.tabs(['영화 목록', '새 영화 등록', '수정/삭제 관리'])

# =========================================================================================
# 탭 1: 영화 목록 (조회)
# =========================================================================================
with tab_list:
    # ----검색/필터 영역----------------------------------------------------------------
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([3, 2, 2, 1])
    with filter_col1:
        keyword = st.text_input('영화명 검색', placeholder='예: 하얼빈')
    with filter_col2:
        genre = st.text_input('장르 필터', placeholder='예: 드라마')
    with filter_col3:
        nation = st.text_input('국가 필터', placeholder='예: 한국')
    with filter_col4:
        st.write('')
        st.write('')
        search_clicked = st.button('검색', use_container_width=True)

    # ----페이지네이션 상태----------------------------------------------------------------
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if search_clicked:
        st.session_state.page = 0  # 새로 검색하면 1페이지로 리셋

    PAGE_SIZE = 12
    offset = st.session_state.page * PAGE_SIZE

    # ----목록 조회----------------------------------------------------------------
    params = {'limit': PAGE_SIZE, 'offset': offset}
    if keyword:
        params['keyword'] = keyword
    if genre:
        params['genre'] = genre
    if nation:
        params['nation'] = nation

    res = requests.get(f'{API_BASE}/movies', params=params)

    if res.status_code != 200:
        st.error(extract_error_message(res, '목록을 불러오지 못했습니다.'))
        movies = []
        total = 0
    else:
        data = res.json()
        movies = data['items']
        total = data['total']

    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)  # 올림 나눗셈

    # 현재 페이지가 전체 페이지 수를 넘어가면 마지막 페이지로 보정 (필터 바뀌어서 결과가 줄었을 때)
    if st.session_state.page >= total_pages:
        st.session_state.page = total_pages - 1

    st.divider()

    if not movies:
        st.info('조건에 맞는 영화가 없습니다.')
    else:
        # 3열 그리드로 카드 표시
        cols = st.columns(3)
        for i, movie in enumerate(movies):
            with cols[i % 3]:
                st.markdown(f'''
                <div class="movie-card">
                    <div class="movie-title">{movie["movie_nm"]}</div>
                    <div class="movie-meta">
                        개봉일: {movie.get("open_dt") or "정보없음"}<br>
                        장르: {movie.get("genre") or "정보없음"}<br>
                        국가: {movie.get("nation") or "정보없음"}<br>
                        등급: {movie.get("watch_grade") or "정보없음"}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                if st.button('상세보기', key=f'detail_{movie["movie_cd"]}', use_container_width=True):
                    st.session_state.selected_movie_cd = movie['movie_cd']
                    st.rerun()

    # ----페이지네이션 버튼----------------------------------------------------------------
    st.divider()
    page_col1, page_col2, page_col3, page_col4 = st.columns([1, 2, 1.2, 1])

    with page_col1:
        if st.session_state.page > 0:
            if st.button('◀ 이전'):
                st.session_state.page -= 1
                st.rerun()

    with page_col2:
        st.markdown(
            f'<p style="text-align:center;">페이지 {st.session_state.page + 1} / {total_pages} (전체 {total}개)</p>',
            unsafe_allow_html=True,
        )

    with page_col3:
        # 원하는 페이지 번호를 직접 입력해서 이동
        target_page = st.number_input(
            '페이지 이동',
            min_value=1,
            max_value=total_pages,
            value=st.session_state.page + 1,
            step=1,
            label_visibility='collapsed',
            key='page_jump_input',
        )
        if st.button('이동', use_container_width=True):
            st.session_state.page = target_page - 1
            st.rerun()

    with page_col4:
        if st.session_state.page + 1 < total_pages:
            if st.button('다음 ▶'):
                st.session_state.page += 1
                st.rerun()

    # ----상세보기 모달 (선택된 영화가 있으면)----------------------------------------------
    if st.session_state.selected_movie_cd:
        detail_res = requests.get(f'{API_BASE}/movies/{st.session_state.selected_movie_cd}')

        with st.expander(f'📽️ 상세정보', expanded=True):
            if detail_res.status_code == 200:
                d = detail_res.json()
                st.subheader(d['movie_nm'])
                if d.get('movie_nm_en'):
                    st.caption(d['movie_nm_en'])

                detail_col1, detail_col2 = st.columns(2)
                with detail_col1:
                    st.write(f'**개봉일**: {d.get("open_dt") or "정보없음"}')
                    st.write(f'**상영시간**: {d.get("show_tm") or "정보없음"}분')
                    st.write(f'**장르**: {d.get("genre") or "정보없음"}')
                    st.write(f'**제작국가**: {d.get("nation") or "정보없음"}')
                with detail_col2:
                    st.write(f'**관람등급**: {d.get("watch_grade") or "정보없음"}')
                    st.write(f'**감독**: {", ".join(d.get("directors", [])) or "정보없음"}')
                    st.write(f'**배우**: {", ".join(d.get("actors", [])) or "정보없음"}')

                # ----수정/삭제 (여기에 각자 기능 이어서 확장 가능)----------------------------
                st.divider()
                delete_col1, delete_col2 = st.columns([1, 4])
                with delete_col1:
                    if st.button('🗑️ 삭제', type='secondary'):
                        del_res = requests.delete(f'{API_BASE}/movies/{d["movie_cd"]}')
                        if del_res.status_code == 204:
                            st.success('삭제되었습니다.')
                            st.session_state.selected_movie_cd = None
                            st.rerun()
                        else:
                            st.error(extract_error_message(del_res, '삭제에 실패했습니다.'))
            else:
                st.error('상세정보를 불러오지 못했습니다.')

            if st.button('닫기'):
                st.session_state.selected_movie_cd = None
                st.rerun()

# =========================================================================================
# 탭 2: 새 영화 등록 (추가)
# =========================================================================================
with tab_add:
    st.subheader('새 영화 등록')

    with st.form('add_movie_form', clear_on_submit=True):
        form_col1, form_col2 = st.columns(2)
        with form_col1:
            new_movie_cd = st.text_input('영화 코드 (movie_cd) *', placeholder='예: 99999999')
            new_movie_nm = st.text_input('영화명 *', placeholder='예: 테스트 영화')
            new_movie_nm_en = st.text_input('영문명', placeholder='예: Test Movie')
            new_open_dt = st.text_input('개봉일 (YYYYMMDD)', placeholder='예: 20260101')
            new_show_tm = st.number_input('상영시간(분)', min_value=0, value=0)
        with form_col2:
            new_genre = st.text_input('장르', placeholder='예: 드라마')
            new_nation = st.text_input('제작국가', placeholder='예: 한국')
            new_watch_grade = st.text_input('관람등급', placeholder='예: 15세이상관람가')
            new_directors = st.text_input('감독 (쉼표로 구분)', placeholder='예: 홍길동, 김철수')
            new_actors = st.text_input('배우 (쉼표로 구분)', placeholder='예: 이영희, 박민수')

        submitted = st.form_submit_button('등록', use_container_width=True)

    if submitted:
        if not new_movie_cd or not new_movie_nm:
            st.error('영화 코드와 영화명은 필수입니다.')
        else:
            body = {
                'movie_cd': new_movie_cd,
                'movie_nm': new_movie_nm,
                'movie_nm_en': new_movie_nm_en or None,
                'open_dt': new_open_dt or None,
                'show_tm': new_show_tm or None,
                'genre': new_genre or None,
                'nation': new_nation or None,
                'watch_grade': new_watch_grade or None,
                'directors': [n.strip() for n in new_directors.split(',') if n.strip()],
                'actors': [n.strip() for n in new_actors.split(',') if n.strip()],
            }
            res = requests.post(f'{API_BASE}/movies', json=body)
            if res.status_code == 201:
                st.success(f'"{new_movie_nm}" 등록 완료!')
            else:
                st.error(extract_error_message(res, '등록에 실패했습니다.'))

# =========================================================================================
# 탭 3: 수정/삭제 관리
# =========================================================================================
with tab_manage:
    st.subheader('영화 수정/삭제')
    st.caption('제목으로 검색해서 원하는 영화를 찾은 뒤, 수정하거나 삭제하세요.')

    manage_keyword = st.text_input('영화명 검색', placeholder='예: 하얼빈', key='manage_search')

    if 'editing_movie_cd' not in st.session_state:
        st.session_state.editing_movie_cd = None

    if manage_keyword:
        manage_res = requests.get(f'{API_BASE}/movies', params={'keyword': manage_keyword, 'limit': 20})

        if manage_res.status_code != 200:
            st.error(extract_error_message(manage_res, '검색에 실패했습니다.'))
        else:
            manage_movies = manage_res.json()['items']

            if not manage_movies:
                st.info('검색 결과가 없습니다.')

            for movie in manage_movies:
                row_col1, row_col2, row_col3 = st.columns([4, 1, 1])
                with row_col1:
                    st.write(f'**{movie["movie_nm"]}** ({movie.get("open_dt") or "개봉일 정보없음"}) — {movie.get("genre") or "장르없음"}')
                with row_col2:
                    if st.button('수정', key=f'edit_btn_{movie["movie_cd"]}', use_container_width=True):
                        st.session_state.editing_movie_cd = movie['movie_cd']
                        st.rerun()
                with row_col3:
                    if st.button('삭제', key=f'del_btn_{movie["movie_cd"]}', use_container_width=True):
                        del_res = requests.delete(f'{API_BASE}/movies/{movie["movie_cd"]}')
                        if del_res.status_code == 204:
                            st.success(f'"{movie["movie_nm"]}" 삭제되었습니다.')
                            st.rerun()
                        else:
                            st.error(extract_error_message(del_res, '삭제에 실패했습니다.'))

                # 방금 "수정" 누른 영화면, 바로 아래에 수정 폼을 펼침
                if st.session_state.editing_movie_cd == movie['movie_cd']:
                    edit_detail_res = requests.get(f'{API_BASE}/movies/{movie["movie_cd"]}')
                    if edit_detail_res.status_code == 200:
                        ed = edit_detail_res.json()
                        with st.form(f'edit_form_{movie["movie_cd"]}'):
                            st.markdown(f'**"{ed["movie_nm"]}" 수정**')
                            edit_col1, edit_col2 = st.columns(2)
                            with edit_col1:
                                edit_movie_nm = st.text_input('영화명', value=ed['movie_nm'])
                                edit_open_dt = st.text_input('개봉일 (YYYYMMDD)', value=ed.get('open_dt') or '')
                                edit_show_tm = st.number_input('상영시간(분)', min_value=0, value=ed.get('show_tm') or 0)
                            with edit_col2:
                                edit_genre = st.text_input('장르', value=ed.get('genre') or '')
                                edit_watch_grade = st.text_input('관람등급', value=ed.get('watch_grade') or '')

                            save_col, cancel_col = st.columns(2)
                            with save_col:
                                save_submitted = st.form_submit_button('저장', use_container_width=True)
                            with cancel_col:
                                cancel_submitted = st.form_submit_button('취소', use_container_width=True)

                        if save_submitted:
                            update_body = {
                                'movie_nm': edit_movie_nm,
                                'open_dt': edit_open_dt or None,
                                'show_tm': edit_show_tm or None,
                                'genre': edit_genre or None,
                                'watch_grade': edit_watch_grade or None,
                            }
                            update_res = requests.patch(f'{API_BASE}/movies/{movie["movie_cd"]}', json=update_body)
                            if update_res.status_code == 200:
                                st.success('수정 완료!')
                                st.session_state.editing_movie_cd = None
                                st.rerun()
                            else:
                                st.error(extract_error_message(update_res, '수정에 실패했습니다.'))

                        if cancel_submitted:
                            st.session_state.editing_movie_cd = None
                            st.rerun()

                st.divider()
    else:
        st.info('위 검색창에 영화명을 입력해서 수정/삭제할 영화를 찾아보세요.')