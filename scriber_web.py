import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid
import bcrypt

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "ANON_KEY"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# 🎨 CSS – RENK + BEYAZ ŞERİT YOK EDİLDİ
# ==============================
st.markdown("""
<style>
/* GENEL */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display:none;}

.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e215a);
    background-size: 400% 400%;
    animation: gradient 10s ease infinite;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* 🔥 BEYAZ ŞERİT = ÖLDÜ */
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInput"],
.stChatInput,
.st-emotion-cache-1y34ygi,
.st-emotion-cache-tn0cau,
.st-emotion-cache-1eeryuo {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* CHAT INPUT TEXTAREA */
textarea[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    color: #c7c9ff !important;
    caret-color: #9aa0ff !important;
    font-size: 1.05rem !important;
}

/* PLACEHOLDER */
textarea::placeholder {
    color: #9aa0ff !important;
    opacity: 0.85 !important;
}

/* GÖNDER BUTONU */
button[data-testid="stChatInputSubmitButton"] {
    background: transparent !important;
    color: #9aa0ff !important;
}

/* CHAT MESAJ YAZILARI */
[data-testid="stChatMessageContent"] p {
    color: #c7c9ff !important;
    text-shadow: 0 0 6px rgba(80,80,160,0.4);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(10,10,30,0.92) !important;
}
section[data-testid="stSidebar"] * {
    color: #c7c9ff !important;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 AUTH
# ==============================
def hash_password(pw): return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
def check_password(pw, h): return bcrypt.checkpw(pw.encode(), h.encode())

if "user" not in st.session_state:
    u = st.text_input("Kullanıcı adı")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        r = supabase.table("scriber_users").select("*").eq("username", u).execute()
        if r.data and check_password(p, r.data[0]["password"]):
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Hatalı giriş")
    st.stop()

# ==============================
# 🧠 SESSION
# ==============================
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# 🤖 CHAT
# ==============================
st.markdown("<h1 style='text-align:center;color:#c7c9ff'>SCRIBER AI</h1>", unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for m in st.session_state.history:
    with st.chat_message(m["role"], avatar=LOGO_URL if m["role"]=="assistant" else None):
        st.markdown(m["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    st.session_state.history.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        out = ""
        box = st.empty()
        stream = client.chat.completions.create(
            model="llama3-turkish",
            messages=st.session_state.history,
            stream=True
        )
        for c in stream:
            if c.choices[0].delta.content:
                out += c.choices[0].delta.content
                box.markdown(out + "▌")
        box.markdown(out)
        st.session_state.history.append({"role":"assistant","content":out})
