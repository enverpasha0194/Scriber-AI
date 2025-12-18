import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid
import bcrypt

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide"
)

# ==============================
# 🎨 GÜNCEL MODERN UI (PREMIUM STYLE)
# ==============================
st.markdown("""
<style>

/* === ANA ARKAPLAN VE ANİMASYON === */
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #1a1a2e, #16213e, #0f3460);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* === ALT PANEL TEMİZLİĞİ === */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"] {
    background: transparent !important;
    border: none !important;
}

/* === MODERN CHAT INPUT (SCRIBER'A YAZ) === */
div[data-testid="stChatInput"] {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(106, 17, 203, 0.3) !important;
    border-radius: 20px !important;
    padding: 5px !important;
    backdrop-filter: blur(10px); /* Buzlu cam efekti */
    margin-bottom: 20px !important;
}

textarea[data-testid="stChatInputTextArea"] {
    background-color: transparent !important;
    color: #ffffff !important;
    font-size: 16px !important;
    border: none !important;
}

/* Odaklanınca Parlama Efekti */
textarea[data-testid="stChatInputTextArea"]:focus {
    box-shadow: 0 0 15px rgba(106, 17, 203, 0.4) !important;
}

/* === MESAJ BALONLARI TASARIMI === */
[data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border-radius: 15px !important;
    margin-bottom: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Asistanın mesajı hafif farklı görünsün */
[data-testid="stChatMessageAssistant"] {
    background-color: rgba(106, 17, 203, 0.1) !important;
    border: 1px solid rgba(106, 17, 203, 0.2) !important;
}

/* === SIDEBAR MODERNE ETKİSİ === */
section[data-testid="stSidebar"] {
    background-color: rgba(10, 10, 25, 0.8) !important;
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(106, 17, 203, 0.3) !important;
}

/* Sidebar Butonları */
div.stButton > button {
    background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    transition: 0.3s all ease;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(106, 17, 203, 0.4);
}

/* Başlık ve Yazı Renkleri */
h1, h2, h3, p, span, label { 
    color: #e0e0e0 !important; 
    font-family: 'Segoe UI', sans-serif;
    letter-spacing: 0.5px;
}

/* Scrollbar'ı şık yap */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(106, 17, 203, 0.3); border-radius: 10px; }

</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 FONKSİYONLAR & AUTH
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; padding-top: 50px;'>SCRIBER AI</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,2,1])
    with col:
        if st.session_state.auth_mode == "login":
            u = st.text_input("Kullanıcı adı")
            p = st.text_input("Şifre", type="password")
            if st.button("Giriş Yap", use_container_width=True):
                res = supabase.table("scriber_users").select("*").eq("username", u).execute()
                if res.data and check_password(p, res.data[0]["password"]):
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Hatalı giriş")
            if st.button("Kayıt Ol"):
                st.session_state.auth_mode = "register"; st.rerun()
        else:
            u = st.text_input("Yeni kullanıcı adı")
            p1 = st.text_input("Şifre", type="password")
            p2 = st.text_input("Şifre tekrar", type="password")
            if st.button("Hesap Oluştur"):
                if p1 == p2:
                    supabase.table("scriber_users").insert({"username": u, "password": hash_password(p1)}).execute()
                    st.session_state.auth_mode = "login"; st.rerun()
                else: st.error("Şifreler uyuşmuyor")
    st.stop()

# ==============================
# 🧠 CHAT MANTIĞI
# ==============================
if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.image(LOGO_URL, width=120)
    st.markdown(f"### Hoş geldin, **{st.session_state.user}**")
    st.divider()
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.history = []; st.rerun()

st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

# Mesajları Görüntüle
for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

# Giriş Alanı
if prompt := st.chat_input("Scriber'a bir şeyler sor..."):
    st.session_state.history.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant", avatar=LOGO_URL):
        r = client.chat.completions.create(model="llama3-turkish", messages=st.session_state.history)
        reply = r.choices[0].message.content
        st.markdown(reply)
    st.session_state.history.append({"role":"assistant","content":reply})
