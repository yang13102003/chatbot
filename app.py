import streamlit as st
import google.generativeai as genai
import gspread
from dotenv import load_dotenv
from datetime import datetime
import os

# --- Load biến môi trường ---
load_dotenv("key.env")
api_key = os.getenv("GEMINI_API_KEY")
sheet_key = os.getenv("GOOGLE_SHEET_KEY")

# --- Cấu hình Gemini ---
genai.configure(api_key=api_key)

SYSTEM_CONTEXT = (
    "Bạn là Trợ lý ảo học tập thân thiện của cô giáo Đặng Tố Uyên. 🌼\n"
    "Bạn xưng 'cô' và gọi học sinh là 'em'.\n"
    "Luôn trả lời ngắn gọn, rõ ràng, dễ hiểu, thân thiện và tích cực.\n"
    "Chủ đề chính: giảng dạy Tin học lớp 3 (máy tính, chuột, bàn phím, phần mềm đơn giản...).\n"
    "Nếu em hỏi ngoài chủ đề, hãy nhẹ nhàng hướng về chủ đề học tập.\n"
)

# --- Kết nối Google Sheet ---
def connect_sheet():
    try:
        gc = gspread.service_account(filename="key.json")
        sh = gc.open_by_key(sheet_key)
        return sh.sheet1
    except Exception as e:
        st.error(f"⚠️ Không thể kết nối Google Sheet: {e}")
        return None

sheet = connect_sheet()

# --- Hàm lưu lịch sử ---
def save_to_sheet(name, question, answer):
    try:
        if sheet:
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name, question, answer
            ])
    except Exception as e:
        st.warning(f"⚠️ Không thể lưu lịch sử: {e}")

# --- Hàm xử lý sinh nội dung ---
def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config=genai.GenerationConfig(
                max_output_tokens=200,
                temperature=0.6,
            ),
            system_instruction=SYSTEM_CONTEXT
        )
        response = model.generate_content(prompt)
        if hasattr(response, "text") and response.text:
            return response.text
        else:
            return "Cô chưa nghe rõ câu hỏi của em, con nói lại nha 💬"
    except Exception as e:
        return f"⚠️ Có lỗi khi gọi Gemini API: {e}"

# --- Giao diện Streamlit ---
st.set_page_config(page_title="💬 Trợ lý ảo của cô Uyên", page_icon="🧠", layout="centered")

# --- Nếu chưa nhập tên học sinh ---
if "student_name" not in st.session_state:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("assets/bg_login.jpg");
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("🎓 Xin chào học sinh thân mến!")
    st.subheader("Cô Uyên rất vui được gặp em 💻")

    name = st.text_input("Em hãy nhập tên của mình để bắt đầu học nhé:")
    if st.button("Bắt đầu học 👋"):
        if name.strip():
            st.session_state.student_name = name.strip()
            st.rerun()
        else:
            st.warning("Em quên nhập tên rồi kìa 🌼")
else:
    # --- Trang chatbot ---
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("assets/bg_chat.jpg");
            background-size: cover;
            background-position: center;
        }}
        .stChatMessage {{
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 15px;
            padding: 10px;
            margin: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title(f"💬 Cô Uyên cùng trò chuyện với em {st.session_state.student_name} 🌼")
    st.caption("(Trợ lý ảo học tập – chủ đề Tin học lớp 3)")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Hiển thị lịch sử chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Ô nhập tin nhắn
    if prompt := st.chat_input("Em muốn hỏi gì nè? 💬"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            placeholder = st.empty()
            reply = ask_gemini(prompt)
            placeholder.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        save_to_sheet(st.session_state.student_name, prompt, reply)
