import streamlit as st
from openai import OpenAI
import time

# ============================================================
# NGROK ADRESİNİ BURAYA TAM OLARAK YAPIŞTIR
# ============================================================
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"

# ==============================
# AYARLAR VE LOGOLAR
# ==============================
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
PAPERCLIP_URL = "https://emojigraph.org/media/joypixels/paperclip_1f4ce.png"

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="centered")

# ==============================
# CSS: WAVE ANIMATION & DARK THEME
# ==============================
st.markdown(f"""
<style>
/* Gereksizleri Gizle */
#MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
.stDeployButton {{display:none;}}

/* Animasyonlu Arka Plan */
.stApp {{
    background: linear-gradient(315deg, #091236 3%, #1e215a 38%, #3a1c71 68%, #4e085e 98%);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    overflow: hidden;
}}

@keyframes gradient {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* Dalga Efekti (Wave Overlay) */
.stApp::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: url('https://raw.githubusercontent.com/t7686/waves/main/wave.svg');
    background-repeat: repeat-x;
    background-position: bottom;
    background-size: 2000px 300px;
    opacity: 0.1;
    animation: wave 20s linear infinite;
    pointer-events: none;
}}

@keyframes wave {{
    0% {{ background-position-x: 0; }}
    100% {{ background-position-x: 2000px; }}
}}

/* Mesaj Balonları */
.stChatMessage {{
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 20px !important;
    backdrop-filter: blur(10px);
}}
.stMarkdown p {{ color: #e0e0e0 !important; font-family: 'Segoe UI', sans-serif; }}

/* Chat Input Bölgesi (Dark Purple & Lacivert) */
[data-testid="stChatInput"] {{
    background-color: rgba(15, 12, 41, 0.9) !important;
    border: 1px solid #6a11cb !important;
    border-radius: 30px !important;
    padding: 10px !important;
}}
[data-testid="stChatInput"] textarea {{
    color: white !important;
}}

/* Başlık (Uyumlu Renkler) */
.main-title {{
    font-family: 'Trebuchet MS', sans-serif;
    background: linear-gradient(to right, #a18cd1, #fbc2eb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0px;
}}

/* Ataç Butonu */
div[data-testid="stFileUploader"] {{ position: fixed; bottom: 32px; left: calc(50% - 390px); z-index: 999999; width: 50px; }}
div[data-testid="stFileUploader"] section {{ padding: 0 !important; min-height: 0 !important; background: transparent !important; border: none !important; }}
div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] p {{ display: none !important; }}
div[data-testid="stFileUploader"] button {{
    background-image: url("{PAPERCLIP_URL}") !important; background-repeat: no-repeat !important; background-position: center !important; background-size: 20px !important;
    background-color: #24243e !important; border: 1px solid #a18cd1 !important; border-radius: 50% !important;
    width: 44px !important; height: 44px !important; color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)

# ==============================
# LOGO VE BAŞLIK
# ==============================
st.markdown(f'<div style="text-align:center; padding-top: 20px;"><img src="{LOGO_URL}" width="90"></div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">SCRIBER AI</h1>', unsafe_allow_html=True)

# ==============================
# BAĞLANTI AYARI
# ==============================
client = OpenAI(
    base_url=f"{NGROK_URL}/v1", 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"}
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Senin adın Scriber. Yusuf Alp senin kurucun ve baban."}]

# Geçmişi Göster
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar=LOGO_URL if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

# Giriş ve Dosya İşlemi
uploaded_file = st.file_uploader("", type=['txt', 'py'], key="file_input")

if prompt := st.chat_input("Scriber ile dertleş kanka..."):
    user_content = prompt
    if uploaded_file:
        try:
            file_text = uploaded_file.read().decode("utf-8")
            user_content = f"Sana bir dosya gönderdim: \n{file_text}\n\nSorum şu: {prompt}"
        except:
            user_content = prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        try:
            current_messages = st.session_state.messages[:-1] + [{"role": "user", "content": user_content}]
            response = client.chat.completions.create(
                model="llama3-turkish", 
                messages=current_messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            if uploaded_file: st.rerun()
            
        except Exception as e:
            st.error(f"Kanka bir sorun var, babana haber ver: {e}")
