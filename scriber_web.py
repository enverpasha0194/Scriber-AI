import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid
import bcrypt

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "ANON_KEYİN"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="SCRIBER AI",
    page_icon=LOGO_URL,
    layout="wide"
)

# ==============================
# 🎨 CSS
# ==============================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e215a);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

button,
div[data-testid="stButton"] > button {
    background-color: #393863 !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] {
    background-color: rgba(5,5,20,0.9) !important;
}

h1,h2,h3,p,span,label,div { color: white !important; }
header, footer, #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
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
                st.session_state.auth_mode = "register"
                st.rerun()
        else:
            u = st.text_input("Yeni kullanıcı adı")
            p1 = st.text_input("Şifre", type="password")
            p2 = st.text_input("Şifre tekrar", type="password")
            if st.button("Hesap Oluştur"):
                if p1 == p2:
                    supabase.table("scriber_users").insert({
                        "username": u,
                        "password": hash_password(p1)
                    }).execute()
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("Şifreler uyuşmuyor")
    st.stop()

# ==============================
# 🧠 MULTI CHAT STATE
# ==============================
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "active_chat" not in st.session_state:
    cid = str(uuid.uuid4())
    st.session_state.active_chat = cid
    st.session_state.chats[cid] = []

# ==============================
# 📚 SIDEBAR – SOHBETLER
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=90)
    st.write(f"👤 {st.session_state.user}")
    st.divider()

    if st.button("➕ Yeni Sohbet", use_container_width=True):
        cid = str(uuid.uuid4())
        st.session_state.chats[cid] = []
        st.session_state.active_chat = cid
        st.rerun()

    st.divider()
    st.markdown("### 💬 Sohbetler")

    for cid, history in st.session_state.chats.items():
        title = history[0]["content"][:20] if history else "Yeni Sohbet"
        if st.button(title, key=cid, use_container_width=True):
            st.session_state.active_chat = cid
            st.rerun()

# ==============================
# 💬 CHAT EKRANI
# ==============================
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

client = OpenAI(
    base_url=f"{NGROK_URL}/v1",
    api_key="lm-studio"
)

history = st.session_state.chats[st.session_state.active_chat]

for msg in history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=LOGO_URL):
        r = client.chat.completions.create(
            model="llama3-turkish",
            messages=history
        )
        reply = r.choices[0].message.content
        st.markdown(reply)

    history.append({"role": "assistant", "content": reply})
