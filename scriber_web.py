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
# ✨ GÖRSEL DÜZENLEME: WAVE VE BEYAZ ŞERİT FİX
# ==============================
st.markdown(f"""
<style>
    /* 1. GERÇEK WAVE ANIMASYONU (Lacivert, Mor, Mavi Karışımı) */
    .stApp {{
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1e215a);
        background-size: 400% 400%;
        animation: gradient 10s ease infinite;
    }}
    
    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* 2. BEYAZ ŞERİDİ TAMAMEN SİL */
    [data-testid="stBottomBlockContainer"] {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }}
    .st-emotion-cache-1y34ygi, .e4man117, .st-emotion-cache-tn0cau {{
        background-color: transparent !important;
    }}

    /* 3. SOLDAKİ (SIDEBAR) BUTONLARI GÖRÜNÜR YAP */
    section[data-testid="stSidebar"] {{
        background-color: rgba(10, 10, 30, 0.9) !important;
    }}
    /* Sidebar'daki sohbet geçmişi butonları */
    div[data-testid="stSidebar"] button {{
        background-color: #6a11cb !important;
        color: white !important;
        border: 1px solid #9d50bb !important;
        font-weight: bold !important;
        text-align: left !important;
    }}

    /* 4. GENEL RENKLER VE HEADER SİLME */
    header, footer, #MainMenu {{visibility: hidden;}}
    p, span, label, h1 {{ color: white !important; }}
    
    /* Sohbet Giriş Kutusu */
    div[data-testid="stChatInput"] {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid #6a11cb !important;
        border-radius: 20px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 ŞİFRE VE AUTH SİSTEMİ (DOKUNULMADI)
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    try: return bcrypt.checkpw(pw.encode(), hashed.encode())
    except: return False

if "auth_mode" not in st.session_state: st.session_state.auth_mode = "login"

if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)
    if st.session_state.auth_mode == "login":
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", use_container_width=True):
            res = supabase.table("scriber_users").select("*").eq("username", username).execute()
            if res.data and check_password(password, res.data[0]["password"]):
                st.session_state.user = res.data[0]["username"]
                st.rerun()
            else: st.error("Hatalı giriş!")
        if st.button("Kayıt Ol", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()
    else:
        u_reg = st.text_input("Yeni Kullanıcı Adı")
        p_reg = st.text_input("Yeni Şifre", type="password")
        if st.button("Hesap Oluştur", use_container_width=True):
            supabase.table("scriber_users").insert({"username": u_reg, "password": hash_password(p_reg)}).execute()
            st.success("Kayıt başarılı! Giriş yapabilirsin.")
            st.session_state.auth_mode = "login"
            st.rerun()
    st.stop()

# ==============================
# 🧠 SOHBET GEÇMİŞİ VE SIDEBAR
# ==============================
if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.write(f"👤 **{st.session_state.user}**")
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()
    st.write("---")
    # Geçmiş sohbetleri çek
    chats = supabase.table("messages").select("chat_id, chat_title").eq("username", st.session_state.user).execute()
    seen = set()
    for c in chats.data:
        if c["chat_id"] not in seen and c["chat_title"]:
            seen.add(c["chat_id"])
            if st.button(c["chat_title"], key=c["chat_id"], use_container_width=True):
                msgs = supabase.table("messages").select("role,content").eq("chat_id", c["chat_id"]).order("created_at").execute()
                st.session_state.chat_id = c["chat_id"]
                st.session_state.history = msgs.data
                st.rerun()

# ==============================
# 🤖 CHAT EKRANI
# ==============================
st.markdown("<h1 style='text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

# Geçmişi Basarken Logo Kullanımı
for msg in st.session_state.history:
    # Robot yerine Scriber Logosu (assistant için)
    avatar_img = LOGO_URL if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    st.session_state.history.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL): # Robot yerine logo
        placeholder = st.empty()
        full = ""
        stream = client.chat.completions.create(model="llama3-turkish", messages=st.session_state.history, stream=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                placeholder.markdown(full + "▌")
        placeholder.markdown(full)
        st.session_state.history.append({"role":"assistant","content":full})

    # Veritabanına kaydet
    title = prompt[:30] + "..."
    supabase.table("messages").insert([
        {"username": st.session_state.user, "role": "user", "content": prompt, "chat_id": st.session_state.chat_id, "chat_title": title},
        {"username": st.session_state.user, "role": "assistant", "content": full, "chat_id": st.session_state.chat_id, "chat_title": title}
    ]).execute()
