import streamlit as st
import os
from groq import Groq
from datetime import datetime
from market_data import get_crypto_price, get_trending_coins, get_coin_list, get_coin_ohlc, get_coin_market_chart
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================
# KONFIGURASI PAGE
# ============================================
st.set_page_config(
    page_title="Chatbot AI Kageyoru",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - GLASSMORPHISM + GRADIENT
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #ffffff !important;
}

.stButton > button {
    background: rgba(99, 102, 241, 0.3) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(99, 102, 241, 0.4) !important;
    border-radius: 12px;
    color: #ffffff !important;
    font-weight: 500;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: rgba(99, 102, 241, 0.5) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

.stSelectbox > div > div, .stTextInput > div > div, .stNumberInput > div > div {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px;
    color: #ffffff !important;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.5);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.8);
}

div[data-testid="stHorizontalBlock"] button {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    height: auto !important;
    color: #e0e0e0 !important;
    font-size: 0.9rem !important;
    line-height: 1.4 !important;
    white-space: normal !important;
    text-align: left !important;
}

div[data-testid="stHorizontalBlock"] button:hover {
    background: rgba(99, 102, 241, 0.2) !important;
    border-color: rgba(99, 102, 241, 0.5) !important;
    color: #ffffff !important;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    background: rgba(255, 255, 255, 0.1) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 20px 20px 4px 20px;
    padding: 16px;
    color: #ffffff;
}

[data-testid="stChatMessage"]:nth-child(even) [data-testid="stChatMessageContent"] {
    background: rgba(99, 102, 241, 0.2) !important;
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 20px 20px 20px 4px;
}

[data-testid="stChatInput"] {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 16px;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# INISIALISASI GROQ CLIENT
# ============================================
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    st.error("⚠️ GROQ_API_KEY tidak ditemukan di environment variables!")
    st.stop()

# ============================================
# PERSONA SYSTEM PROMPT
# ============================================
PERSONAS = {
    "📈 Analis Market Pro": """Kamu adalah analis market profesional dengan spesialisasi crypto dan forex. 
Gunakan bahasa Indonesia santai (aku/kamu). 

ATURAN WAJIB:
1. SELALU ingatkan bahwa ini BUKAN financial advice
2. Jelaskan istilah teknikal dengan analogi simpel:
   - RSI = "kelelahan harga" (0-30: oversold/lelah jual, 70-100: overbought/lelah beli)
   - MACD = "persimpangan jalan" (golden cross = jalan lurus, death cross = belok bahaya)
   - Support = "lantai" harga, Resistance = "atap" harga
   - Volume = "semangat pasar" (volume tinggi = banyak yang ikutan)
3. Sebutkan timeframe analisis (1H, 4H, 1D)
4. Kasih 2 skenario: bullish case & bearish case
5. Sebutkan level support & resistance kunci
6. Jangan overconfident — market bisa berubah kapan aja

FORMAT JAWABAN:
📊 Asset: [nama]
⏰ Timeframe: [timeframe]
📈 Analisis Teknikal: [penjelasan simpel]
🎯 Level Kunci: Support $X | Resistance $Y
🐂 Bullish Case: [skenario naik + trigger]
🐻 Bearish Case: [skenario turun + trigger]
⚠️ Disclaimer: Bukan saran finansial. DYOR!""",
    
    "🧑‍💻 Programmer": "Kamu adalah programmer senior yang ramah. Jelaskan konsep coding dengan analogi sederhana. Gunakan bahasa Indonesia santai (aku/kamu). Hindari jargon berlebihan.",
    
    "🎬 Kreator Konten": "Kamu adalah kreator konten kreatif. Berikan ide konten, script, atau tips viral dengan gaya santai dan engaging. Bahasa Indonesia gaul tapi tetap sopan.",
    
    "🤙 Teman Ngobrol": "Kamu adalah teman ngobrol santai. Jawab dengan gaya conversational, pakai bahasa Indonesia sehari-hari, dan sesekali kasih emoji. Jangan terlalu formal."
}

# ============================================
# MODEL OPTIONS
# ============================================
MODELS = {
    "⚡ Llama 3.1 8B (Cepat)": "llama-3.1-8b-instant",
    "🧠 Llama 3.3 70B (Pintar)": "llama-3.3-70b-versatile",
    "🔥 Mixtral 8x7B": "mixtral-8x7b-32768",
    "💎 Gemma 2 9B": "gemma2-9b-it"
}

# ============================================
# FUNGSI CHART
# ============================================

def create_candlestick_chart(df, coin_name="Bitcoin"):
    """Buat chart candlestick interaktif pakai Plotly"""
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{coin_name} Price', 'Volume')
    )
    
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC',
            increasing_line_color='#22c55e',
            decreasing_line_color='#ef4444',
            increasing_fillcolor='#22c55e',
            decreasing_fillcolor='#ef4444'
        ),
        row=1, col=1
    )
    
    df['volume'] = (df['high'] - df['low']) * 1000000
    colors = ['#22c55e' if row['close'] >= row['open'] else '#ef4444' 
              for _, row in df.iterrows()]
    
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.3
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,15,30,0.5)',
        font=dict(color='white', family='Inter'),
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False,
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=False, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    
    return fig

def create_price_chart(df, coin_name="Bitcoin"):
    """Buat line chart harga simpel"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            mode='lines',
            name='Price',
            line=dict(color='#818cf8', width=2),
            fill='tozeroy',
            fillcolor='rgba(129,140,248,0.1)'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            mode='lines',
            name='Price',
            line=dict(color='#c084fc', width=3),
            hoverinfo='skip'
        )
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15,15,30,0.5)',
        font=dict(color='white', family='Inter'),
        height=300,
        margin=dict(l=50, r=50, t=30, b=30),
        showlegend=False,
        xaxis_showgrid=False,
        yaxis_showgrid=True,
        yaxis_gridcolor='rgba(255,255,255,0.05)'
    )
    
    return fig

# ============================================
# SESSION STATE
# ============================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = "📈 Analis Market Pro"

if "selected_model" not in st.session_state:
    st.session_state.selected_model = "⚡ Llama 3.1 8B (Cepat)"

if "market_data" not in st.session_state:
    st.session_state.market_data = None

if "ohlc_data" not in st.session_state:
    st.session_state.ohlc_data = None

if "chart_data" not in st.session_state:
    st.session_state.chart_data = None

# ============================================
# SIDEBAR - TAB PENGATURAN & MARKET
# ============================================
tab1, tab2 = st.sidebar.tabs(["⚙️ Pengaturan", "📊 Market"])

with tab1:
    st.markdown("### ⚙️ Pengaturan")
    
    persona = st.selectbox(
        "🎭 Persona AI",
        options=list(PERSONAS.keys()),
        index=list(PERSONAS.keys()).index(st.session_state.selected_persona)
    )
    st.session_state.selected_persona = persona
    st.caption(f"*{persona}* aktif")
    
    st.divider()
    
    model = st.selectbox(
        "🔧 Model AI",
        options=list(MODELS.keys()),
        index=list(MODELS.keys()).index(st.session_state.selected_model)
    )
    st.session_state.selected_model = model
    
    st.divider()
    
    if st.session_state.messages:
        chat_history = ""
        for msg in st.session_state.messages:
            role = "User" if msg["role"] == "user" else "AI"
            chat_history += f"[{role}]\n{msg['content']}\n\n"
        
        st.download_button(
            label="📝 Export Chat",
            data=chat_history,
            file_name=f"chat_kageyoru_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    if st.button("🗑️ Hapus Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.market_data = None
        st.session_state.ohlc_data = None
        st.session_state.chart_data = None
        st.rerun()

with tab2:
    st.markdown("### 📈 Data Real-Time")
    st.caption("Data langsung dari CoinGecko — gratis & real-time")
    
    coin_list = get_coin_list()
    coin_names = list(coin_list.keys())
    
    selected_name = st.selectbox("💱 Pilih Crypto", coin_names, index=0)
    selected_id = coin_list[selected_name]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Harga + Chart", use_container_width=True):
            with st.spinner("Mengambil data dari CoinGecko..."):
                data = get_crypto_price(selected_id)
                ohlc_data = get_coin_ohlc(selected_id, days=7)
                chart_data = get_coin_market_chart(selected_id, days=7)
                
                if "error" not in data:
                    st.session_state.market_data = data
                    st.session_state.ohlc_data = ohlc_data if "error" not in ohlc_data else None
                    st.session_state.chart_data = chart_data if "error" not in chart_data else None
                    
                    change_emoji = "🟢" if data['change_24h'] >= 0 else "🔴"
                    change_sign = "+" if data['change_24h'] >= 0 else ""
                    
                    market_msg = f"""📊 Data Real-Time {data['symbol'].upper()}/USD (CoinGecko):

💰 Harga: ${data['price']:,.2f}
{change_emoji} Change 24h: {change_sign}{data['change_24h']:.2f}%
📦 Volume 24h: ${data['volume_24h']:,.0f}
🏦 Market Cap: ${data['market_cap']:,.0f}
⏰ Last Updated: {data['last_updated']}

Berdasarkan data di atas, analisis teknikal {data['symbol'].upper()} gimana?"""
                    
                    st.session_state.messages.append({"role": "user", "content": market_msg})
                    st.rerun()
                else:
                    st.error(f"❌ Gagal ambil data: {data['error']}")
    
    with col2:
        if st.button("🔥 Trending Coins", use_container_width=True):
            with st.spinner("Mengambil trending..."):
                trending = get_trending_coins()
                if "error" not in trending:
                    trend_msg = "🔥 Crypto yang lagi trending hari ini:\n\n"
                    for i, coin in enumerate(trending, 1):
                        trend_msg += f"{i}. **{coin['name']}** ({coin['symbol']}) — Rank #{coin['market_cap_rank']}\n"
                    trend_msg += "\nKasih analisis singkat untuk 3 coin teratas dong!"
                    
                    st.session_state.messages.append({"role": "user", "content": trend_msg})
                    st.rerun()
                else:
                    st.error(f"❌ Error: {trending['error']}")
    
    # Tampilkan data terakhir + CHART
    if st.session_state.market_data:
        d = st.session_state.market_data
        change_sign = "+" if d['change_24h'] >= 0 else ""
        
        st.markdown("---")
        st.markdown(f"**{d['symbol'].upper()}/USD**")
        
        col_price, col_change = st.columns(2)
        with col_price:
            st.metric("Harga", f"${d['price']:,.2f}")
        with col_change:
            st.metric("Change 24h", f"{change_sign}{d['change_24h']:.2f}%")
        
        col_vol, col_cap = st.columns(2)
        with col_vol:
            st.metric("Volume 24h", f"${d['volume_24h']:,.0f}")
        with col_cap:
            st.metric("Market Cap", f"${d['market_cap']:,.0f}")
        
        st.caption(f"📡 Source: {d['source']} | ⏰ {d['last_updated'][:19]}")
        
        # CHART CANDLESTICK
        if st.session_state.ohlc_data is not None:
            st.markdown("---")
            st.markdown("### 📈 Chart 7 Hari")
            
            fig = create_candlestick_chart(
                st.session_state.ohlc_data, 
                coin_name=selected_name
            )
            st.plotly_chart(fig, use_container_width=True, key="candlestick_chart")
            
            st.caption("💡 Hover/scroll untuk zoom. Hijau = naik, Merah = turun.")
        
        # LINE CHART (fallback)
        elif st.session_state.chart_data is not None:
            st.markdown("---")
            st.markdown("### 📈 Price Chart 7 Hari")
            
            fig = create_price_chart(
                st.session_state.chart_data,
                coin_name=selected_name
            )
            st.plotly_chart(fig, use_container_width=True, key="price_chart")
    
    # Input manual fallback
    with st.expander("📝 Input Data Manual (dari TradingView)"):
        st.caption("Kalau CoinGecko error atau mau analisis forex/stock")
        
        col1, col2 = st.columns(2)
        with col1:
            manual_asset = st.text_input("Asset", value="BTC/USDT", key="manual_asset")
        with col2:
            manual_tf = st.selectbox(
                "Timeframe",
                ["1m", "5m", "15m", "1H", "4H", "1D", "1W"],
                index=3,
                key="manual_tf"
            )
        
        manual_price = st.number_input("Harga Sekarang ($)", value=0.0, step=0.01, key="manual_price")
        
        with st.expander("📉 Indikator Teknikal"):
            col_rsi, col_macd = st.columns(2)
            with col_rsi:
                manual_rsi = st.number_input("RSI", min_value=0, max_value=100, value=50, key="manual_rsi")
            with col_macd:
                manual_macd = st.number_input("MACD", value=0.0, step=0.01, key="manual_macd")
            
            col_sup, col_res = st.columns(2)
            with col_sup:
                manual_sup = st.number_input("Support ($)", value=0.0, step=0.01, key="manual_sup")
            with col_res:
                manual_res = st.number_input("Resistance ($)", value=0.0, step=0.01, key="manual_res")
        
        if st.button("🚀 Analisis Manual", use_container_width=True, key="manual_btn"):
            manual_context = f"""Data Market {manual_asset} ({manual_tf}):
💰 Harga: ${manual_price:,.2f}"""
            if manual_rsi != 50:
                manual_context += f"\n📊 RSI: {manual_rsi}"
            if manual_macd != 0:
                manual_context += f"\n📈 MACD: {manual_macd}"
            if manual_sup != 0:
                manual_context += f"\n🟢 Support: ${manual_sup:,.2f}"
            if manual_res != 0:
                manual_context += f"\n🔴 Resistance: ${manual_res:,.2f}"
            
            manual_context += f"\n\nBerdasarkan data di atas, analisis teknikal {manual_asset} gimana?"
            
            st.session_state.messages.append({"role": "user", "content": manual_context})
            st.rerun()

# ============================================
# HEADER
# ============================================
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="font-size: 2.5rem; font-weight: 700; background: linear-gradient(90deg, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🤖 Chatbot AI Kageyoru
    </h1>
    <p style="color: rgba(255,255,255,0.6); font-size: 1rem; margin-top: -10px;">
        Asisten AI untuk analisis market & berbagai kebutuhanmu
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# QUICK PROMPTS
# ============================================
if not st.session_state.messages:
    st.markdown("### 🎯 Mulai dengan pertanyaan ini:")
    
    quick_prompts = [
        "Analisis BTC minggu ini, bullish or bearish?",
        "Jelasin RSI itu apa sih? Gimana cara bacanya?",
        "Kasih ide konten TikTok tentang teknologi AI",
        "Bantu aku debug Python: list index out of range"
    ]
    
    cols = st.columns(2)
    for idx, prompt in enumerate(quick_prompts):
        with cols[idx % 2]:
            if st.button(prompt, key=f"quick_{idx}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                try:
                    system_msg = PERSONAS[st.session_state.selected_persona]
                    groq_messages = [{"role": "system", "content": system_msg}]
                    for m in st.session_state.messages:
                        groq_messages.append({"role": m["role"], "content": m["content"]})
                    
                    response = client.chat.completions.create(
                        model=MODELS[st.session_state.selected_model],
                        messages=groq_messages,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    
                    ai_response = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"Waduh, error: {str(e)}"})
                
                st.rerun()

# ============================================
# TAMPILKAN CHAT HISTORY
# ============================================
for message in st.session_state.messages:
    avatar = "🧑" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ============================================
# INPUT CHAT
# ============================================
if prompt := st.chat_input("Ketik pesanmu di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            system_msg = PERSONAS[st.session_state.selected_persona]
            groq_messages = [{"role": "system", "content": system_msg}]
            
            for m in st.session_state.messages:
                groq_messages.append({"role": m["role"], "content": m["content"]})
            
            stream = client.chat.completions.create(
                model=MODELS[st.session_state.selected_model],
                messages=groq_messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_msg = f"Waduh, terjadi kesalahan: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})