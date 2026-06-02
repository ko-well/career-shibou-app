import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="志望動機添削アシスタント", layout="wide")

# --- カスタムCSS（壁紙・明朝体・桜色テーマ・スマホ対応） ---
st.markdown("""
<style>
/* 1. 全体のフォントを游明朝に統一 */
html, body, p, div, span, a, button, h1, h2, h3, h4, h5, h6, label {
    font-family: 'Yu Mincho', '游明朝', 'YuMincho', 'Hiragino Mincho ProN', 'HGS明朝E', serif !important;
}

/* 2. ページ全体の壁紙（和紙風テクスチャ） */
.stApp {
    background-color: #FCFAFA;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.04'/%3E%3C/svg%3E");
    background-attachment: fixed;
}

/* 3. ヘッダーデザイン（PC用） */
.header-box {
    text-align: center;
    padding: 3rem 1rem;
    background-color: rgba(255, 255, 255, 0.8);
    border-bottom: 2px solid #DB90A0;
    margin-bottom: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
}
.header-title { font-size: 2.2rem; font-weight: 700; color: #3D2D2E; }
.header-subtitle { font-size: 1.1rem; color: #5C4B4D; margin-top: 0.8rem; line-height: 1.6; }

/* 4. フォームと結果コンテナのデザイン */
div[data-testid="stForm"] {
    background-color: rgba(255, 255, 255, 0.9) !important;
    border-radius: 8px !important;
    padding: 30px !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
}
.result-box {
    background-color: #FDFEFE;
    padding: 25px;
    border-radius: 8px;
    border-left: 5px solid #DB90A0;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    font-size: 1.05rem;
    line-height: 1.8;
}

/* サブヘッダー色 */
h3 { color: #3D2D2E !important; }

/* ★5. スマートフォン向けの画面表示設定（レスポンシブ対応） */
@media screen and (max-width: 768px) {
    /* タイトル周りの縮小 */
    .header-title { font-size: 1.5rem !important; }
    .header-subtitle { font-size: 0.95rem !important; margin-top: 0.8rem !important; }
    .header-box { padding: 2rem 1rem !important; }
    
    /* フォームや結果の余白を詰める */
    div[data-testid="stForm"] { padding: 15px !important; }
    .result-box { padding: 15px !important; font-size: 0.95rem !important; }
    
    /* 見出しとテキストの縮小 */
    h3 { font-size: 1.2rem !important; margin-bottom: 0.5rem !important; }
    p, label { font-size: 0.95rem !important; line-height: 1.6 !important; }
    
    /* スマホ用ボタン調整（横幅いっぱいにしてタップしやすく） */
    [data-testid="stFormSubmitButton"] button, 
    .stButton button, 
    [data-testid="stLinkButton"] a {
        padding: 0.6rem 1rem !important;
        font-size: 1rem !important;
        width: 100% !important;
        text-align: center;
    }
}

/* 6. ボタンのデザイン（PC用ベース） */
[data-testid="stFormSubmitButton"] button, 
.stButton button,
[data-testid="stLinkButton"] a {
    background-color: #DB90A0 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
    padding: 0.7rem 3rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    width: 100% !important;
    text-align: center;
    text-decoration: none !important;
    transition: all 0.3s ease;
}
[data-testid="stFormSubmitButton"] button:hover,
.stButton button:hover,
[data-testid="stLinkButton"] a:hover {
    background-color: #C27082 !important;
    transform: translateY(-2px);
}
[data-testid="stLinkButton"] a * {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# --- タイトル表示 ---
st.markdown('''
<div class="header-box">
    <div class="header-title">📝 志望動機添削アシスタント</div>
    <div class="header-subtitle">
        あなたが書いた志望動機を、求人情報と照らし合わせてプロの視点で添削します。<br>
        より面接官の心に響く、説得力のある文章へブラッシュアップしましょう。
    </div>
</div>
''', unsafe_allow_html=True)

# --- APIキー設定 ---
st.sidebar.header("🔑 セキュリティ設定")
api_key = st.sidebar.text_input("Gemini APIキー", type="password")

# --- 入力フォーム ---
with st.form("resume_form"):
    st.markdown("### 📋 添削に必要な情報を入力してください")
    job_description = st.text_area("求人情報（職務内容や求める人物像など）", height=150, placeholder="ハローワークや求人サイトに記載されている内容をコピー＆ペーストしてください")
    user_motivation = st.text_area("あなたが書いた志望動機", height=200, placeholder="現状の志望動機を入力してください（箇条書きやメモ程度でも構いません）")
    
    submit_btn = st.form_submit_button("✨ プロの視点で添削・ブラッシュアップする ➔")

# --- 処理実行 ---
if submit_btn:
    if not api_key:
        st.error("⚠️ 左側のメニューにAPIキーを入力してください。")
    elif not job_description or not user_motivation:
        st.warning("⚠️ 求人情報と志望動機の両方を入力してください。")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        あなたはプロのキャリアコンサルタントです。
        以下の「求人情報」と求職者が書いた「志望動機」を読み込み、より採用担当者に刺さる説得力のある志望動機へと添削してください。
        
        【求人情報】
        {job_description}
        
        【求職者が書いた志望動機】
        {user_motivation}
        
        以下の構成で出力してください。
        
        1. 【良かった点】：現状の志望動機で優れている点、アピールできている点を褒めてください。
        2. 【改善ポイント】：求人情報と照らし合わせ、足りない要素や表現を直すべき点を具体的に指摘してください。
        3. 【ブラッシュアップ案】：指摘を踏まえ、そのまま履歴書に書けるレベルに整えた「完成版の志望動機」を提示してください。
        
        ※出力にはHTMLタグは使用せず、Markdown形式で読みやすく構成してください。
        """
        
        with st.spinner("⏳ キャリアコンサルタントがあなたの志望動機を分析・添削しています..."):
            try:
                response = model.generate_content(prompt)
                st.markdown("### 💡 添削結果とブラッシュアップ案")
                st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                st.write(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

# ==================================================
# 共通最下部：ポータルサイトへの戻りボタン
# ==================================================
st.markdown("---")
st.link_button("🏠 C.HARIGOMA キャリア支援ポータルへ戻る", "https://harigoma-career.streamlit.app/")
