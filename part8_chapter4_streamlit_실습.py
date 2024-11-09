import streamlit as st

import requests
import json

# Ollama API 주소와 모델 설정
API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3B"

# API 호출 함수
def get_response_from_ollama(history):
    headers = {'Content-Type': 'application/json'}
    
    # 대화 기록을 하나의 문자열로 결합하여 보냄
    prompt = "\n".join([f"{entry['role']}: {entry['content']}" for entry in history])
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # 요청 오류 시 예외 발생
        response_data = response.json()
        return response_data.get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        # 오류 메시지를 출력해 문제를 파악
        print(f"Request error: {e}")
        return f"Error: {e}"

# 메시지 전송 함수
def send_message():
    user_input = st.session_state["input_text"]
    if user_input.strip():  # 빈 메시지일 경우 제외
        # 사용자 입력을 history에 추가
        st.session_state["history"].append({"role": "user", "content": user_input})

        # Ollama API로부터 응답을 받고 history에 추가
        response = get_response_from_ollama(st.session_state["history"])
        st.session_state["history"].append({"role": "assistant", "content": response})

        # 입력 필드를 비웁니다.
        st.session_state["input_text"] = ""  # Session State의 값을 직접 초기화

# Streamlit UI 구성
st.title("Ollama Chat UI")

# 세션 상태 초기화
if "history" not in st.session_state:
    st.session_state["history"] = []

# 채팅 기록 표시
for chat in st.session_state["history"]:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['content']}")
    else:
        st.markdown(f"**Ollama:** {chat['content']}")

# 사용자 입력 받기 (엔터 키 입력 감지)
st.text_input("Enter your message here:", key="input_text", on_change=send_message)

# 전송 버튼 생성
if st.button("Send"):
    send_message()