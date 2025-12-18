import streamlit as st
from openai import OpenAI

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
# CSS: BEYAZ ŞERİDİ KESİN SİLEN TASARIM
# ==============================
st.markdown(f"""
<style>
/* 1. TÜM GEREKSİZLERİ GİZLE */
#MainMenu, footer, header {{visibility: hidden;}}
.stDeployButton {{display:none;}}

/* 2. ARKA PLAN ANIMASYONU */
.stApp {{
    background: linear-gradient(315deg, #091236 0%, #1e215a 35%, #3a1c71 70%, #0f0c29 100%);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}}

@keyframes gradient {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* 3. ALTAKİ BEYAZ ŞERİDİ KESİN YOK ETME (image_e7b20b.jpg Çözümü) */
/* Burası alt paneli tamamen görünmez yapar ve ana arka planın görünmesini sağlar */
[data-testid="stBottom"] {{
    background-color: transparent !important;
    border: none !important;
}}

.stChatInputContainer {{
    background-color: transparent !important;
    border: none !important;
    bottom: 20px !important;
}}

/* 4. YAZMA BÖLMESİ (Chat Input) */
div[data-testid="stChatInput"] {{
    background-color: rgba(15, 12, 41, 0.9) !important;
    border: 2px solid #6a11cb !important;
    border-radius: 25px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.6);
}}

/* 5. YAZDIĞIN YAZI RENGİ */
div[data-testid="stChatInput"] textarea {{
    color: #d1a3ff !important; /* Parlak lila/mor */
    -webkit-text-fill-color: #d1a3ff !important;
}}

/* 6. ATAÇ ÜSTÜNDEKİ YAZILARI SİL */
div[data-testid="stFileUploader"] section {{
    display: flex !important;
    justify-content: center !important;
    padding: 0 !important;
    min-height: 0 !important;
    background: transparent !important;
    border: none !important;
}}
div[data-testid="stFileUploader"] label, 
div[data-testid="stFileUploader"] small, 
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] {{
    display: none !important;
}}

/* 7. ATAÇ BUTONU */
div[data-testid="stFileUploader"] {{
    position: fixed;
    bottom: 35px;
    left: calc(50% - 380px);
    z-index: 999999;
    width: 45px;
}}
div[data-testid="stFileUploader"] button {{
    background-image: url("{PAPERCLIP_URL}") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 20px !important;
    background-color: #1e215a !important;
    border: 1px solid #6a11cb !important;
    border-radius: 50% !important;
    width: 42px !important;
    height: 42px !important;
    color: transparent !important;
}}

/* 8. SCRIBER AI BAŞLIĞI */
.main-title {{
    background: linear-gradient(to right, #6a11cb, #2575fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.5rem;
    font-weight: 800;
    text-align: center;
    margin-top: -10px;
}}

/* Mesaj Balonları */
.stChatMessage {{
    background-color: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(8px);
    border-radius: 15px !important;
    border: 1px solid rgba(106, 17, 203, 0.2) !important;
    margin-bottom: 10px !important;
}}
</style>
""", unsafe_allow_html=True)

# ==============================
# ARAYÜZ KURULUMU
# ==============================
st.markdown(f'<div style="text-align:center; padding-top: 10px;"><img src="{LOGO_URL}" width="90"></div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">SCRIBER AI</h1>', unsafe_allow_html=True)

# ==============================
# BAĞLANTI (Ngrok/LM Studio)
# ==============================
client = OpenAI(
    base_url=f"{NGROK_URL}/v1", 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"}
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Senin adın Scriber. Yusuf Alp senin baban."}]

# Mesaj Geçmişini Göster
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar=LOGO_URL if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

# Giriş Bölümü
uploaded_file = st.file_uploader("", type=['txt', 'py'], key="file_input")

if prompt := st.chat_input("Scriber'e bir şeyler yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model="llama3-turkish", 
                messages=st.session_state.messages,
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
            st.error(f"Bağlantı Hatası: {e}")
