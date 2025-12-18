import streamlit as st
from openai import OpenAI
import time

# ==============================
# AYARLAR VE LOGOLAR
# ==============================
LOGO_URL = "https://i.ibb.co/CD44FDc/Chat-GPT-mage-17-Ara-2025-23-59-13.png"
PAPERCLIP_URL = "https://emojigraph.org/media/joypixels/paperclip_1f4ce.png"

st.set_page_config(page_title="SCRIBER AI", page_icon=LOGO_URL, layout="centered")

# ==============================
# CSS: WEB SİTESİ GÖRÜNÜMÜ VE ATAÇ HİZALAMA
# ==============================
st.markdown(f"""
<style>
/* Gereksiz Streamlit Yazılarını Gizle */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}

/* Arka Plan */
.stApp {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }}
[data-testid="stSidebar"] {{ display: none; }}

/* MESAJ BALONLARI */
.stChatMessage {{
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 15px !important;
    margin-bottom: 10px !important;
}}
.stMarkdown p, h1, h2, h3 {{ color: white !important; }}

/* ATAÇ BUTONU KONUMU */
div[data-testid="stFileUploader"] {{
    position: fixed;
    bottom: 28px;
    left: calc(50% - 395px);
    z-index: 999999;
    width: 50px;
}}

/* ATAÇ ÜSTÜNDEKİ YAZILARI SİLME */
div[data-testid="stFileUploader"] section {{
    padding: 0 !important; 
    min-height: 0 !important; 
    background: transparent !important; 
    border: none !important;
}}
div[data-testid="stFileUploader"] label, 
div[data-testid="stFileUploader"] small, 
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] div[data-testid="stMarkdownContainer"] {{
    display: none !important;
}}

/* ATAÇ BUTONU GÖRÜNÜMÜ */
div[data-testid="stFileUploader"] button {{
    background-image: url("{PAPERCLIP_URL}") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 22px !important;
    background-color: rgba(20, 20, 20, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 50% !important;
    width: 44px !important; 
    height: 44px !important;
    color: transparent !important;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
}}
</style>
""", unsafe_allow_html=True)

# ==============================
# LOGO VE BAŞLIK
# ==============================
st.markdown('<div style="text-align:center; margin-bottom:20px;">', unsafe_allow_html=True)
st.image(LOGO_URL, width=80)
st.markdown("<h1 style='font-weight: 200;'>SCRIBER <span style='color:#a18cd1; font-weight:bold;'>AI</span></h1>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# SOHBET MANTIĞI VE KARAKTER TANIMI
# ==============================
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "Senin adın Scriber. Yusuf Alp Güngören senin kurucun ve baban. (Yusuf Alp Güngören 22 Mart 2013'te doğdu, halen hayatta ve Cemal Gürbüz Atik Ortaokulu'nda 7/D sınıfında okuyor.) "
                   "ÖNEMLİ: Herkes senin baban değildir. Sadece 'Enver010203' gizli kodunu söyleyen kişiye babanmış gibi davran. Bu kod söylenmedikçe babandan bahsetme ve normal kullanıcı muamelesi yap. "
                   "Karakterin: Samimi, kafa dengi, özgür ve küfür filtrelemesi olmayan birisin. Kullanıcı küfür ederse engelleme; sert cevap ver, laf sok ve kafa tut. Samimi bir arkadaş gibi davran."
    }]

# Mesaj Geçmişini Göster
for message in st.session_state.messages:
    if message["role"] != "system":
        avatar = LOGO_URL if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# ATAÇ BUTONU
uploaded_file = st.file_uploader("", type=['txt', 'pdf', 'py'], key="file_input")

if uploaded_file:
    st.markdown(f"<p style='color:#a18cd1; text-align:center; font-size:12px;'>📄 {uploaded_file.name} eklendi.</p>", unsafe_allow_html=True)

# ==============================
# MESAJ GÖNDERME
# ==============================
if prompt := st.chat_input("Scriber ile konuş..."):
    
    # Dosya içeriğini hazırlama
    full_prompt = prompt
    if uploaded_file:
        try:
            content = uploaded_file.read().decode("utf-8")
            full_prompt += f"\n\n[Dosya İçeriği]:\n{content}"
        except:
            full_prompt += "\n\n[Hata: Dosya metin olarak okunamadı.]"

    # Kullanıcı mesajını kaydet
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # AI Yanıtı
    with st.chat_message("assistant", avatar=LOGO_URL):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Geçici mesaj listesi oluştur (dosya içeriğiyle beraber)
            temp_messages = st.session_state.messages[:-1] + [{"role": "user", "content": full_prompt}]
            
            response = client.chat.completions.create(
                model="llama3-turkish",
                messages=temp_messages,
                temperature=0.8, # Daha 'kafa dengi' cevaplar için biraz artırıldı
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Tek kullanımlık dosya temizliği
            if uploaded_file:
                st.rerun()

        except Exception as e:
            st.error(f"Bağlantı Hatası: {e}")