import streamlit as st
import requests
import time
import uuid
from supabase import create_client

# =========================
# CONFIG (DOKUNMADIM)
# =========================
SUPABASE_URL = "https://rhenrzjfkiefhzfkkwgv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJoZW5yempma2llZmh6Zmtrd2d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYwNzY3MTMsImV4cCI6MjA4MTY1MjcxM30.gwjvIT5M8PyP9SBysXImyNblPm6XNwJTeZAayUeVCxU"
NGROK_BASE = "https://hydropathical-duodecastyle-camron.ngrok-free.dev"
LM_ENDPOINT = f"{NGROK_BASE}/v1/chat/completions"
MODEL_NAME = "qwen2.5-7b-instruct"

SYSTEM_PROMPT = """
Senin adın Scriber AI.
Net konuşursun.
Sansür yok ama boş laf da yok.
Teknik cevapları direkt verirsin.
"""

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

st.set_page_config("Scriber AI", "✍️", layout="wide")

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

# =========================
# AUTH (USERNAME ONLY)
# =========================
def login(username, password):
    r = supabase.table("scribble_users") \
        .select("*") \
        .eq("username", username) \
        .eq("password", password) \
        .execute()
    return r.data[0] if r.data else None

def register(username, password):
    exists = supabase.table("scribble_users") \
        .select("id") \
        .eq("username", username) \
        .execute()

    if exists.data:
        return None

    user = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": password
    }
    supabase.table("scribble_users").insert(user).execute()
    return user

# =========================
# LOGIN UI
# =========================
if not st.session_state.user:
    st.title("✍️ Scriber AI")

    tab1, tab2 = st.tabs(["Giriş", "Kayıt"])

    with tab1:
        u = st.text_input("Kullanıcı adı")
        p = st.text_input("Şifre", type="password")
        if st.button("Giriş"):
            user = login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre")

    with tab2:
        u = st.text_input("Kullanıcı adı", key="ru")
        p = st.text_input("Şifre", type="password", key="rp")
        if st.button("Kayıt Ol"):
            user = register(u, p)
            if user:
                st.success("Kayıt başarılı, giriş yap")
            else:
                st.error("Bu kullanıcı adı alınmış")

    st.stop()

# =========================
# LOAD CHATS
# =========================
def load_chats():
    r = supabase.table("scribble_chats") \
        .select("*") \
        .eq("user_id", st.session_state.user["id"]) \
        .order("created_at", desc=True) \
        .execute()
    return r.data or []

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 💬 Sohbetler")

    if st.button("➕ Yeni Sohbet"):
        st.session_state.active_chat = None
        st.session_state.messages = []

    for c in load_chats():
        if st.button(c["title"], key=c["id"]):
            st.session_state.active_chat = c
            m = supabase.table("scribble_messages") \
                .select("*") \
                .eq("chat_id", c["id"]) \
                .order("created_at") \
                .execute()
            st.session_state.messages = m.data or []

# =========================
# CHAT UI
# =========================
st.title("✍️ Scriber AI")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

user_input = st.chat_input("Yaz bakalım...")

# =========================
# CHAT LOGIC
# =========================
if user_input:
    if not st.session_state.active_chat:
        chat = supabase.table("scribble_chats").insert({
            "id": str(uuid.uuid4()),
            "user_id": st.session_state.user["id"],
            "title": user_input[:40]
        }).execute().data[0]

        st.session_state.active_chat = chat

    chat_id = st.session_state.active_chat["id"]

    supabase.table("scribble_messages").insert({
        "id": str(uuid.uuid4()),
        "chat_id": chat_id,
        "role": "user",
        "content": user_input
    }).execute()

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + st.session_state.messages
    }

    r = requests.post(LM_ENDPOINT, json=payload, timeout=120)
    reply = r.json()["choices"][0]["message"]["content"]

    supabase.table("scribble_messages").insert({
        "id": str(uuid.uuid4()),
        "chat_id": chat_id,
        "role": "assistant",
        "content": reply
    }).execute()

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    with st.chat_message("assistant"):
        box = st.empty()
        txt = ""
        for c in reply:
            txt += c
            box.markdown(txt)
            time.sleep(0.01)

    st.rerun()
