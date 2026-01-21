import streamlit as st
import time
import os
import random
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(
    page_title="阿美語 - 我的朋友", 
    page_icon="👫", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS 視覺設計 (溫暖友情風 🧡) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap');

    /* 全局背景：溫暖的米黃色 */
    .stApp { 
        background-color: #FFF8E1; 
        font-family: 'Noto Sans TC', sans-serif;
    }
    
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    
    /* 標題樣式 */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 900 !important;
        text-align: center;
        color: #FF6F00 !important;
        margin-bottom: 10px;
    }
    
    /* 副標題 */
    .sub-title {
        text-align: center;
        color: #8D6E63 !important;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 30px;
    }

    /* 按鈕：溫暖橘漸層 */
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        font-size: 18px;
        font-weight: 700;
        background: linear-gradient(90deg, #FF8F00 0%, #FF6F00 100%);
        color: #FFFFFF !important;
        border: none;
        padding: 12px 0px;
        box-shadow: 0px 4px 10px rgba(255, 111, 0, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 6px 15px rgba(255, 111, 0, 0.5);
    }
    
    /* 單字卡片 */
    .card {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 15px;
        border: 2px solid #FFE082; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    /* 句子卡片 */
    .sentence-box {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #FF8F00;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .amis-text {
        font-size: 20px;
        font-weight: 800;
        color: #E65100 !important;
        margin-bottom: 5px;
    }
    
    .zh-text {
        font-size: 15px;
        color: #795548 !important;
        font-weight: 500;
    }

    .emoji-icon { font-size: 40px; margin-bottom: 5px; }
    
    /* Tab 樣式 */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.6);
        border-radius: 10px;
        color: #5D4037 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF8F00 !important;
        color: #FFFFFF !important;
    }
    
    /* Radio 選項優化 */
    .stRadio label {
        background: white;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #FFE082;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 數據結構 ---

# 單字資料
VOCABULARY = [
    {"amis": "takaraw",   "zh": "高的",   "emoji": "🦒", "file": "v_takaraw"},
    {"amis": "poener",    "zh": "矮的",   "emoji": "🍄", "file": "v_poener"},
    {"amis": "maso^so",   "zh": "胖的",   "emoji": "🍔", "file": "v_masoso"},
    {"amis": "ma'okak",   "zh": "瘦的",   "emoji": "🦴", "file": "v_maokak"},
    {"amis": "malalok",   "zh": "勤勞",   "emoji": "🐝", "file": "v_malalok"},
    {"amis": "matoka",    "zh": "懶惰",   "emoji": "🦥", "file": "v_matoka"},
    {"amis": "kalamkam",  "zh": "勤快/快速", "emoji": "⚡", "file": "v_kalamkam"},
    {"amis": "mihinom",   "zh": "安慰",   "emoji": "🤗", "file": "v_mihinom"},
    {"amis": "maolah",    "zh": "喜歡",   "emoji": "💖", "file": "v_maolah"},
    {"amis": "tayal",     "zh": "工作",   "emoji": "💼", "file": "v_tayal"},
    {"amis": "singsi",    "zh": "老師",   "emoji": "👩‍🏫", "file": "v_singsi"},
    {"amis": "fana'",     "zh": "會/知道", "emoji": "💡", "file": "v_fana"},
]

# 句子資料
SENTENCES = [
    {"amis": "Takaraw ci Hana.", "zh": "Hana很高。", "file": "s_1"},
    {"amis": "Malalok ci Arik.", "zh": "Arik很勤勞。", "file": "s_2"},
    {"amis": "Mafana' a mihinom to faloco' no widang ci Nah.", "zh": "Nah很會安慰朋友的心。", "file": "s_3"},
    {"amis": "O malasingsiay ko tayal nangra.", "zh": "她們的工作都是族語老師。", "file": "s_4"},
    {"amis": "Maolah kako to widang ako.", "zh": "我很喜歡我的朋友。", "file": "s_5"},
]

# 測驗題庫：角色與特質配對
# 修正重點：更新了 Nah 的問句
QUIZ_CHARACTERS = [
    {"q": "Takaraw ci ima?", "zh_q": "誰很高？", "ans": "Hana", "options": ["Hana", "Arik", "Nah"]},
    {"q": "Malalok ci ima?", "zh_q": "誰很勤勞？", "ans": "Arik", "options": ["Arik", "Hana", "Nah"]},
    
    # 👇 這裡更新了問句 👇
    {"q": "Cima ko mafana'ay a mihinom to faloco' no widang?", "zh_q": "誰很會安慰朋友的心？", "ans": "Nah", "options": ["Nah", "Hana", "Arik"]},
    
    {"q": "O maan ko tayal nangra?", "zh_q": "她們的工作是什麼？", "ans": "Singsi", "options": ["Singsi", "Ising", "Kingcaco"]},
]

# --- 1.5 智慧語音核心 ---
def play_audio(text, filename_base=None):
    # 1. 優先播放真人錄音
    if filename_base:
        for ext in ['mp3', 'm4a']:
            path = f"audio/{filename_base}.{ext}"
            if os.path.exists(path):
                st.audio(path, format=f'audio/{ext}')
                return
    
    # 2. 備用 TTS
    try:
        tts = gTTS(text=text, lang='id') # 印尼語發音接近阿美語
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇")

# --- 2. 隨機出題邏輯 ---
def init_quiz():
    st.session_state.score = 0
    st.session_state.current_q = 0
    
    # Q1: 單字聽力
    q1_target = random.choice(VOCABULARY)
    others = [v for v in VOCABULARY if v['amis'] != q1_target['amis']]
    q1_options = random.sample(others, 2) + [q1_target]
    random.shuffle(q1_options)
    st.session_state.q1_data = {"target": q1_target, "options": q1_options}

    # Q2: 句子理解 (角色題)
    q2_data = random.choice(QUIZ_CHARACTERS)
    random.shuffle(q2_data['options'])
    st.session_state.q2_data = q2_data

    # Q3: 句子翻譯 (聽音檔選中文)
    q3_target = random.choice(SENTENCES)
    other_sentences = [s['zh'] for s in SENTENCES if s['zh'] != q3_target['zh']]
    q3_options = random.sample(other_sentences, 2) + [q3_target['zh']]
    random.shuffle(q3_options)
    st.session_state.q3_data = {"target": q3_target, "options": q3_options}

if 'q1_data' not in st.session_state:
    init_quiz()

# --- 3. 介面邏輯 ---

def show_learning_mode():
    st.markdown("<div class='sub-title'>— 認識朋友與特質 —</div>", unsafe_allow_html=True)
    
    # --- Part 1: 單字卡片 (先單字) ---
    st.markdown("### 📝 重點單字")
    
    cols = st.columns(3)
    for idx, item in enumerate(VOCABULARY):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card">
                <div class="emoji-icon">{item['emoji']}</div>
                <div class="amis-text" style="font-size:18px;">{item['amis']}</div>
                <div class="zh-text">{item['zh']}</div>
            </div>
            """, unsafe_allow_html=True)
            play_audio(item['amis'], filename_base=item['file'])
            
    st.markdown("---")

    # --- Part 2: 句子學習 (後句子) ---
    st.markdown("### 📖 課文句子")
    for s in SENTENCES:
        st.markdown(f"""
        <div class="sentence-box">
            <div class="amis-text">{s['amis']}</div>
            <div class="zh-text">{s['zh']}</div>
        </div>
        """, unsafe_allow_html=True)
        play_audio(s['amis'], filename_base=s['file'])

def show_quiz_mode():
    st.markdown("<h3 style='text-align: center; color: #E65100; margin-bottom: 20px;'>🏆 友情大考驗</h3>", unsafe_allow_html=True)
    
    st.progress(st.session_state.current_q / 3)
    st.write("") 

    # Q1: 單字聽力
    if st.session_state.current_q == 0:
        data = st.session_state.q1_data
        target = data['target']
        st.markdown("**第 1 關：聽聽看，這是什麼意思？**")
        play_audio(target['amis'], filename_base=target['file'])
        
        cols = st.columns(3)
        for idx, opt in enumerate(data['options']):
            with cols[idx]:
                if st.button(f"{opt['emoji']} {opt['zh']}"):
                    if opt['amis'] == target['amis']:
                        st.balloons()
                        st.success("答對了！")
                        time.sleep(1)
                        st.session_state.score += 1
                        st.session_state.current_q += 1
                        st.rerun()
                    else:
                        st.error("不對喔！")

    # Q2: 角色理解
    elif st.session_state.current_q == 1:
        data = st.session_state.q2_data
        st.markdown("**第 2 關：課文理解**")
        st.markdown(f"❓ **{data['q']}**")
        st.caption(f"({data['zh_q']})")
        
        ans = st.radio("請選擇正確答案：", data['options'])
        if st.button("送出答案"):
            if ans == data['ans']:
                st.balloons()
                st.success(f"沒錯！答案就是 {data['ans']}！")
                time.sleep(1)
                st.session_state.score += 1
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.error("再想一下，課文裡是怎麼說的呢？")

    # Q3: 句子翻譯
    elif st.session_state.current_q == 2:
        data = st.session_state.q3_data
        target = data['target']
        st.markdown("**第 3 關：句子翻譯**")
        st.markdown("請聽這句話，是什麼意思？")
        play_audio(target['amis'], filename_base=target['file'])
        
        for opt in data['options']:
            if st.button(opt):
                if opt == target['zh']:
                    st.balloons()
                    st.success("太厲害了！全部通關！🎉")
                    time.sleep(1)
                    st.session_state.score += 1
                    st.session_state.current_q += 1
                    st.rerun()
                else:
                    st.error("再聽一次看看！")

    # 結算
    else:
        st.markdown(f"""
        <div style='text-align: center; padding: 40px; background-color: #FFFFFF; border-radius: 24px; border: 4px solid #FFE082;'>
            <h1 style='color: #FF6F00 !important;'>🎉 挑戰成功！</h1>
            <p style='font-size: 20px; color: #5D4037 !important;'>你很了解你的朋友喔！</p>
            <div style='font-size: 80px; margin: 20px 0;'>👫</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 再玩一次"):
            init_quiz()
            st.rerun()

# --- 4. 主程式 ---
def main():
    st.markdown("<h1>O widang ako <br>我的朋友</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📖 學習模式", "🎮 測驗挑戰"])
    
    with tab1:
        show_learning_mode()
    
    with tab2:
        show_quiz_mode()

if __name__ == "__main__":
    main()
