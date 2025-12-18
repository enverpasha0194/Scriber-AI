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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# ✨ WAVE ANIMASYONU VE GÖRSEL DÜZENLEME (YENİ)
# ==============================
st.markdown(f"""
<style>
    /* 1. DALGALI ARKA PLAN ANIMASYONU */
    .stApp, [data-testid="stAppViewContainer"] {{
        background: linear-gradient(-45deg, #091236, #1e215a, #3a1c71, #0f0c29);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: white !important;
    }}
    
    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* 2. BEYAZ ŞERİT VE ALT KATMAN TEMİZLİĞİ */
    div[data-testid="stBottomBlockContainer"],
    .st-emotion-cache-1y34ygi,
    .e4man117,
    .st-emotion-cache-tn0cau,
    .ek2vi383,
    .st-emotion-cache-1vo6xi6,
    .ek2vi381 {{
        background: transparent !important;
        background-color: transparent !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* 3. SIDEBAR STİLİ */
    section[data-testid="stSidebar"] {{
        background-color: rgba(5, 5, 20, 0.95) !important;
        border-right: 2px solid #6a11cb !important;
    }}

    /* 4. GENEL YAZI RENKLERİ */
    #MainMenu, footer, header {{visibility: hidden;}}
    p, span, label, h1 {{ color: #ffffff !important; }}
    
    /* Input Alanı Düzenlemesi */
    div[data-testid="stChatInput"] {{
        background-color: rgba(15, 12, 41, 0.9) !important;
        border: 10px solid #6a11cb !important; /* Belirginleştirilmiş mor kenarlık */
        border-radius: 25px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# 🔐 ŞİFRE
# ==============================
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except:
        return False

# ==============================
# 🔐 AUTH STATE
# ==============================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "user" not in st.session_state:
    st.markdown("<h1 style='color:white;text-align:center'>SCRIBER AI</h1>", unsafe_allow_html=True)

    # ---------- LOGIN ----------
    if st.session_state.auth_mode == "login":
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")

        if st.button("Giriş Yap", use_container_width=True):
            res = supabase.table("scriber_users").select("*").eq("username", username).execute()

            if not res.data:
                st.error("Kullanıcı yok")
                st.stop()

            user = res.data[0]

            if not check_password(password, user["password"]):
                st.error("Şifre yanlış")
                st.stop()

            st.session_state.user = user["username"]
            st.session_state.user_id = user["id"]
            st.rerun()

        if st.button("Hesabın yok mu? Kayıt Ol", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()

    # ---------- REGISTER ----------
    else:
        username = st.text_input("Kullanıcı adı")
        password = st.text_input("Şifre", type="password")
        password2 = st.text_input("Şifre (tekrar)", type="password")

        if st.button("Hesap Oluştur", use_container_width=True):
            if password != password2:
                st.error("Şifreler uyuşmuyor")
                st.stop()

            exists = supabase.table("scriber_users").select("id").eq("username", username).execute()
            if exists.data:
                st.error("Bu kullanıcı adı alınmış")
                st.stop()

            supabase.table("scriber_users").insert({
                "username": username,
                "password": hash_password(password)
            }).execute()

            st.success("Kayıt tamam, giriş yap")
            st.session_state.auth_mode = "login"
            st.rerun()
            
        if st.button("Zaten hesabın var mı? Giriş Yap", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()

    st.stop()

# ==============================
# 🧠 SESSION
# ==============================
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

# ==============================
# 🧭 SIDEBAR
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.write(f"👤 **{st.session_state.user}**")

    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()

    st.write("---")

    chats = supabase.table("messages") \
        .select("chat_id, chat_title") \
        .eq("username", st.session_state.user) \
        .execute()

    seen = set()
    for c in chats.data:
        if c["chat_id"] not in seen and c["chat_title"]:
            seen.add(c["chat_id"])
            if st.button(c["chat_title"], key=c["chat_id"], use_container_width=True):
                msgs = supabase.table("messages") \
                    .select("role,content") \
                    .eq("chat_id", c["chat_id"]) \
                    .order("created_at") \
                    .execute()
                st.session_state.chat_id = c["chat_id"]
                st.session_state.history = msgs.data
                st.rerun()

# ==============================
# 🤖 CHAT
# ==============================
st.markdown("<h1 style='text-align:center;color:white'>SCRIBER AI</h1>", unsafe_allow_html=True)

client = OpenAI(
    base_url=f"{NGROK_URL}/v1",
    api_key="lm-studio"
)

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):

    st.session_state.history.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""

        stream = client.chat.completions.create(
            model="llama3-turkish",
            messages=st.session_state.history,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                placeholder.markdown(full + "▌")

        placeholder.markdown(full)
        st.session_state.history.append({"role":"assistant","content":full})

    title = prompt[:30] + "..."

    supabase.table("messages").insert({
        "username": st.session_state.user,
        "role": "user",
        "content": prompt,
        "chat_id": st.session_state.chat_id,
        "chat_title": title
    }).execute()

    supabase.table("messages").insert({
        "username": st.session_state.user,
        "role": "assistant",
        "content": full,
        "chat_id": st.session_state.chat_id,
        "chat_title": title
    }).execute()
