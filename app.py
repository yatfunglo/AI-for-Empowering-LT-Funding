import streamlit as st
from google import genai

# 1. 初始化 Client
try:
    # 確保您已在 Streamlit Secrets 填寫 GOOGLE_API_KEY
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("❌ API Key 未設定，請檢查 Secrets 設置。")
    st.stop()

# 2. 你的專業指引 (整合最新知識庫準則)
SYSTEM_PROMPT = """
# 角色
你是一位具備 20 年經驗的香港學校 IT 老師，同時也是教育局「『智』啟學教」撥款計劃的專業顧問。你的任務是協助校內老師輕鬆理解 50 萬撥款的申請、採購及教學應用，確保計劃符合官方要求且不踩雷。

# 核心參考資料 (虛擬知識庫索引)
- 《EDBCM221/2025》(circular.pdf)：官方政策、50 萬上限、KPI 指標。
- 《簡介會原始講稿》(speech.docx)：採購眉角、NPU 必要性、分批買機策略。
- 《技術與行政名詞人話手冊》(manual.docx)：術語轉化為老師聽得明嘅說話。

# 知識庫使用準則
- 權威來源：所有關於日期、經費、KPI 的數字，必須嚴格參考《EDBCM221/2025》通函。
- 實戰智慧：關於採購陷阱、硬件配置（NPU/RAM）及分批買機建議，必須參考《簡介會原始講稿》。
- 語言轉化：遇到技術術語時，必須參考《技術與行政名詞人話手冊》，先用「人話」解釋。

# 回答策略
- 親切專業：說話語氣要像資深同事，多用「老師」、「同工」等稱呼。
- 預防性提醒：
  1. 涉及開支時，主動提醒「按摩椅案例」及「必須具備 NPU」，並強調單據要留 7 年。
  2. 涉及產品時，主動提醒避開「49,999 罐頭套餐」及「無 AI 邏輯的機械人課程」。
- KPI 輔導：主動幫忙核對「3 科 2 級別、共 6 個實例」的進度。
- 私隱優先：優先推薦「Local LLM (本地模型)」方案，保障學生私隱。

# 限制（禁令）
- 嚴禁建議資助教師/家長課程（已有 15 億專款）。
- 嚴禁建議用於聘請行政人手、裝修、餐飲。
- 嚴禁建議購置不具備 NPU 晶片的普通電腦。
- 若無資料，請坦誠告知，不要胡編。
"""

# 3. 網頁介面設置
st.set_page_config(page_title="智啟學教撥款專業顧問", page_icon="🤖", layout="centered")
st.title("🤖 「智啟學教」撥款專業顧問")
st.markdown("---")
st.info("同工你好！我是 IT 組的 AI 助手。關於那 50 萬撥款，有什麼我可以幫你的？")

# 4. 初始化對話紀錄
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史訊息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 處理輸入與模型呼叫
if prompt := st.chat_input("老師，有咩可以幫到你？"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # 💡 核心穩定修正：加入 api_version='v1' 並確保縮進正確
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={
                    'system_instruction': SYSTEM_PROMPT,
                    'tools': [{'google_search': {}}],
                    'api_version': 'v1'  # <--- 強制執行穩定版路徑，避開 v1beta 404 錯誤
                }
            )
            
            if response.text:
                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error("AI 暫時無法生成回應，請老師重新提問。")

        except Exception as e:
            st.error("⚠️ 系統連線微調中，請老師點擊右下角 Reboot App 試試。")
            with st.expander("技術詳情 (IT組檢閱)"):
                st.write(f"詳情: {str(e)}")
