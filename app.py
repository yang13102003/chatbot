import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# --- Load API key ---
load_dotenv(dotenv_path="key.env")  # ⚠️ chỉ rõ tên file .env của bạn
api_key = os.getenv("OPENAI_API_KEY")

# --- Kết nối OpenAI ---
client = OpenAI(api_key=api_key)

# --- Cấu hình giao diện ---
st.set_page_config(page_title="Uyên ChatGPT 🤖", page_icon="💬", layout="wide")

# --- CSS Tùy chỉnh ---
st.markdown("""
<style>
/* Toàn trang - nền + font */
[data-testid="stAppViewContainer"] {
    background: url("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1740&q=80")
                no-repeat center center fixed;
    background-size: cover;
    font-family: 'Segoe UI', sans-serif;
    color: #ffffff;
}

/* Hiệu ứng overlay làm mờ */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.65);
    z-index: 0;
}

/* Vùng nội dung chính */
.block-container {
    position: relative;
    z-index: 2;
    padding-top: 1rem;
}

/* Khung chat */
[data-testid="stChatMessage"] {
    background-color: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
}

/* Ô nhập chat */
[data-testid="stChatInput"] textarea {
    background-color: rgba(255,255,255,0.1);
    color: #fff;
    border-radius: 8px;
}

/* Tiêu đề */
h1, h2, h3, h4 {
    color: #00ffff !important;
    text-align: center;
}

/* Floating icons animation */
@keyframes float {
    0% { transform: translateY(0px) rotate(0deg); opacity: 0.8; }
    50% { transform: translateY(-20px) rotate(10deg); opacity: 1; }
    100% { transform: translateY(0px) rotate(-10deg); opacity: 0.8; }
}
.floating-icon {
    position: fixed;
    font-size: 24px;
    color: #00ffff;
    opacity: 0.15;
    animation: float 6s ease-in-out infinite;
    z-index: 1;
}
#icon1 { top: 10%; left: 5%; animation-delay: 0s; }
#icon2 { top: 30%; right: 10%; animation-delay: 2s; }
#icon3 { bottom: 20%; left: 10%; animation-delay: 4s; }
#icon4 { top: 60%; right: 20%; animation-delay: 1s; }
#icon5 { bottom: 10%; right: 5%; animation-delay: 3s; }

/* Thanh cuộn */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: #00ffff; border-radius: 4px; }
</style>

<!-- Các icon bay quanh giao diện -->
<div id="icon1" class="floating-icon">💻</div>
<div id="icon2" class="floating-icon">⚙️</div>
<div id="icon3" class="floating-icon">💡</div>
<div id="icon4" class="floating-icon">🧠</div>
<div id="icon5" class="floating-icon">💾</div>
""", unsafe_allow_html=True)

# --- Header đẹp ---
col1, col2 = st.columns([1,4])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=80)
with col2:
    st.markdown("<h1 style='margin-bottom:0;'>Uyên ChatGPT 🤖</h1>", unsafe_allow_html=True)
    st.caption("Trợ lý AI phong cách ChatGPT – nền tùy chỉnh, hiệu ứng công nghệ ✨")

# --- Nút xóa hội thoại ---
if st.button("🗑️ Xóa hội thoại"):
    st.session_state.messages = []
    st.experimental_rerun()

# --- Bộ nhớ hội thoại ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Hiển thị lịch sử ---
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- Input người dùng ---
if prompt := st.chat_input("Nhập tin nhắn của bạn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🧑‍💻").markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
