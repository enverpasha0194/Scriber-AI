import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
import uuid

# ==============================
# 🔑 AYARLAR
# ==============================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide", initial_sidebar_state="expanded")

# ==============================
# CSS: WAVE ANIMASYONU VE SIDEBAR FIX
# ==============================
st.markdown(f"""
<style>
    /* 1. WAVE ANIMASYONLU ARKA PLAN (Giriş dahil her yer) */
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

    /* 2. SIDEBAR (YAN MENÜ) ZORLAMA */
    section[data-testid="stSidebar"] {{
        background-color: rgba(5, 5, 20, 0.95) !important;
        border-right: 2px solid #6a11cb !important;
        visibility: visible !important;
        display: block !important;
    }}

    /* 3. BEYAZ ŞERİT VE GEREKSİZ ELEMENTLERİ SİL */
    #MainMenu, footer, header {{visibility: hidden;}}
    [data-testid="stBottomBlockContainer"] {{ background: transparent !important; border: none !important; }}
    .st-emotion-cache-1y34ygi, .st-emotion-cache-6shykm {{ background-color: transparent !important; }}

    /* 4. YAZILAR VE INPUT */
    p, span, label {{ color: #ffffff !important; }}
    div[data-testid="stChatInput"] {{
        background-color: rgba(15, 12, 41, 0.9) !important;
        border: 2px solid #6a11cb !important;
        border-radius: 25px !important;
    }}
    
    /* Sekme (Tabs) Tasarımı */
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent !important; }}
    .stTabs [data-baseweb="tab"] {{ color: white !important; border-bottom: 2px solid transparent; }}
    .stTabs [data-baseweb="tab--active"] {{ border-bottom: 2px solid #6a11cb !important; }}
</style>
""", unsafe_allow_html=True)

# ==============================
# GİRİŞ / KAYIT EKRANI
# ==============================
if "user" not in st.session_state:
    st.markdown(f'<div style="text-align:center"><img src="{LOGO_URL}" width="100"></div>', unsafe_allow_html=True)
    st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol"])
    
    with tab1:
        with st.form("l_form"):
            u = st.text_input("Kullanıcı Adı")
            p = st.text_input("Şifre", type="password")
            if st.form_submit_button("Giriş Yap"):
                res = supabase.table("scriber_users").select("*").eq("username", u).eq("password", p).execute()
                if res.data:
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre yanlış!")

    with tab2:
        with st.form("r_form"):
            u_r = st.text_input("Kullanıcı Adı Belirle")
            p_r = st.text_input("Şifre Belirle", type="password")
            if st.form_submit_button("Hesap Oluştur"):
                if u_r and p_r:
                    try:
                        supabase.table("scriber_users").insert({"username": u_r, "password": p_r}).execute()
                        st.success("Kayıt başarılı! Şimdi giriş yapabilirsin.")
                    except:
                        st.error("Bu kullanıcı adı alınmış!")
                else:
                    st.warning("Eksik bilgi girmeyin.")
    st.stop()

# ==============================
# OTURUM VE SIDEBAR
# ==============================
if "chat_id" not in st.session_state: st.session_state.chat_id = str(uuid.uuid4())
if "history" not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown(f"### 👤 {st.session_state.user}")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()
    
    st.write("---")
    st.subheader("Sohbet Geçmişi")
    # Kullanıcının benzersiz chat_id'lerini ve başlıklarını çek
    hist_data = supabase.table("messages").select("chat_id, chat_title").eq("username", st.session_state.user).execute()
    
    unique_chats = {}
    for d in hist_data.data:
        if d['chat_id'] not in unique_chats:
            unique_chats[d['chat_id']] = d['chat_title']
    
    for cid, title in unique_chats.items():
        if st.button(title or "Adsız Sohbet", key=cid, use_container_width=True):
            st.session_state.chat_id = cid
            msgs = supabase.table("messages").select("*").eq("chat_id", cid).order("created_at").execute()
            st.session_state.history = [{"role": m['role'], "content": m['content']} for m in msgs.data]
            st.rerun()

# ==============================
# ANA CHAT EKRANI
# ==============================
st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

for msg in st.session_state.history:
    with st.chat_message(msg["role"], avatar=LOGO_URL if msg["role"]=="assistant" else None):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scriber'a yaz..."):
    # Yapay zeka tanıtımı
    sys_prompt = f"Adın Scriber. Karşındaki kişi {st.session_state.user}. Ona ismiyle hitap et."
    
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_res = ""
        response = client.chat.completions.create(
            model="llama3-turkish",
            messages=[{"role": "system", "content": sys_prompt}] + st.session_state.history,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                placeholder.markdown(full_res + "▌")
        placeholder.markdown(full_res)
        st.session_state.history.append({"role": "assistant", "content": full_res})

        # VERİTABANI KAYIT
        chat_title = prompt[:20] + "..."
        supabase.table("messages").insert([
            {"username": st.session_state.user, "role": "user", "content": prompt, "chat_id": st.session_state.chat_id, "chat_title": chat_title},
            {"username": st.session_state.user, "role": "assistant", "content": full_res, "chat_id": st.session_state.chat_id, "chat_title": chat_title}
        ]).execute()

