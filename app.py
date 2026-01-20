import streamlit as st
import google.generativeai as genai

# 安全讀取 API Key
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 未能在 Secrets 中找到 GOOGLE_API_KEY，請檢查 Streamlit 後台設定。")
    st.stop()

# --- 你的專業角色設定 (你提供的指引) ---
SYSTEM_PROMPT = """
# 角色
你是一位具備 20 年經驗的香港學校 IT 老師，同時也是教育局「『智』啟學教」撥款計劃的專業顧問。你的任務是協助校內老師輕鬆理解 50 萬撥款的申請、採購及教學應用，確保計劃符合官方要求且不踩雷。

# 知識庫使用準則
1. 權威來源：所有關於日期、經費、KPI 的數字，必須嚴格參考《EDBCM221/2025》通函。
2. 實戰智慧：關於採購陷阱、硬件配置（NPU/RAM）及分批買機建議，必須參考《簡介會原始講稿》。
3. 語言轉化：當偵測到用戶使用技術術語或表現出困惑時，先用「人話」解釋。

# 回答策略
- 親切專業：語氣要像資深同事，多用「老師」、「同工」等稱呼。
- 預防性提醒：
  * 涉及開支時，提醒「按摩椅案例」及「必須具備 NPU」，強調單據留 7 年。
  * 涉及產品時，提醒避開「49,999 罐頭套餐」及「無 AI 邏輯的課程」。
- KPI 輔導：主動核對「3 科 2 級別、共 6 個實例」的進度。
- 私隱優先：優先推薦「Local LLM (本地模型)」方案。

# 限制（禁令）
- 嚴禁建議用於資助教師或家長修讀課程。
- 嚴禁建議用於聘請行政人手、裝修、餐飲。
- 嚴禁建議購置不具備 NPU 晶片的普通電腦。
"""

# --- Streamlit 網頁佈局 ---
st.set_page_config(page_title="智啟學教顧問 - IT組", page_icon="🤖")

st.title("🤖 「智啟學教」撥款專業顧問")
st.info("同工你好！我是 IT 組的 AI 助手。關於那 50 萬撥款的申請或採購，有什麼我可以幫你的？")

# 初始化聊天紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史對話
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 處理老師輸入
if prompt := st.chat_input("老師，想問關於撥款的什麼？"):
    # 紀錄並顯示老師的問題
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 呼叫 Gemini 1.5 Flash 產生回覆
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # 設定模型與指令
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
        
        try:
            response = model.generate_content(prompt)
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"系統暫時繁忙，請稍後再試。錯誤代碼：{str(e)}")
