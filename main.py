
import openai
import os
key = os.environ.get("api_key")
client = openai
client.api_key = key

# Replace 'MY_VARIABLE' with the name of the environment variable you want to access

print('my_variable', key)

##### 기본 정보 입력 #####
import streamlit as st
from audiorecorder import audiorecorder

import os
from datetime import datetime
from pathlib import Path
import base64

from pydub import AudioSegment
from pydub.playback import play

def STT(audio):
    # 파일 저장
    filename = 'input.mp3'
    audio.export(filename, format="mp3")
    # 음원 파일 열기
    audio_file = open(filename, "rb")
    # Whisper 모델을 활용해 텍스트 얻기
    transcript = client.audio.translations.create(model='whisper-1', file = audio_file)
    audio_file.close()
    # 파일 삭제
    os.remove(filename)
    return transcript.text


def ask_gpt(prompt, model):
    response = client.chat.completions.create(model=model, messages=prompt)
    system_message = response.choices[0].message
    return system_message.content


def TTS(response):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    answer = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=response
    )
    answer.stream_to_file(speech_file_path)

    try:
        # Open and read the MP3 file
        audio = AudioSegment.from_mp3(speech_file_path)

        # Play the audio
        play(audio)
    except Exception as e:
        print(f"An error occurred: {e}")




##### 메인 함수 #####
def main():

    # session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system",
                                         "content": "You are a thoughtful assistant. You answer questions within 30 words"}]

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    # 사이드바 생성
    with st.sidebar:

        # Open AI API 키 입력받기

        st.markdown("---")

        # GPT 모델을 선택하기 위한 라디오 버튼 생성
        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        # 리셋 버튼 생성
        if st.button(label="초기화"):
            # 리셋 코드
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system",
                                             "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"] = True

    # 기능 구현 공간
    col1, col2 = st.columns(2)
    with col1:
        # 왼쪽 영역 작성
        st.subheader("질문하기")
        # 음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기", "녹음중...")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # 음성 재생
            st.audio(audio.export().read())
            # 음원 파일에서 텍스트 추출
            question = STT(audio)

            # 채팅을 시각화하기 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]

    with col2:
        # 오른쪽 영역 작성
        st.subheader("질문/답변")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
            # ChatGPT에게 답변 얻기
            response = ask_gpt(st.session_state["messages"], model)

            # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]

            # 채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]

            # 채팅 형식으로 시각화 하기
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(
                        f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(
                        f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>',
                        unsafe_allow_html=True)
                    st.write("")

            # gTTS 를 활용하여 음성 파일 생성 및 재생
            TTS(response)
        else:
            st.session_state["check_reset"] = False


if __name__ == "__main__":
    main()