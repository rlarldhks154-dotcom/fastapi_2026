# ========================================================================
# ~/bigdata2026/fastapi/Streamlit/06_multiselect_slider.py
#   
#   Streamlit 라이브러리 기초 실습
#
#       - 입력 위젯 (단중 선택 박스, 숫자 슬라이더 등)
# ========================================================================
import streamlit as st
from datetime import time

st.title("Streamlit 입력 위젯 실습")

st.divider()

# 1. 다중 선택 박스 퀴즈
st.subheader("1. 다중 선택 박스 퀴즈")

fruits = st.multiselect(
    "Q1. 과일을 모두 선택하세요 (복수 정답 가능):",
    ["사과", "토마토", "당근", "바나나"]
)

correct = {"사과", "토마토", "바나나"}

if set(fruits) == correct:
    st.write("완벽해요! 모두 맞았습니다.")
else:
    st.write("다시 선택해보세요!")

st.divider()

# 2. 숫자 슬라이더
st.subheader("2. 숫자 슬라이더")

score = st.slider("Your score is...", 0, 100, 1)

st.text(f"Score :{score}")

st.divider()

# 3. 시간 범위 슬라이더
st.subheader("3. 시간 범위 슬라이더")

start_time, end_time = st.slider(
    "Working time is ...",
    min_value=time(0),
    max_value=time(23),
    value=(time(9), time(18)),
    format="HH:mm"
)

st.text(f"Working time :{start_time},{end_time}")