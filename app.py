import streamlit as st
import google.generativeai as genai
import gspread
from dotenv import load_dotenv
from datetime import datetime
import os
import base64
import json

service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])

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

# --- Kết nối Google Sheets ---
def connect_sheet():
    try:
        gc = gspread.service_account_from_dict(service_account_info)
        sh = gc.open_by_key(sheet_key)
        return sh.sheet1
    except Exception as e:
        st.error(f"⚠️ Không thể kết nối Google Sheet: {e}")
        return None

sheet = connect_sheet()

def save_to_sheet(name, question, answer):
    try:
        if sheet:
            sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                name, question, answer
            ])
    except Exception as e:
        st.warning(f"⚠️ Không thể lưu lịch sử: {e}")

# --- Tạo hàm đọc ảnh base64 để nhúng vào CSS ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    return f"data:image/jpg;base64,{encoded}"

# --- Đường dẫn ảnh trong thư mục chính ---
bg_login = get_base64_image("bg_login.jpg")
bg_chat = get_base64_image("bg_chat.jpg")

# --- Cấu hình trang ---
st.set_page_config(page_title="💬 Trợ lý ảo của cô Uyên", page_icon="🧠", layout="centered")

# --- Nếu chưa nhập tên học sinh ---
if "student_name" not in st.session_state:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{bg_login}");
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
            background-image: url("{bg_chat}");
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

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Em muốn hỏi gì nè? 💬"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            placeholder = st.empty()
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
                    reply = response.text
                else:
                    reply = "Cô chưa nghe rõ câu hỏi của em, con nói lại nha 💬"
            except Exception as e:
                reply = f"⚠️ Có lỗi khi gọi Gemini API: {e}"

            placeholder.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        save_to_sheet(st.session_state.student_name, prompt, reply)

