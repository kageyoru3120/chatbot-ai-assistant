import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load konfigurasi dari .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. Inisialisasi client Groq
client = Groq(api_key=GROQ_API_KEY)

# 3. Konfigurasi Tampilan Halaman Web
st.set_page_config(page_title="AI Assistant Kageyoru", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot AI Kageyoru")
st.caption("Ditenagai oleh Groq, Llama 3, dan Streamlit")
st.divider() # Garis pembatas

# 4. Membuat 'Ingatan' (Session State) agar chatbot ingat obrolan sebelumnya
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. Menampilkan riwayat obrolan di layar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Kotak input untuk mengetik pesan
user_input = st.chat_input("Ketik pesanmu di sini...")

if user_input:
    # Tampilkan pesan user ke layar
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Simpan pesan user ke dalam ingatan program
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Siapkan tempat untuk jawaban AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Sedang berpikir... 🤔")
        
        try:
            # Menyusun format pesan yang bisa dibaca oleh Groq
            groq_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            # Meminta jawaban dari AI Groq
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=groq_messages,
                temperature=0.7,
                max_tokens=1024,
            )
            
            ai_response = response.choices[0].message.content
            
            # Tampilkan jawaban asli dari AI
            message_placeholder.markdown(ai_response)
            
            # Simpan jawaban AI ke dalam ingatan program
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except Exception as e:
            message_placeholder.error(f"Waduh, terjadi kesalahan: {e}")