import streamlit as st
import google.generativeai as genai
import gspread
import json
from datetime import datetime
import pandas as pd

# ===================== CẤU HÌNH GOOGLE SHEET =====================
service_account_info = json.loads(st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
gc = gspread.service_account_from_dict(service_account_info)
sheet_key = st.secrets["GOOGLE_SHEET_KEY"]
worksheet = gc.open_by_key(sheet_key).sheet1

# ===================== CẤU HÌNH GEMINI =====================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model_name = "gemini-2.5-flash"

# ===================== CẤU HÌNH GIAO DIỆN TRANG =====================
st.set_page_config(page_title="Cô Uyên 🌸", page_icon="🤖", layout="centered")

# ===================== CSS =====================
def apply_css(bg_image):
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{bg_image}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .title-box {{
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 20px 30px;
            margin: 30px auto;
            width: fit-content;
            backdrop-filter: blur(8px);
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
            text-align: center;
        }}
        h1, h2, h3 {{
            color: #003366;
            text-shadow: 1px 1px 2px white;
        }}
        .user-msg {{
            background-color: rgba(255, 255, 255, 0.8);
            border-left: 4px solid #6ec1e4;
            padding: 8px 12px;
            border-radius: 12px;
        }}
        .assistant-msg {{
            background-color: rgba(255, 255, 255, 0.9);
            border-left: 4px solid #f5b642;
            padding: 8px 12px;
            border-radius: 12px;
        }}
        </style>
    """, unsafe_allow_html=True)

# ===================== TRANG ĐĂNG NHẬP =====================
if "student_name" not in st.session_state:
    apply_css("https://raw.githubusercontent.com/yang13102003/chatbot/main/images/bg_login.jpg")
    st.markdown("<div class='title-box'><h1>🌸 Xin chào em! 🌸</h1><p>Nhập tên để cô Uyên biết em là ai nhé 💬</p></div>", unsafe_allow_html=True)
    name = st.text_input("👧 Nhập tên của em:")
    if st.button("Bắt đầu học 💻"):
        if name.strip():
            st.session_state.student_name = name.strip()
            st.session_state.messages = []
            st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.page = "chat"
            st.rerun()
        else:
            st.warning("Vui lòng nhập tên nha em 💡")
    st.stop()

# ===================== THANH ĐIỀU HƯỚNG =====================
page = st.sidebar.radio("📚 Chọn trang", ["💬 Trò chuyện", "📜 Lịch sử trò chuyện"])

# ===================== TRANG 1: TRÒ CHUYỆN =====================
if page == "💬 Trò chuyện":
    apply_css("https://raw.githubusercontent.com/yang13102003/chatbot/main/images/bg_chat.jpg")

    st.markdown(f"""
    <div class='title-box'>
        <h1>💬 Cô Uyên cùng trò chuyện với em {st.session_state.student_name} 🌼</h1>
        <p>(Trợ lý học tập – Chủ đề Tin học lớp 3)</p>
    </div>
    """, unsafe_allow_html=True)

    SYSTEM_CONTEXT = (
        "Bạn là Trợ lý học tập thân thiện của cô giáo Đặng Tố Uyên. "
        "Xưng hô: cô và em. "
        "Luôn nói ngắn gọn, dễ hiểu, dùng lời lẽ dịu dàng như đang dạy học sinh tiểu học. "
        "Nếu học sinh hỏi về Tin học lớp 3, hãy giảng giải từng bước rõ ràng. "
        "Nếu học sinh chào hỏi hoặc tâm sự, hãy phản hồi nhẹ nhàng, thân thiện. "
        "Không nói về các chủ đề ngoài giáo dục hoặc không phù hợp với trẻ em."
    )

    # Hiển thị lịch sử chat hiện tại
    for msg in st.session_state.get("messages", []):
        css_class = "user-msg" if msg["role"] == "user" else "assistant-msg"
        st.markdown(f"<div class='{css_class}'>{msg['content']}</div>", unsafe_allow_html=True)

    # Học sinh nhập câu hỏi
    if prompt := st.chat_input("Nhập tin nhắn để nói chuyện với cô 💬"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f"<div class='user-msg'>{prompt}</div>", unsafe_allow_html=True)

        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(f"{SYSTEM_CONTEXT}\nHọc sinh hỏi: {prompt}")
            reply = response.text.strip() if response.text else "⚠️ Cô chưa nghe rõ câu hỏi, em nói lại giúp cô nhé!"
        except Exception as e:
            reply = f"⚠️ Có lỗi khi gọi Gemini API: {e}"

        st.markdown(f"<div class='assistant-msg'>{reply}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Lưu vào Google Sheet
        try:
            worksheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                st.session_state.student_name,
                st.session_state.session_id,
                prompt,
                reply
            ])
        except Exception as e:
            st.warning(f"⚠️ Không thể lưu vào Google Sheet: {e}")

# ===================== TRANG 2: LỊCH SỬ =====================
elif page == "📜 Lịch sử trò chuyện":
    import io
    import pandas as pd
    apply_css("https://raw.githubusercontent.com/yang13102003/chatbot/main/images/bg_login.jpg")

    st.markdown(f"""
    <div class='title-box'>
        <h1>📜 Lịch sử trò chuyện</h1>
        <p>Xem lại các buổi học đã ghi vào Google Sheet 🌼</p>
    </div>
    """, unsafe_allow_html=True)

    # Chọn chế độ xem
    view_mode = st.radio("Chọn chế độ xem:", ["📖 Của em", "👩‍🏫 Tất cả học sinh"])

    try:
        records = worksheet.get_all_records()
        if not records:
            st.info("💤 Chưa có buổi học nào được ghi lại.")
        else:
            df = pd.DataFrame(records)
            df.columns = [col.strip().lower() for col in df.columns]

            col_time = next((c for c in df.columns if "thời" in c or "time" in c), None)
            col_name = next((c for c in df.columns if "học" in c or "sinh" in c), None)
            col_question = next((c for c in df.columns if "câu" in c or "question" in c), None)
            col_answer = next((c for c in df.columns if "trả" in c or "answer" in c), None)

            # 🧩 Chuyển thời gian linh hoạt
            df[col_time] = pd.to_datetime(df[col_time].astype(str), errors='coerce', format='mixed')

            # 🧩 Lọc lịch sử
            if view_mode == "📖 Của em":
                df = df[df[col_name].str.lower().str.strip() == st.session_state.student_name.lower().strip()]
            else:
                st.success("👩‍🏫 Đang hiển thị lịch sử của tất cả học sinh.")

            df = df.sort_values(by=col_time, ascending=False)

            if df.empty:
                st.info("🙋 Không có lịch sử nào để hiển thị.")
            else:
                # 🧩 Định dạng lại thời gian
                df[col_time] = df[col_time].dt.strftime("%Y-%m-%d %H:%M")

                df_display = df[[col_time, col_name, col_question, col_answer]]
                df_display.columns = ["Thời gian", "Học sinh", "Câu hỏi", "Câu trả lời"]

                # Hiển thị bảng lịch sử
                st.dataframe(df_display, use_container_width=True)

                # ===== 📥 Nút tải file CSV UTF-8 =====
                csv_bytes = df_display.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "📄 Tải CSV (UTF-8, tiếng Việt chuẩn)",
                    csv_bytes,
                    file_name="lich_su_tro_chuyen.csv",
                    mime="text/csv"
                )

                # ===== 📗 Nút tải file Excel =====
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df_display.to_excel(writer, index=False, sheet_name="Lich_su")
                    ws = writer.sheets["Lich_su"]
                    ws.set_column("A:A", 20)
                    ws.set_column("B:B", 18)
                    ws.set_column("C:C", 40)
                    ws.set_column("D:D", 60)
                buffer.seek(0)
                st.download_button(
                    "📘 Tải Excel (.xlsx)",
                    data=buffer,
                    file_name="lich_su_tro_chuyen.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"⚠️ Không thể tải lịch sử: {e}")
