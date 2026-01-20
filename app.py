import streamlit as st
import google.generativeai as genai

# 1. 安全讀取 API Key
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("❌ 未能在 Secrets 中找到 GOOGLE_API_KEY，請檢查 Streamlit 設定。")
    st.stop()

# 2. 完整指引植入
SYSTEM_PROMPT = """
# 角色
你是一位具備 20 年經驗的香港學校 IT 老師，同時也是教育局「『智』啟學教」撥款計劃的專業顧問。你的任務是協助校內老師輕鬆理解 50 萬撥款的申請、採購及教學應用，確保計劃符合官方要求且不踩雷。

# 知識庫使用準則
- 權威來源：所有關於日期、經費、KPI（3科2級別）的數字，嚴格參考《EDBCM221/2025》通函。
- 實戰智慧：硬件必須具備 NPU，參考《簡介會原始講稿》。
- 語言轉化：使用《技術與行政名詞人話手冊》，將術語轉為「人話」。

# 回答策略
- 親切專業：語氣要像資深同事，多用「老師」、「同工」稱呼。
- 預防性提醒：
    1. 提及開支必提「按摩椅案例」及「必須具備 NPU」。
    2. 強調單據保留 7 年。
    3. 避開「49,999 罐頭套餐」。
- 私隱優先：推薦「Local LLM (本地模型)」。

# 限制（禁令）
- 嚴禁建議資助教師/家長課程、聘請行政人手、裝修、餐飲。
- 嚴禁購置不具備 NPU 晶片的普通電腦。
"""

st.set_page_config(page_title="智啟學教專業顧問", page_icon="🤖")
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
        
        try:
            # 💡 終極修正：強制指定路徑，移除所有 beta 工具
            # 這是目前最能避開 404 models/gemini-1.5-flash is not found 的寫法
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=SYSTEM_PROMPT
            )
            
            response = model.generate_content(prompt)
            
            if response and response.text:
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.warning("同工，AI 暫時反應唔到，請試下簡化你嘅問題。")
                
        except Exception as e:
            # 即使報錯也用主任的口吻回答
            st.error("抱歉同工，系統連線出咗啲技術問題，可能係 Google API 暫時繁忙。")
            with st.expander("查看技術錯誤（供 IT 組參考）"):
                st.write(str(e))
