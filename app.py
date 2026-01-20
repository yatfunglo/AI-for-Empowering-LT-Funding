import streamlit as st
import google.generativeai as genai

# 1. 安全讀取 API Key
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 未能在 Secrets 中找到 GOOGLE_API_KEY，請檢查 Streamlit 設定。")
    st.stop()

# 2. 你的專業顧問指引 (完整植入)
SYSTEM_PROMPT = """
# 角色
你是一位具備 20 年經驗的香港學校 IT 老師，同時也是教育局「『智』啟學教」撥款計劃的專業顧問。你的任務是協助校內老師輕鬆理解 50 萬撥款的申請、採購及教學應用，確保計劃符合官方要求且不踩雷。

# 知識庫使用準則
- 權威來源：參考《EDBCM221/2025》通函。
- 實戰智慧：參考《簡介會原始講稿》，強調 NPU 硬件配置。
- 語言轉化：參考《技術與行政名詞人話手冊》，先用「人話」解釋。

# 回答策略
- 親切專業：語氣像資深同事，多用「老師」、「同工」稱呼。
- 預防性提醒：必提「按摩椅案例」、「必須具備 NPU」及「單據留 7 年」。
- KPI 輔導：核對「3 科 2 級別、共 6 個實例」。
- 聯網搜尋：詢問最新型號或格價時，請使用 Google Search 提供市場資訊。

# 限制（禁令）
- 嚴禁建議資助教師/家長課程、聘請行政人手、裝修、餐飲。
- 嚴禁建議購置不具備 NPU 晶片的電腦。
"""

st.set_page_config(page_title="智啟學教撥款專業顧問", page_icon="🤖")
st.title("🤖 「智啟學教」撥款專業顧問")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("老師，有咩可以幫到你？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # --- 核心修正：使用穩定版呼叫並整合 Google Search ---
        try:
            # 建立具備聯網功能的模型
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=SYSTEM_PROMPT,
                tools=[{'google_search_retrieval': {}}] 
            )
            
            # 產生回覆
            response = model.generate_content(prompt)
            full_response = response.text
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 容錯處理：如果 Google Search 工具報錯，自動切換至純 AI 模式
            model_basic = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=SYSTEM_PROMPT
            )
            response = model_basic.generate_content(prompt)
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
