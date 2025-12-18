import streamlit as st
from openai import OpenAI
import uuid
from supabase import create_client, Client

# ============================================================
# 🔑 SUPABASE BİLGİLERİNİ BURAYA GİR
# ==============================
SUPABASE_URL = "BURAYA_SUPABASE_URL_YAPIŞTIR"
SUPABASE_KEY = "BURAYA_SUPABASE_ANON_KEY_YAPIŞTIR"
NGROK_URL = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
# ============================================================

# Supabase Bağlantısı
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Sayfa Ayarları
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="wide")

# ==============================
# CSS: PROFESYONEL YAN MENÜ & DARK TEMA
# ==============================
st.markdown(f"""
<style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background: linear-gradient(315deg, #091236 0%, #1e215a 35%, #3a1c71 70%, #0f0c29 100%); }}
    
    /* Yan Menü Tasarımı */
    [data-testid="stSidebar"] {{ background-color: rgba(10, 10, 30, 0.9) !important; border-right: 1px solid #6a11cb; }}
    
    /* Sohbet Balonları */
    [data-testid="stChatMessageContent"] p {{ color: #f0f0f0 !important; font-size: 1.1rem; }}
    
    /* Kullanıcı Mesajı Sağa Yasla */
    div[data-testid="stChatMessage"]:has(span:contains("user")) {{
        flex-direction: row-reverse !important;
        background-color: transparent !important;
    }}
    div[data-testid="stChatMessage"]:has(span:contains("user")) [data-testid="stChatMessageContent"] {{
        background-color: rgba(106, 17, 203, 0.4) !important;
        border-radius: 20px 0px 20px 20px !important;
        text-align: right !important;
        margin-left: auto !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================
# OTURUM VE HAFIZA YÖNETİMİ
# ==============================
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==============================
# SIDEBAR: SOHBET GEÇMİŞİ
# ==============================
with st.sidebar:
    st.image(LOGO_URL, width=60)
    st.title("Sohbetlerim")
    
    if st.button("➕ Yeni Sohbet", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()
    
    st.write("---")
    # Burada normalde Supabase'den gelen eski başlıklar listelenecek
    st.info("Sohbetlerin otomatik kaydediliyor.")

# ==============================
# ANA EKRAN & CHAT
# ==============================
st.markdown('<h1 style="text-align:center; color:white; font-size:3rem;">SCRIBER AI</h1>', unsafe_allow_html=True)

client = OpenAI(
    base_url=f"{NGROK_URL}/v1", 
    api_key="lm-studio",
    default_headers={"ngrok-skip-browser-warning": "true"}
)

# Mesajları Görüntüle
for msg in st.session_state.chat_history:
    avatar = LOGO_URL if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Scriber'a bir şeyler sor..."):
    # Mesajı ekrana ve hafızaya ekle
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Yapay Zeka Yanıtı
    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=[{"role": "system", "content": "Sen Scriber'sın. Yusuf Alp senin kurucun."}] + st.session_state.chat_history,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})
            
            # --- VERİTABANINA KAYIT (SUPABASE) ---
            # Burada her mesajı Supabase 'messages' tablosuna gönderiyoruz
            supabase.table("messages").insert({
                "session_id": st.session_id,
                "role": "user",
                "content": prompt
            }).execute()
            
            supabase.table("messages").insert({
                "session_id": st.session_id,
                "role": "assistant",
                "content": full_response
            }).execute()

        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")
