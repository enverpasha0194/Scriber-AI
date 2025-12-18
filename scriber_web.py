import streamlit as st
from openai import OpenAI
from supabase import create_client, Client

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU" # Burayı doldurmayı unutma kanka!
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

# Supabase Bağlantısı
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# CSS: BEYAZ ŞERİT VE İKON SİLEN NİHAİ TASARIM
# ==============================
st.markdown(f"""
<style>
    /* 1. GENEL AYARLAR */
    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}

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

    /* 2. ALTAKİ BEYAZ ŞERİDİ KESİN SİL (Senin Gönderdiğin HTML'e Göre) */
    [data-testid="stBottomBlockContainer"], 
    .st-emotion-cache-1y34ygi, 
    .st-emotion-cache-128upt6 {{
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* 3. MESAJLAR: KULLANICI İKONU SİL VE SAĞA YASLA */
    div[data-testid="stChatMessage"]:has(span:contains("user")) {{
        flex-direction: row-reverse !important;
        background-color: transparent !important;
    }}
    
    /* Kullanıcı İkonu Gizle */
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}

    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageContent"] {{
        background-color: rgba(106, 17, 203, 0.4) !important;
        border-radius: 20px 0px 20px 20px !important;
        text-align: right !important;
        margin-left: auto !important;
        max-width: 80%;
    }}

    /* Scriber Mesajları (Parlak Gümüş) */
    [data-testid="stChatMessageContent"] p {{
        color: #f0f0f0 !important;
        font-size: 1.1rem;
    }}

    /* 4. CHAT INPUT */
    div[data-testid="stChatInput"] {{
        background-color: rgba(15, 12, 41, 0.95) !important;
        border: 2px solid #6a11cb !important;
        border-radius: 25px !important;
    }}
    
    div[data-testid="stChatInputTextArea"] textarea {{
        color: #d1a3ff !important;
    }}

    /* 5. SIDEBAR (YAN MENÜ) */
    [data-testid="stSidebar"] {{
        background-color: rgba(10, 10, 30, 0.95) !important;
        border-right: 1px solid #6a11cb;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# GİRİŞ VE OTURUM
# ==============================
if "user_email" not in st.session_state:
    st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)
    email = st.text_input("Giriş yapmak için e-postanı yaz kanka:")
    if st.button("Google ile Devam Et (Simüle)"):
        st.session_state.user_email = email
        st.rerun()
    st.stop()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=60)
    st.subheader(f"👤 {st.session_state.user_email}")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    st.write("---")
    st.write("📌 Sohbetlerin otomatik kaydediliyor.")

# ==============================
# ANA EKRAN
# ==============================
st.markdown('<h1 style="text-align:center; color:white; font-size: 3rem;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(
    base_url=f"{NGROK_URL}/v1", 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"}
)

# Mesajları Göster
for msg in st.session_state.chat_history:
    avatar = LOGO_URL if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Giriş
if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=st.session_state.chat_history,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            
            # SUPABASE KAYIT
            supabase.table("messages").insert({
                "user_email": st.session_state.user_email,
                "role": "user",
                "content": prompt,
                "chat_title": prompt[:20]
            }).execute()
            
            supabase.table("messages").insert({
                "user_email": st.session_state.user_email,
                "role": "assistant",
                "content": full_response,
                "chat_title": prompt[:20]
            }).execute()

        except Exception as e:
            st.error(f"Hata oluştu kanka: {e}")
