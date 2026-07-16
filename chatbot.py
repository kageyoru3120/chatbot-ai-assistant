import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load environment variables dari file .env
load_dotenv()

# 2. Ambil API Key dari .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ Error: GROQ_API_KEY tidak ditemukan di file .env!")
    exit(1)

# 3. Inisialisasi Client Groq
client = Groq(api_key=GROQ_API_KEY)

def start_chat():
    print("\n==================================================")
    print("⚡ Groq AI (Llama 3) - Content Brainstorming Chatbot")
    print("==================================================")
    print("Ketik 'keluar' atau 'exit' untuk mengakhiri chat.\n")
    
    # Membuat sistem penyimpanan riwayat chat manual (memori chatbot)
    history = [
        {
            "role": "system",
            "content": (
                "Kamu adalah asisten kreatif khusus untuk membantu konten kreator "
                "melakukan brainstorming ide konten. Berikan jawaban yang terstruktur, "
                "kreatif, interaktif, dan mudah dipahami."
            )
        }
    ]
    
    while True:
        try:
            user_input = input("👤 Kamu: ")
            
            # Cek kondisi keluar
            if user_input.lower() in ['keluar', 'exit']:
                print("\n🤖 Assistant: Sampai jumpa! Semangat bikin kontennya! 🚀")
                break
                
            if not user_input.strip():
                continue
                
            print("🤖 Assistant sedang berpikir...")
            
            # Masukkan input kamu ke dalam riwayat
            history.append({"role": "user", "content": user_input})
            
            # Kirim seluruh riwayat obrolan ke Groq API
            chat_completion = client.chat.completions.create(
                messages=history,
                model="llama-3.1-8b-instant",  # Model gratis terbaik, super cepat, dan andal di Groq
            )
            
            # Ambil balasan teks dari AI
            response_text = chat_completion.choices[0].message.content
            
            # Simpan balasan AI ke riwayat agar diingat pada chat berikutnya
            history.append({"role": "assistant", "content": response_text})
            
            print(f"\n🤖 Assistant:\n{response_text}\n")
            print("-" * 50)
            
        except Exception as e:
            print(f"\n❌ Terjadi kesalahan saat mengirim pesan: {e}\n")

if __name__ == "__main__":
    start_chat()