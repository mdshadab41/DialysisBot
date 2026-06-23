"""
DialysisBot - Streamlit Web Application
Minimal modern UI with gradient design
"""

import streamlit as st # type: ignore
from chat import ChatBot
import config
from datetime import datetime
from pdf_manager import save_uploaded_pdf, list_all_pdfs, delete_pdf, rebuild_vector_database




# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="DialysisBot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ── CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }

/* ── Header ── */
.app-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.app-title {
    font-size: 2.8rem;
    font-weight: 600;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem;
}
.app-subtitle {
    font-size: 0.95rem;
    color: rgba(255,255,255,0.45);
    font-weight: 300;
    letter-spacing: 0.5px;
}

/* ── Disclaimer ── */
.disclaimer {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    font-size: 0.82rem;
    color: rgba(255,255,255,0.6);
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

/* ── Chat messages ── */
.msg-user {
    background: linear-gradient(135deg, rgba(167,139,250,0.15), rgba(96,165,250,0.15));
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 14px 14px 4px 14px;
    padding: 0.9rem 1.2rem;
    margin: 0.6rem 0 0.6rem 3rem;
    color: rgba(255,255,255,0.9);
    font-size: 0.92rem;
    line-height: 1.6;
}
.msg-bot {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px 14px 14px 4px;
    padding: 0.9rem 1.2rem;
    margin: 0.6rem 3rem 0.6rem 0;
    color: rgba(255,255,255,0.88);
    font-size: 0.92rem;
    line-height: 1.6;
}
.msg-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
    opacity: 0.5;
}

/* ── Confidence badge ── */
.conf-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.6rem;
}
.conf-high   { background: rgba(52,211,153,0.15); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.conf-medium { background: rgba(251,191,36,0.15);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
.conf-low    { background: rgba(239,68,68,0.15);   color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03);
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.75) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, rgba(167,139,250,0.2), rgba(96,165,250,0.2));
    border: 1px solid rgba(167,139,250,0.35);
    color: rgba(255,255,255,0.85) !important;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 400;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(167,139,250,0.35), rgba(96,165,250,0.35));
    border-color: rgba(167,139,250,0.6);
    transform: translateY(-1px);
}

/* ── Chat input ── */
.stChatInput > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
}
.stChatInput input {
    color: white !important;
    font-size: 0.92rem !important;
}

/* ── Metrics ── */
[data-testid="stMetricValue"] {
    color: #a78bfa !important;
    font-size: 1.6rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.4) !important;
    font-size: 0.75rem !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    color: rgba(255,255,255,0.55) !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── Select/Slider ── */
.stSlider > div > div { background: rgba(167,139,250,0.3) !important; }
.stSelectbox > div > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
}

/* ── Comparison columns ── */
.comp-rag {
    background: rgba(52,211,153,0.06);
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: rgba(255,255,255,0.85);
    font-size: 0.88rem;
    line-height: 1.6;
}
.comp-nrag {
    background: rgba(251,191,36,0.06);
    border: 1px solid rgba(251,191,36,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: rgba(255,255,255,0.85);
    font-size: 0.88rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ── Init session state ──────────────────────────────────────────────
if 'chatbot' not in st.session_state:
    with st.spinner('Initializing DialysisBot...'):
        st.session_state.chatbot = ChatBot()
        st.session_state.messages = []
        st.session_state.show_sources = True

# ── Header ─────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-title">🏥 DialysisBot</div>
    <div class="app-subtitle">AI · RAG · Clinical Knowledge Base</div>
</div>
""", unsafe_allow_html=True)

# ── Disclaimer ─────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
⚠️ For educational purposes only — not a substitute for professional medical advice.
Always consult your healthcare provider.
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    st.session_state.show_sources = st.checkbox(
        "Show sources", value=True
    )
    comparison_mode = st.checkbox(
        "Comparison mode", value=False,
        help="RAG vs Non-RAG side by side"
    )
    top_k = st.slider(
        "Sources to retrieve", 1, 10, config.TOP_K
    )

    st.divider()

    st.markdown("### 📊 Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("PDFs", "7")
    with col2:
        st.metric("Chunks", "300")
    st.metric("Messages", len(st.session_state.messages))

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chatbot.chat_history = []
        st.rerun()

    if st.button("💾 Export chat", use_container_width=True):
        if st.session_state.messages:
            export_text = f"DialysisBot Chat — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*60}\n\n"
            for msg in st.session_state.messages:
                if msg['role'] == 'user':
                    export_text += f"\nYOU:\n{msg['content']}\n"
                elif msg['role'] == 'assistant':
                    export_text += f"\nDIALYSISBOT:\n{msg['content']}\n"
                export_text += "\n" + "-"*60 + "\n"
            st.download_button(
                "📥 Download",
                data=export_text,
                file_name=f"dialysisbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("No messages yet")

    st.divider()

    st.markdown("### 💡 Try asking")
    samples = [
        "What foods should I avoid?",
        "How does hemodialysis work?",
        "What is peritoneal dialysis?",
        "Emergency dialysis procedures?",
        "Potassium levels in dialysis?"
    ]
    for q in samples:
        if st.button(q, use_container_width=True, key=f"s_{q}"):
            st.session_state.sample_question = q

    st.divider()

   with st.expander("📁 Manage PDFs"):
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=['pdf']
    )
    
    category = "uploaded"
    
    if uploaded_file:
        if st.button("📤 Upload PDF", use_container_width=True):
            with st.spinner('Uploading...'):
                result = save_uploaded_pdf(uploaded_file, category)
                if result['success']:
                    st.success(result['message'])
                    st.info("Click Rebuild Database to use this PDF")
                else:
                    st.error(result['message'])

    st.markdown("**Current PDFs**")
    pdfs = list_all_pdfs()
    if pdfs:
        for pdf in pdfs:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.caption(f"📄 {pdf['name']}")
            with c2:
                if st.button("🗑️", key=f"d_{pdf['path']}"):
                    result = delete_pdf(pdf['path'])
                    if result['success']:
                        st.success(result['message'])
                        st.rerun()
    else:
        st.info("No PDFs found")

    if st.button("🔄 Rebuild database", 
                 type="primary", 
                 use_container_width=True):
        with st.spinner('Rebuilding...'):
            result = rebuild_vector_database()
            if result['success']:
                st.success(result['message'])
                st.session_state.chatbot = ChatBot()
                st.rerun()
            else:
                st.error(result['message'])

# ── Chat history ───────────────────────────────────────────────────
for message in st.session_state.messages:

    if message['role'] == 'user':
        st.markdown(f"""
        <div class="msg-user">
            <div class="msg-label">You</div>
            {message['content']}
        </div>
        """, unsafe_allow_html=True)

    elif message['role'] == 'comparison':
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ With RAG**")
            st.markdown(f'<div class="comp-rag">{message["rag"]["answer"]}</div>',
                       unsafe_allow_html=True)
            conf = message['rag']['confidence']
            level_class = 'conf-high' if conf['score'] >= 80 else 'conf-medium' if conf['score'] >= 60 else 'conf-low'
            st.markdown(f'<span class="conf-badge {level_class}">Confidence {conf["score"]}%</span>',
                       unsafe_allow_html=True)
        with col2:
            st.markdown("**⚠️ Without RAG**")
            st.markdown(f'<div class="comp-nrag">{message["non_rag"]["answer"]}</div>',
                       unsafe_allow_html=True)
            st.markdown('<span class="conf-badge conf-low">No retrieval</span>',
                       unsafe_allow_html=True)
        st.markdown("---")

    else:
        # Bot message
        st.markdown(f"""
        <div class="msg-bot">
            <div class="msg-label">DialysisBot</div>
            {message['content']}
        </div>
        """, unsafe_allow_html=True)

        # Confidence badge
        if 'confidence' in message and message['confidence']:
            conf = message['confidence']
            level_class = 'conf-high' if conf['score'] >= 80 else 'conf-medium' if conf['score'] >= 60 else 'conf-low'
            st.markdown(
                f'<span class="conf-badge {level_class}">🎯 {conf["score"]}% confidence · {conf["level"]}</span>',
                unsafe_allow_html=True
            )

        # Sources
        if st.session_state.show_sources and message.get('sources'):
            with st.expander(f"📚 {len(message['sources'])} sources"):
                for i, src in enumerate(message['sources'], 1):
                    st.markdown(f"""
                    **{i}.** `{src['category']}/{src['filename']}`
                    · similarity `{src['similarity']:.3f}`
                    > {src['preview']}
                    """)

# ── Chat input ─────────────────────────────────────────────────────
if 'sample_question' in st.session_state:
    user_input = st.session_state.sample_question
    del st.session_state.sample_question
else:
    user_input = st.chat_input("Ask about dialysis...")

if user_input:
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input
    })

    st.markdown(f"""
    <div class="msg-user">
        <div class="msg-label">You</div>
        {user_input}
    </div>
    """, unsafe_allow_html=True)

    if comparison_mode:
        from comparison import Comparator
        with st.spinner('Comparing responses...'):
            if 'comparator' not in st.session_state:
                st.session_state.comparator = Comparator()
            config.TOP_K = top_k
            result = st.session_state.comparator.compare(user_input)

        st.session_state.messages.append({
            'role': 'comparison',
            'rag': result['rag'],
            'non_rag': result['non_rag']
        })

    else:
        with st.spinner('Thinking...'):
            config.TOP_K = top_k
            response = st.session_state.chatbot.chat(
                user_input,
                show_sources=st.session_state.show_sources
            )

        st.session_state.messages.append({
            'role': 'assistant',
            'content': response['answer'],
            'sources': response.get('sources', []),
            'confidence': response.get('confidence', {})
        })

    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; color:rgba(255,255,255,0.2);
            font-size:0.75rem; margin-top:3rem; letter-spacing:0.5px;'>
    DialysisBot v2.0 &nbsp;·&nbsp; RAG + Groq Llama 3.1 &nbsp;·&nbsp; ChromaDB
</div>
""", unsafe_allow_html=True)