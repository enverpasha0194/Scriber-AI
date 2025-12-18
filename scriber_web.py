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
st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# CSS: BEYAZ ŞERİT YOK ETME & PARLAK YAZILAR
# ==============================
st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    .stApp {{ background: linear-gradient(315deg, #091236 0%, #1e215a 35%, #3a1c71 70%, #0f0c29 100%); }}
    
    /* BEYAZ ŞERİT İÇİN NİHAİ ÇÖZÜM */
    [data-testid="stBottomBlockContainer"] {{
        background: transparent !important;
        border: none !important;
    }}
    .st-emotion-cache-1y34ygi, .st-emotion-cache-128upt6, .st-emotion-cache-6shykm {{
        background-color: transparent !important;
    }}

    /* SCRIBER YAZILARI (Parlak Beyaz/Gümüş) */
    [data-testid="stChatMessageContent"] p {{
        color: #ffffff !important;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        text-shadow: 0px 0px 5px rgba(0,0,0,1);
    }}

    /* KULLANICI MESAJI (Sağa Yasla & İkon Sifirla) */
    div[data-testid="stChatMessage"]:has(span:contains("user")) {{
        flex-direction: row-reverse !important;
        background-color: transparent !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageAvatar"] {{
        display: none !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageContent"] {{
        background-color: rgba(106, 17, 203, 0.5) !important;
        border-radius: 20px 0px 20px 20px !important;
        text-align: right !important;
        margin-left: auto !important;
        max-width: 75%;
    }}

    /* YAN MENÜ (SIDEBAR) */
    [data-testid="stSidebar"] {{
        background-color: rgba(5, 5, 20, 0.95) !important;
        border-right: 1px solid #6a11cb;
    }}
    
    /* INPUT ALANI */
    div[data-testid="stChatInput"] {{
        background-color: rgba(15, 12, 41, 0.9) !important;
        border: 2px solid #6a11cb !important;
        border-radius: 25px !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# KAYIT / GİRİŞ SİSTEMİ
# ==============================
if "user" not in st.session_state:
    st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI - KAYIT</h1>', unsafe_allow_html=True)
    with st.form("auth_form"):
        username = st.text_input("Kullanıcı Adı Belirle:", placeholder="Örn: YusufAlp")
        password = st.text_input("Şifre Belirle:", type="password")
        if st.form_submit_button("Hesap Oluştur ve Giriş Yap"):
            if username and password:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Alanları boş bırakma kanka!")
    st.stop()

# Oturum Değişkenleri
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chats_list" not in st.session_state:
    st.session_state.chats_list = {} # {id: title}

# ==============================
# SIDEBAR (OTOMATİK SOHBET LİSTESİ)
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=70)
    st.write(f"👋 Merhaba, **{st.session_state.user}**")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()
    
    st.write("---")
    st.subheader("Sohbetlerin")
    for cid, title in st.session_state.chats_list.items():
        if st.button(title, key=cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            # Burada normalde Supabase'den o chat_id'ye ait mesajlar çekilir
            st.rerun()

# ==============================
# ANA EKRAN
# ==============================
st.markdown('<h1 style="text-align:center; color:white;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(base_url=f"{NGROK_URL}/v1", api_key="lm-studio")

# Mesajları Ekrana Yaz
for msg in st.session_state.chat_history:
    avatar = LOGO_URL if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Sohbet Girişi
if prompt := st.chat_input("Scriber'a bir şeyler yaz..."):
    # Eğer bu ilk mesajsa başlığı belirle ve yan menüye ekle
    if not st.session_state.chat_history:
        title = prompt[:20] + "..."
        st.session_state.chats_list[st.session_state.current_chat_id] = title

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
            
            # SUPABASE'E KAYDET
            supabase.table("messages").insert({
                "username": st.session_state.user,
                "role": "user",
                "content": prompt,
                "chat_id": st.session_state.current_chat_id,
                "chat_title": st.session_state.chats_list[st.session_state.current_chat_id]
            }).execute()

        except Exception as e:
            st.error(f"Hata: {e}")
