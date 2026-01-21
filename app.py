import streamlit as st
import time
import os
from gtts import gTTS
from io import BytesIO

# --- 0. 系統配置 ---
st.set_page_config(page_title="Unit 3: O loma' no mako", page_icon="🏠", layout="centered")

# CSS 優化 (卡片與按鈕樣式)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-size: 24px;
        background-color: #FFD700;
        color: #333;
        border: none;
        padding: 10px;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #FFC107;
        transform: scale(1.02);
    }
    .big-font {
        font-size: 40px !important;
        font-weight: bold;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 5px;
    }
    .med-font {
        font-size: 22px !important;
        color: #555;
        text-align: center;
        margin-bottom: 10px;
    }
    .card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 數據資料庫 (Unit 3 專屬) ---

# 單字：家庭成員
VOCABULARY = {
    "Wama":     {"zh": "爸爸", "emoji": "👨", "file": "u3_wama"},
    "Wina":     {"zh": "媽媽", "emoji": "👩", "file": "u3_wina"},
    "Akong":    {"zh": "阿公", "emoji": "👴", "file": "u3_akong"},
    "Ama":      {"zh": "阿嬤", "emoji": "👵", "file": "u3_ama"},
    "Kaka":     {"zh": "哥哥/姊姊", "emoji": "👦", "file": "u3_kaka"},
    "Safa":     {"zh": "弟弟/妹妹", "emoji": "👶", "file": "u3_safa"}
}

# 句型：結合動作 (Unit 2) + 人物 (Unit 3)
SENTENCES = [
    {"amis": "Romadiw ci Wina.", "zh": "媽媽在唱歌。", "file": "u3_s_mom_sings"},
    {"amis": "Mafoti' ci Akong.", "zh": "阿公在睡覺。", "file": "u3_s_grandpa_sleeps"},
    {"amis": "Cima ko romadiway?", "zh": "誰在唱歌？", "file": "u3_q_who_sings"}
]

# --- 1.5 智慧語音核心 ---
def play_audio(text, filename_base=None):
    # 優先檢查是否有預錄的音檔
    if filename_base:
        path_m4a = f"audio/{filename_base}.m4a"
        if os.path.exists(path_m4a):
            st.audio(path_m4a, format='audio/mp4')
            return
        path_mp3 = f"audio/{filename_base}.mp3"
        if os.path.exists(path_mp3):
            st.audio(path_mp3, format='audio/mp3')
            return

    # 如果沒有檔案，使用 Google小姐 (印尼語腔調模擬)
    try:
        tts = gTTS(text=text, lang='id')
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        st.audio(fp, format='audio/mp3')
    except:
        st.caption("🔇 (無聲)")

# --- 2. 狀態管理 ---
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0

# --- 3. 學習模式 (Learning Mode) ---
def show_learning_mode():
    st.markdown("<h2 style='text-align: center;'>Sakatoolo: O loma' no mako</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>我的家庭 🏠</h4>", unsafe_allow_html=True)
    
    # 顯示單字卡
    col1, col2 = st.columns(2)
    words = list(VOCABULARY.items())
    
    for idx, (amis, data) in enumerate(words):
        with (col1 if idx % 2 == 0 else col2):
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div style="font-size: 60px;">{data['emoji']}</div>
                    <div class="big-font">{amis}</div>
                    <div class="med-font">{data['zh']}</div>
                </div>
                """, unsafe_allow_html=True)
                play_audio(amis, filename_base=data.get('file'))

    st.markdown("---")
    st.markdown("### 🗣️ 句型練習：誰在做什麼？")
    
    # 句子 1
    s1 = SENTENCES[0]
    st.info(f"🔹 {s1['amis']}")
    st.caption(f"({s1['zh']})")
    play_audio(s1['amis'], filename_base=s1.get('file'))
    
    # 句子 2
    s2 = SENTENCES[1]
    st.info(f"🔹 {s2['amis']}")
    st.caption(f"({s2['zh']})")
    play_audio(s2['amis'], filename_base=s2.get('file'))
    
    # 問答
    st.markdown("#### ❓ 問答練習")
    q = SENTENCES[2]
    st.success(f"Q: {q['amis']} ({q['zh']})")
    play_audio(q['amis'], filename_base=q.get('file'))
    
    st.warning("A: Ci Wina. (是媽媽。)")
    play_audio("Ci Wina", filename_base="u3_wina")

# --- 4. 測驗模式 (Quiz Mode) ---
def show_quiz_mode():
    st.markdown("<h2 style='text-align: center;'>🎮 家庭小偵探</h2>", unsafe_allow_html=True)
    progress = st.progress(st.session_state.current_q / 3)
    
    # 第一關：單字聽力
    if st.session_state.current_q == 0:
        st.markdown("### 第一關：這是誰？")
        st.write("請聽聲音：")
        play_audio("Akong", filename_base="u3_akong")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👴 阿公"):
                st.balloons()
                st.success("答對了！ Akong!")
                time.sleep(1)
                st.session_state.score += 100
                st.session_state.current_q += 1
                st.rerun()
        with c2:
            if st.button("👵 阿嬤"): st.error("那是 Ama 喔！")

    # 第二關：句子理解
    elif st.session_state.current_q == 1:
        st.markdown("### 第二關：誰在唱歌？")
        st.markdown("#### 請聽句子：")
        play_audio("Romadiw ci Wina.", filename_base="u3_s_mom_sings")
        
        st.write("請問句子裡是誰在唱歌？")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("👩 媽媽"):
                st.snow()
                st.success("沒錯！ Romadiw ci Wina.")
                time.sleep(1)
                st.session_state.score += 100
                st.session_state.current_q += 1
                st.rerun()
        with c2:
            if st.button("👶 妹妹"): st.error("不對喔！")

    # 第三關：問答
    elif st.session_state.current_q == 2:
        st.markdown("### 第三關：看圖回答")
        st.markdown("#### Q: Cima ko mafoti'ay? (誰在睡覺？)")
        play_audio("Cima ko mafoti'ay?", filename_base="u3_q_who_sleeps") # 模擬問句
        
        st.markdown("<div style='font-size:80px; text-align:center;'>👴💤</div>", unsafe_allow_html=True)
        
        options = ["Ci Wama (是爸爸)", "Ci Akong (是阿公)", "Ci Safa (是弟弟)"]
        choice = st.radio("請選擇：", options)
        
        if st.button("確定送出"):
            if "Akong" in choice:
                st.balloons()
                st.success("太厲害了！全部答對！")
                time.sleep(1)
                st.session_state.score += 100
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.error("再看一次圖片喔！")

    else:
        st.markdown(f"<div style='text-align: center;'><h1>🏆 挑戰完成！</h1><h2>得分：{st.session_state.score}</h2></div>", unsafe_allow_html=True)
        if st.button("再玩一次"):
            st.session_state.current_q = 0
            st.session_state.score = 0
            st.rerun()

# --- 5. 主程式入口 ---
st.sidebar.title("Unit 3: O loma' 🏠")
mode = st.sidebar.radio("選擇模式", ["📖 學習單詞", "🎮 練習挑戰"])

if mode == "📖 學習單詞":
    show_learning_mode()
else:
    show_quiz_mode()
