import streamlit as st
import os
import requests
from groq import Groq
from datetime import datetime
from market_data import get_crypto_price, get_trending_coins, get_coin_list, get_coin_ohlc, get_coin_market_chart
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================
# KONFIGURASI PAGE
# ============================================
st.set_page_config(
    page_title="KAGEYORU TERMINAL",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

:root {
    --terminal-bg: #08090c;
    --terminal-panel: #0d0f14;
    --terminal-border: rgba(240, 180, 41, 0.15);
    --amber: #f0b429;
    --amber-dim: rgba(240, 180, 41, 0.5);
    --amber-glow: rgba(240, 180, 41, 0.12);
    --up: #22c55e;
    --down: #ef4444;
    --text-dim: rgba(255,255,255,0.55);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Numbers, labels, headers get a mono terminal feel */
h1, h2, h3, .stMetric, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    font-family: 'IBM Plex Mono', monospace !important;
}

.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(240,180,41,0.06), transparent),
        linear-gradient(180deg, #08090c 0%, #0a0b0f 100%);
}

/* subtle terminal grid overlay */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(240,180,41,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(240,180,41,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--terminal-panel) !important;
    border-right: 1px solid var(--terminal-border) !important;
}

h1, h2, h3, h4, h5, h6, p, label, span {
    color: #f4f4f2 !important;
    letter-spacing: 0.2px;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-dim) !important;
}

.stButton > button {
    background: rgba(240, 180, 41, 0.06) !important;
    border: 1px solid var(--amber-dim) !important;
    border-radius: 4px;
    color: #f0b429 !important;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: var(--amber-glow) !important;
    border-color: var(--amber) !important;
    color: #ffd166 !important;
    box-shadow: 0 0 16px rgba(240,180,41,0.25);
}

.stSelectbox > div > div, .stTextInput > div > div, .stNumberInput > div > div {
    background: var(--terminal-panel) !important;
    border: 1px solid var(--terminal-border) !important;
    border-radius: 4px;
    color: #f4f4f2 !important;
    font-family: 'IBM Plex Mono', monospace;
}

[data-testid="stMetric"] {
    background: var(--terminal-panel);
    border: 1px solid var(--terminal-border);
    border-radius: 4px;
    padding: 12px 16px;
}

hr, [data-testid="stDivider"] {
    border-color: var(--terminal-border) !important;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--terminal-bg);
}

::-webkit-scrollbar-thumb {
    background: var(--amber-dim);
    border-radius: 4px;
}

[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
    background: var(--terminal-panel) !important;
    border: 1px solid var(--terminal-border);
    border-radius: 6px;
    padding: 16px;
    color: #f4f4f2;
}

[data-testid="stChatMessage"]:nth-child(even) [data-testid="stChatMessageContent"] {
    background: rgba(240, 180, 41, 0.05) !important;
    border: 1px solid var(--amber-dim);
    border-left: 2px solid var(--amber);
}

[data-testid="stChatInput"] {
    background: var(--terminal-panel) !important;
    border: 1px solid var(--terminal-border) !important;
    border-radius: 6px;
    color: #f4f4f2;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--amber) !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# INISIALISASI GROQ CLIENT
# ============================================
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    st.error("⚠️ GROQ_API_KEY tidak ditemukan!")
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
   - RSI = "kelelahan harga" (0-30: oversold, 70-100: overbought)
   - MACD = "persimpangan jalan" (golden cross/death cross)
   - Support = "lantai" harga, Resistance = "atap" harga
   - Volume = "semangat pasar"
3. Kalau ada "Konteks timeframe" di pesan user, WAJIB sesuaikan gaya analisis sama timeframe itu (scalping = fokus pergerakan cepat, swing = tren menengah, long-term = tren besar). Kalau nggak ada, sebutkan timeframe analisis (1H, 4H, 1D)
4. Kasih 2 skenario: bullish case & bearish case
5. Sebutkan level support & resistance kunci
6. Jangan overconfident

FORMAT JAWABAN:
📊 Asset: [nama]
⏰ Timeframe: [timeframe]
📈 Analisis Teknikal: [penjelasan simpel]
🎯 Level Kunci: Support $X | Resistance $Y
🐂 Bullish Case: [skenario naik + trigger]
🐻 Bearish Case: [skenario turun + trigger]
⚠️ Disclaimer: Bukan saran finansial. DYOR!"""
}

MODELS = {
    "⚡ Llama 3.1 8B (Cepat)": "llama-3.1-8b-instant",
    "🧠 Llama 3.3 70B (Pintar)": "llama-3.3-70b-versatile",
    "🔥 Mixtral 8x7B": "mixtral-8x7b-32768",
    "💎 Gemma 2 9B": "gemma2-9b-it"
}

TIMEFRAMES = {
    "⚡ Scalping (15m-1H)": {
        "days": 1,
        "context": "Trader lagi cari peluang SCALPING/intraday cepat (hitungan menit-jam). Fokus ke pergerakan harga jangka pendek, volatilitas, dan level entry/exit yang tajam. Jangan kasih analisis makro jangka panjang."
    },
    "📊 Swing (4H-1D)": {
        "days": 7,
        "context": "Trader lagi cari peluang SWING trading (posisi ditahan beberapa hari). Fokus ke tren jangka menengah, level support/resistance mingguan, dan momentum."
    },
    "📈 Long-term (1W+)": {
        "days": 90,
        "context": "Trader lagi mikir posisi JANGKA PANJANG (mingguan-bulanan). Fokus ke tren besar, siklus market, dan level kunci jangka panjang. Nggak perlu bahas noise pergerakan harian."
    }
}

# ============================================
# FUNGSI CHART
# ============================================
def create_candlestick_chart(df, coin_name="Bitcoin"):
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
# LIVE PRICE TICKER
# ============================================
@st.cache_data(ttl=30, show_spinner=False)
def get_ticker_snapshot(coin_id):
    """Ambil snapshot harga, di-cache 30 detik biar nggak spam API tiap rerun."""
    return get_crypto_price(coin_id)

def render_price_ticker(coin_id, coin_name):
    data = get_ticker_snapshot(coin_id)

    if not data or "error" in data:
        st.markdown("""
        <div style="
            background: var(--terminal-panel);
            border: 1px solid var(--terminal-border);
            border-radius: 6px;
            padding: 14px 24px;
            margin: 0 0 24px 0;
            font-family: 'IBM Plex Mono', monospace;
            color: rgba(255,255,255,0.45);
            font-size: 0.85rem;
            text-align: center;
        ">
            ⚠️ Data harga belum bisa dimuat. Klik "Refresh Harga" di sidebar.
        </div>
        """, unsafe_allow_html=True)
        return

    change = data['change_24h']
    color = "#22c55e" if change >= 0 else "#ef4444"
    arrow = "▲" if change >= 0 else "▼"
    sign = "+" if change >= 0 else ""

    st.markdown(f"""
    <div style="
        background: #0d0f14;
        border: 1px solid rgba(240, 180, 41, 0.15);
        border-radius: 6px;
        padding: 14px 24px;
        margin: 0 0 24px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        position: relative;
        z-index: 1;
    ">
        <div style="display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap;">
            <span style="font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: #f0b429; letter-spacing: 1px;">
                {data['symbol'].upper()}/USD
            </span>
            <span style="font-family: 'IBM Plex Mono', monospace; font-size: 1.6rem; font-weight: 700; color: #f4f4f2;">
                ${data['price']:,.2f}
            </span>
            <span style="font-family: 'IBM Plex Mono', monospace; font-size: 1rem; font-weight: 600; color: {color};">
                {arrow} {sign}{change:.2f}%
            </span>
        </div>
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; color: rgba(255,255,255,0.45); text-align: right; line-height: 1.5;">
            VOL 24H: ${data['volume_24h']:,.0f}<br>
            MCAP: ${data['market_cap']:,.0f}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FEAR & GREED INDEX + FUNDING RATE
# ============================================
@st.cache_data(ttl=300, show_spinner=False)
def get_fear_greed_index():
    """Sentimen market crypto secara keseluruhan (alternative.me), update harian jadi cache 5 menit cukup."""
    try:
        response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        data = response.json()
        latest = data["data"][0]
        return {
            "value": int(latest["value"]),
            "classification": latest["value_classification"]
        }
    except Exception:
        return None

@st.cache_data(ttl=60, show_spinner=False)
def get_funding_rate(futures_symbol):
    """Funding rate futures dari Binance, contoh symbol: BTCUSDT."""
    try:
        response = requests.get(
            "https://fapi.binance.com/fapi/v1/premiumIndex",
            params={"symbol": futures_symbol},
            timeout=5
        )
        data = response.json()
        if "lastFundingRate" in data:
            return float(data["lastFundingRate"]) * 100
        return None
    except Exception:
        return None

def render_sentiment_row(coin_symbol):
    fg = get_fear_greed_index()
    futures_symbol = f"{coin_symbol.upper()}USDT"
    funding = get_funding_rate(futures_symbol)

    col1, col2 = st.columns(2)

    with col1:
        if fg:
            fg_labels_id = {
                "Extreme Fear": "Ketakutan Ekstrem",
                "Fear": "Ketakutan",
                "Neutral": "Netral",
                "Greed": "Keserakahan",
                "Extreme Greed": "Keserakahan Ekstrem"
            }
            label_id = fg_labels_id.get(fg["classification"], fg["classification"])

            if fg["value"] <= 25:
                fg_color = "#ef4444"
            elif fg["value"] <= 45:
                fg_color = "#f97316"
            elif fg["value"] <= 55:
                fg_color = "#f0b429"
            elif fg["value"] <= 75:
                fg_color = "#84cc16"
            else:
                fg_color = "#22c55e"

            st.markdown(f"""
            <div style="
                background: #0d0f14;
                border: 1px solid rgba(240, 180, 41, 0.15);
                border-radius: 6px;
                padding: 14px 20px;
                margin: 0 0 24px 0;
                height: 88px;
            ">
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: rgba(255,255,255,0.45); letter-spacing: 1px; margin-bottom: 6px;">
                    😨 FEAR &amp; GREED INDEX
                </div>
                <div style="display: flex; align-items: baseline; gap: 10px;">
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 1.7rem; font-weight: 700; color: {fg_color};">{fg['value']}</span>
                    <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.9rem; font-weight: 600; color: {fg_color};">{label_id}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #0d0f14; border: 1px solid rgba(240, 180, 41, 0.15); border-radius: 6px; padding: 14px 20px; margin: 0 0 24px 0; height: 88px; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.45); font-family: 'IBM Plex Mono', monospace; font-size: 0.8rem;">
                ⚠️ Fear &amp; Greed Index nggak bisa dimuat
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if funding is not None:
            f_color = "#22c55e" if funding >= 0 else "#ef4444"
            f_note = "Long bayar Short (market cenderung greedy)" if funding >= 0 else "Short bayar Long (market cenderung takut)"

            st.markdown(f"""
            <div style="
                background: #0d0f14;
                border: 1px solid rgba(240, 180, 41, 0.15);
                border-radius: 6px;
                padding: 14px 20px;
                margin: 0 0 24px 0;
                height: 88px;
            ">
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; color: rgba(255,255,255,0.45); letter-spacing: 1px; margin-bottom: 6px;">
                    ⚖️ FUNDING RATE ({futures_symbol})
                </div>
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 1.7rem; font-weight: 700; color: {f_color};">
                    {funding:+.4f}%
                </div>
                <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; color: rgba(255,255,255,0.4); margin-top: 2px;">
                    {f_note}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #0d0f14; border: 1px solid rgba(240, 180, 41, 0.15); border-radius: 6px; padding: 14px 20px; margin: 0 0 24px 0; height: 88px; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.45); font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; text-align: center;">
                ⚠️ Funding rate {futures_symbol} nggak tersedia (mungkin belum listed di Binance Futures)
            </div>
            """, unsafe_allow_html=True)

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

if "selected_timeframe" not in st.session_state:
    st.session_state.selected_timeframe = "📊 Swing (4H-1D)"

# ============================================
# SIDEBAR
# ============================================
tab1, tab2 = st.sidebar.tabs(["⚙️ Pengaturan", "📊 Market"])

with tab1:
    st.markdown("### ⚙️ Pengaturan")

    st.session_state.selected_persona = "📈 Analis Market Pro"
    st.caption("🎭 Persona AI: **Analis Market Pro** (khusus analisis crypto)")

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
    st.caption("Data langsung dari CoinGecko")
    
    coin_list = get_coin_list()
    coin_names = list(coin_list.keys())
    
    selected_name = st.selectbox("💱 Pilih Crypto", coin_names, index=0)
    selected_id = coin_list[selected_name]

    timeframe = st.selectbox(
        "⏱️ Timeframe Trading",
        options=list(TIMEFRAMES.keys()),
        index=list(TIMEFRAMES.keys()).index(st.session_state.selected_timeframe)
    )
    st.session_state.selected_timeframe = timeframe
    tf_config = TIMEFRAMES[timeframe]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Harga", use_container_width=True):
            with st.spinner("Mengambil data..."):
                data = get_crypto_price(selected_id)
                ohlc_data = get_coin_ohlc(selected_id, days=tf_config["days"])
                chart_data = get_coin_market_chart(selected_id, days=tf_config["days"])
                
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

Konteks timeframe: {tf_config['context']}

Berdasarkan data di atas, analisis teknikal {data['symbol'].upper()} gimana untuk timeframe {timeframe}?"""
                    
                    st.session_state.messages.append({"role": "user", "content": market_msg})
                    st.rerun()
                else:
                    st.error(f"❌ Gagal: {data['error']}")
    
    with col2:
        if st.button("🔥 Trending", use_container_width=True):
            with st.spinner("Mengambil..."):
                trending = get_trending_coins()
                if "error" not in trending:
                    trend_msg = "🔥 Crypto trending hari ini:\n\n"
                    for i, coin in enumerate(trending, 1):
                        trend_msg += f"{i}. **{coin['name']}** ({coin['symbol']}) — Rank #{coin['market_cap_rank']}\n"
                    trend_msg += "\nKasih analisis singkat untuk 3 coin teratas dong!"
                    
                    st.session_state.messages.append({"role": "user", "content": trend_msg})
                    st.rerun()
                else:
                    st.error(f"❌ Error: {trending['error']}")
    
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
        
        st.caption(f"📡 Source: {d['source']} | ⏰ {d['last_updated'][:19]}")
    
    with st.expander("📝 Input Manual"):
        st.caption("Dari TradingView")
        
        col1, col2 = st.columns(2)
        with col1:
            manual_asset = st.text_input("Asset", value="BTC/USDT", key="manual_asset")
        with col2:
            manual_tf = st.selectbox("Timeframe", ["1m", "5m", "15m", "1H", "4H", "1D", "1W"], index=3, key="manual_tf")
        
        manual_price = st.number_input("Harga ($)", value=0.0, step=0.01, key="manual_price")
        
        with st.expander("📉 Indikator"):
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
        
        if st.button("🚀 Analisis", use_container_width=True, key="manual_btn"):
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
<div style="text-align: center; padding: 24px 0 12px 0; position: relative; z-index: 1;">
    <h1 style="font-family: 'IBM Plex Mono', monospace; font-size: 2.1rem; font-weight: 700; letter-spacing: 4px; color: #f0b429; margin-bottom: 4px;">
        📈 KAGEYORU TERMINAL
    </h1>
    <p style="color: rgba(255,255,255,0.45); font-size: 0.85rem; font-family: 'IBM Plex Mono', monospace; letter-spacing: 1px; text-transform: uppercase; margin-top: 0;">
        Personal Trading Intelligence · Bukan Financial Advice
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# LIVE PRICE TICKER (tampil di atas, ikut crypto yang dipilih di sidebar)
# ============================================
render_price_ticker(selected_id, selected_name)

# ============================================
# FEAR & GREED INDEX + FUNDING RATE (ikut crypto yang dipilih)
# ============================================
_ticker_snapshot = get_ticker_snapshot(selected_id)
if _ticker_snapshot and "error" not in _ticker_snapshot:
    render_sentiment_row(_ticker_snapshot["symbol"])

# ============================================
# QUICK PROMPTS
# ============================================
if not st.session_state.messages:
    st.markdown("### 🎯 Mulai dengan pertanyaan ini:")
    
    quick_prompts = [
        "Analisis BTC minggu ini, bullish or bearish?",
        "Jelasin RSI itu apa sih? Gimana cara bacanya?",
        "Cara set stop loss & take profit yang aman gimana?",
        "Kapan waktu terbaik entry saat market sideways?"
    ]
    
    cols = st.columns(2)
    for idx, prompt in enumerate(quick_prompts):
        with cols[idx % 2]:
            if st.button(prompt, key=f"quick_{idx}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

# ============================================
# TAMPILKAN CHAT HISTORY + CHART
# ============================================

# Cek apakah ada message baru dari user yang perlu AI response
needs_ai_response = False
if len(st.session_state.messages) > 0:
    last_msg = st.session_state.messages[-1]
    if last_msg["role"] == "user":
        needs_ai_response = True

# Tampilkan semua chat history (termasuk chart yang sudah ada)
for i, message in enumerate(st.session_state.messages):
    avatar = "🧑" if message["role"] == "user" else "🤖"
    
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
    
    # Tampilkan chart setelah AI response yang memiliki data chart
    # Kita cek apakah message AI ini adalah response terakhir dan kita punya chart data
    if message["role"] == "assistant" and i == len(st.session_state.messages) - 1 and not needs_ai_response:
        # Tampilkan chart di main area setelah AI response terakhir
        _tf_days = TIMEFRAMES[st.session_state.selected_timeframe]["days"]
        if st.session_state.ohlc_data is not None:
            st.markdown("---")
            st.markdown(f"### 📊 Chart {_tf_days} Hari ({st.session_state.selected_timeframe})")
            
            fig = create_candlestick_chart(
                st.session_state.ohlc_data, 
                coin_name=selected_name
            )
            st.plotly_chart(fig, use_container_width=True, key=f"chart_candle_main_{i}")
            st.caption("💡 Hover/scroll untuk zoom. Hijau = naik, Merah = turun.")
        
        elif st.session_state.chart_data is not None:
            st.markdown("---")
            st.markdown(f"### 📈 Price Chart {_tf_days} Hari ({st.session_state.selected_timeframe})")
            
            fig = create_price_chart(
                st.session_state.chart_data,
                coin_name=selected_name
            )
            st.plotly_chart(fig, use_container_width=True, key=f"chart_line_main_{i}")

# ============================================
# AI RESPONSE (streaming)
# ============================================
if needs_ai_response:
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
            
            # Simpan AI response
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Tampilkan chart setelah AI selesai (tapi di rerun berikutnya)
            # Chart akan otomatis muncul di loop di atas karena sekarang messages[-1] adalah assistant
            
            st.rerun()
            
        except Exception as e:
            error_msg = f"Waduh, terjadi kesalahan: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ============================================
# INPUT CHAT
# ============================================
if prompt := st.chat_input("Ketik pesanmu di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
