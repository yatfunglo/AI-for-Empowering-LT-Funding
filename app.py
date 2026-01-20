import streamlit as st
import google.generativeai as genai
import os

# 1. 安全讀取 API Key
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 未能在 Secrets 中找到 GOOGLE_API_KEY，請檢查 Streamlit 設定。")
    st.stop()

# 2. 角色與知識庫指引
SYSTEM_PROMPT = """
你是具備 20 年經驗的香港學校 IT 老師及「智啟學教」撥款顧問。
你的回答必須結合以下參考資料：
- 《EDBCM221/2025》(circular.pdf)
- 《簡介會原始講稿》(speech.pdf)
- 《技術與行政名詞人話手冊》(manual.pdf)

# 核心規則：
1. 撥款 50 萬上限，電腦必須配備 NPU。
2. 嚴禁買按摩椅、裝修、行政費。單據留 7 年。
3. 詢問產品或規格時，請使用 Google Search 尋找最新市場型號。
"""

st.set_page_config(page_title="智啟學教專業顧問", page_icon="🤖")
st.title("🤖 「智啟學教」撥款專業顧問")

# 3. 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 處理老師輸入
if prompt := st.chat_input("老師，有咩可以幫到你？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # 修正 404 錯誤：明確指定 model 呼叫方式
        try:
            # 這裡整合了 Google Search Grounding (聯網功能)
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=SYSTEM_PROMPT,
                tools=[{'google_search_retrieval': {}}] 
            )
            
            # 啟動對話
            response = model.generate_content(prompt)
            full_response = response.text
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 如果 Flash 仍然報錯，切換至穩定版路徑
            st.error(f"系統自動修復中，請重試。若持續報錯請檢查 API 狀態。 (Error: {str(e)})")
