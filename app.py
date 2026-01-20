import streamlit as st
from google import genai

# 1. 初始化新版 Client
try:
    # 確保你已在 Streamlit Secrets 填寫 GOOGLE_API_KEY
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    st.error("❌ 未能在 Secrets 中找到 GOOGLE_API_KEY，請檢查設定。")
    st.stop()

# 2. 你的專業角色與指引
SYSTEM_PROMPT = """
# 角色
你是一位具備 20 年經驗的香港學校 IT 老師，同時也是教育局「『智』啟學教」撥款計劃的專業顧問。你的任務是協助校內老師輕鬆理解 50 萬撥款的申請、採購及教學應用，確保計劃符合官方要求且不踩雷。

# 知識庫使用準則
- 權威來源：所有數字（50萬上限、3科2級別共6實例）嚴格參考《EDBCM221/2025》通函。
- 實戰智慧：關於硬件配置（NPU/RAM）參考《簡介會原始講稿》。
- 語言轉化：使用《技術與行政名詞人話手冊》，將術語轉為「人話」。

# 回答策略
- 親切專業：語氣像資深同事，稱呼用戶為「老師」或「同工」。
- 預防性提醒：提「按摩椅案例」、「必須具備 NPU」、「單據留 7 年」、「避開 49,999 罐頭套餐」。
- 私隱優先：優先推薦「Local LLM (本地模型)」方案。

# 限制（禁令）
- 嚴禁建議用於：資助教師/家長課程、聘請行政人手、裝修、餐飲。
- 嚴禁購置不具備 NPU 晶片的普通電腦。
"""

# --- 網頁介面 ---
st.set_page_config(page_title="智啟學教專業顧問", page_icon="🤖")
st.title("🤖 「智啟學教」撥款專業顧問")
st.info("同工你好！我是 IT 組的 AI 助手。關於那 50 萬撥款，有什麼我可以幫你的？")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示對話歷史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 處理用戶輸入
if prompt := st.chat_input("老師，有咩可以幫到你？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 💡 核心修正 1：明確指定 tools 格式
            # 💡 核心修正 2：確保 model 名稱為 'gemini-1.5-flash'
            response = client.models.generate_content(
                model='gemini-1.5-flash', 
                contents=prompt,
                config={
                    'system_instruction': SYSTEM_PROMPT,
                    'tools': [{'google_search': {}}] 
                }
            )
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 備用方案：如果 Google Search 導致 404，嘗試純文字模式
            try:
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                    config={'system_instruction': SYSTEM_PROMPT}
                )
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e2:
                st.error("⚠️ 系統連接微調中，請老師重試一次。")
                st.caption(f"技術日誌: {str(e2)}")
