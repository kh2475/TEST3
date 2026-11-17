import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-6.1-sol")
MAX_CHARS = 5000
LANGUAGES = {
    "영어": ("English", "🇺🇸"),
    "일본어": ("Japanese", "🇯🇵"),
    "베트남어": ("Vietnamese", "🇻🇳"),
}


def get_api_key():
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        try:
            key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            key = None
    return key


def translate(text: str, target: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a professional translator. Translate the user's text into {target}. "
                    "Preserve meaning, tone, and line breaks. Output only the translation."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()


def clear_all():
    st.session_state["input_text"] = ""
    st.session_state.pop("result", None)


st.set_page_config(page_title="번역기", page_icon="🌐", layout="centered")

st.markdown(
    """
    <style>
    .block-container { max-width: 720px; padding-top: 2rem; }
    div.stButton > button { height: 3rem; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌐 번역기")
st.caption("텍스트를 입력하고 번역할 언어 버튼을 눌러보세요. 입력 언어는 자동으로 감지됩니다.")

text = st.text_area(
    "번역할 텍스트",
    key="input_text",
    height=200,
    max_chars=MAX_CHARS,
    placeholder="여기에 번역할 내용을 입력하세요.",
)
info_col, clear_col = st.columns([3, 1])
info_col.caption(f"{len(text)} / {MAX_CHARS}자")
clear_col.button("지우기", on_click=clear_all, use_container_width=True)

# 모바일에서는 버튼이 세로로 쌓이도록 columns 사용
cols = st.columns(len(LANGUAGES))
clicked = None
for col, (label, (_, flag)) in zip(cols, LANGUAGES.items()):
    if col.button(f"{flag} {label}", use_container_width=True, type="primary"):
        clicked = label

if clicked:
    api_key = get_api_key()
    if not text.strip():
        st.warning("번역할 내용을 입력해주세요.")
    elif not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    else:
        try:
            with st.spinner(f"{clicked}로 번역 중..."):
                result = translate(text, LANGUAGES[clicked][0], api_key)
            st.session_state["result"] = (clicked, result)
        except Exception as e:
            st.session_state.pop("result", None)
            st.error(f"번역 중 오류가 발생했습니다: {e}")

if "result" in st.session_state:
    lang_label, result = st.session_state["result"]
    st.divider()
    st.subheader(f"{LANGUAGES[lang_label][1]} {lang_label} 번역 결과")
    # st.code 우측 상단에 복사 버튼이 자동 제공됨
    st.code(result, language=None, wrap_lines=True)
