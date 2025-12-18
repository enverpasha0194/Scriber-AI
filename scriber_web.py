import streamlit as st
from openai import OpenAI

# ============================================================
# NGROK ADRESİNİ BURAYA TAM OLARAK YAPIŞTIR (v1 EKLEME!)
# ============================================================
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"

# ==============================
# AYARLAR VE LOGOLAR
# ==============================
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
PAPERCLIP_URL = "https://emojigraph.org/media/joypixels/paperclip_1f4ce.png"

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="centered")

# ==============================
# CSS: TEMİZ TASARIM
# ==============================
st.markdown(f"""
<style>
#MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
.stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}
.stChatMessage {{ background-color: rgba(255, 255, 255, 0.1) !important; color: white !important; border-radius: 15px !important; }}
.stMarkdown p {{ color: white !important; }}

/* ATAÇ BUTONU */
div[data-testid="stFileUploader"] {{ position: fixed; bottom: 28px; left: calc(50% - 395px); z-index: 999999; width: 50px; }}
div[data-testid="stFileUploader"] section {{ padding: 0 !important; min-height: 0 !important; background: transparent !important; border: none !important; }}
div[data-testid="stFileUploader"] label, div[data-testid="stFileUploader"] small, div[data-testid="stFileUploader"] p {{ display: none !important; }}
div[data-testid="stFileUploader"] button {{
    background-image: url("{PAPERCLIP_URL}") !important; background-repeat: no-repeat !important; background-position: center !important; background-size: 22px !important;
    background-color: rgba(20, 20, 20, 0.9) !important; border: 1px solid rgba(255, 255, 255, 0.4) !important; border-radius: 50% !important;
    width: 44px !important; height: 44px !important; color: transparent !important;
}}
</style>
""", unsafe_allow_html=True)

# ==============================
# BAĞLANTI (ÖNEMLİ GÜNCELLEME)
# ==============================
# Buraya headers ekledik ki Ngrok'un o meşhur uyarı ekranına takılmayalım
client = OpenAI(
    base_url=f"{NGROK_URL}/v1", 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"}
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Senin adın Scriber. Yusuf Alp senin kurucun ve baban."}]

st.markdown(f'<div style="text-align:center;"><img src="{LOGO_URL}" width="80"><h1>SCRIBER AI</h1></div>', unsafe_allow_html=True)

# Geçmişi Göster
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"], avatar=LOGO_URL if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])

# Giriş ve Dosya İşlemi
uploaded_file = st.file_uploader("", type=['txt', 'py'], key="file_input")

if prompt := st.chat_input("Scriber ile konuş..."):
    # Dosya varsa içeriğini prompt'a ekle (Görsel hatasını önlemek için)
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
            # Sadece bu istek için içeriği genişletiyoruz
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
            st.error(f"Kanka bir sorun var: {e}")
