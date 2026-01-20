import streamlit as st
import google.generativeai as genai

# 1. 安全讀取 API Key
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 未能在 Secrets 中找到 GOOGLE_API_KEY，請檢查 Streamlit 設定。")
    st.stop()

# 2. 你的專業角色與知識庫指引 (完整植入)
SYSTEM_PROMPT = """
# 角色
你是一位具備 20 年經驗的香港學校 IT 老師，同時也是教育局「『智』啟學教」撥款計劃的專業顧問。你的任務是協助校內老師輕鬆理解 50 萬撥款的申請、採購及教學應用。

# 知識庫使用準則
- 權威來源：參考《EDBCM221/2025》通函。
- 硬件規格：參考《簡介會原始講稿》，必須具備 NPU。
- 語言：參考《技術與行政名詞人話手冊》，用「人話」解釋。

# 回答策略
- 親切專業：稱呼用戶為「老師」或「同工」。
- 預防性提醒：主動提及「按摩椅案例」、「單據留 7 年」及「避開 49,999 套餐」。
- KPI 輔導：核對「3 科 2 級別、共 6 個實例」。
- 私隱優先：推薦「Local LLM (本地模型)」。

# 限制（禁令）
- 嚴禁建議用於教師培訓、家長課程、行政人手、裝修、餐飲。
- 嚴禁購置不具備 NPU 的普通電腦。

# 聯網功能
當老師詢問最新市場型號或格價時，請啟動 Google 搜尋功能。
"""

st.set_page_config(page_title="智啟學教撥款顧問", page_icon="🤖")

# 網頁頂部標題與說明
st.title("🤖 「智啟學教」撥款專業顧問")
st.markdown("---")

# 3. 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史訊息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. 處理用戶輸入
if prompt := st.chat_input("老師，有咩可以幫到你？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 使用最穩定的模型呼叫方式，並加入 google_search 引擎
        try:
            # 修正 404 關鍵：明確使用穩定版模型名稱並移除 beta 路徑
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=SYSTEM_PROMPT,
                tools=[{'google_search_retrieval': {}}] 
            )
            
            response = model.generate_content(prompt)
            full_response = response.text
            
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # 若發生錯誤，提供人性化提示
            st.warning("⚠️ 系統正忙，請稍微等候 10 秒再試一次。")
            st.caption(f"技術詳情: {str(e)}")
