import streamlit as st
import google.generativeai as genai

# --- ページ設定 ---
st.set_page_config(page_title="志望動機添削アシスタント", layout="wide")

# --- カスタムCSS（壁紙・明朝体・桜色テーマ・スマホ対応） ---
st.markdown("""
<style>
/* 1. 全体のフォントを游明朝に統一（※アイコンが壊れないよう span は除外しています） */
html, body, p, div, a, button, h1, h2, h3, h4, h5, h6, label {
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
    margin-top: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    font-size: 1.05rem;
    line-height: 1.8;
}

/* サブヘッダー色 */
h1, h2, h3 { color: #3D2D2E !important; }

/* 5. スマートフォン向けの画面表示設定（レスポンシブ対応） */
@media screen and (max-width: 768px) {
    .header-title { font-size: 1.5rem !important; }
    .header-subtitle { font-size: 0.95rem !important; margin-top: 0.8rem !important; }
    .header-box { padding: 2rem 1rem !important; }
    
    div[data-testid="stForm"] { padding: 15px !important; }
    .result-box { padding: 15px !important; font-size: 0.95rem !important; }
    
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.5rem !important; }
    p, label { font-size: 0.95rem !important; line-height: 1.6 !important; }
    
    /* スマホ用ボタン調整（横幅いっぱい） */
    [data-testid="stFormSubmitButton"] button, 
    .stButton button, 
    [data-testid="stLinkButton"] a {
        padding: 0.6rem 1rem !important;
        font-size: 1rem !important;
        width: 100% !important;
        text-align: center;
        margin-bottom: 10px !important;
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
        求職者の情報と求人情報を入力すると、AIがプロのキャリアコンサルタント視点で志望動機を添削・作成します。
    </div>
</div>
''', unsafe_allow_html=True)

st.info("【使い方】完璧な文章でなくても構いません。箇条書きや思いつく言葉を入力し、一番下の「志望動機を添削する」ボタンを押してください。\n\n※ブラウザの更新を押すと入力内容が消えてしまいます。長文はメモ帳などで作成してからの貼り付けをおすすめします。")

# --- はじめての方へ：APIキーの説明と取得手順 ---
with st.expander("🔰 はじめてご利用の方へ（APIって何？ / 無料APIキーの取得手順）", expanded=False):
    st.markdown("""
    **Q. 「API（エーピーアイ）」って何ですか？** A. このアプリの画面と、裏側で添削を行う「AI（頭脳）」を安全に繋ぐための**「専用の直通電話」**のようなものです。この高性能なAIを無料で利用していただくための**「通行手形」**として、利用者様ご自身に取得をお願いしております。（※もちろん料金が発生することはありませんのでご安心ください）

    ---
    **【図解】無料APIキーの取得手順（所要時間：約3分）**
    
    **ステップ1：Google AI Studioにアクセス** Googleアカウントにログインした状態で、[Google AI Studio](https://aistudio.google.com/) にアクセスします。

    **ステップ2：APIキーを発行** 画面左側のメニューから「Get API key」を選び、「Create API key」ボタンをクリックして新しいキーを作成します。
    
    **ステップ3：キーをコピーしてアプリに貼り付け** 画面に表示された `AIza...` から始まる長い文字列をコピーし、このアプリの左側（サイドバー）にある「APIキー」の入力欄に貼り付けてください。設定はこれだけで完了です！
    """)

# --- サイドバー：APIキー設定 ---
st.sidebar.header("🔑 セキュリティ設定")
st.sidebar.write("取得したGemini APIキーを入力してください。")
api_key = st.sidebar.text_input("APIキー", type="password")
st.sidebar.caption("※入力したキーは保存されず、画面を閉じると安全に消去されます。")

# --- 入力フォーム ---
with st.form("input_form"):
    st.subheader("【求職者の情報】")
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("年齢", min_value=15, max_value=100, value=35)
    with col2:
        gender = st.selectbox("性別", ["回答しない", "男性", "女性"])
    
    history = st.text_area("簡単な職歴（例：事務職5年／販売職3年／等）")
    episodes = st.text_area("これまでの仕事で「こだわったところ」「頑張り評価されたところ」「時間を忘れて夢中になったところ」")
    strengths = st.text_area("あなたの「強み」「価値観」")
    draft = st.text_area("作成した志望動機（ドラフトがない場合は空欄でも可）")

    st.subheader("【求人票の情報】")
    job_title = st.text_input("職種")
    emp_type = st.selectbox("雇用形態", ["正社員", "契約社員", "派遣社員", "パート・アルバイト", "業務委託", "その他"])
    job_desc = st.text_area("仕事内容")
    requirements = st.text_area("必要な免許・資格・スキル（経験）")

    submit_btn = st.form_submit_button("志望動機を添削する ✨")

# --- 実行処理 ---
if submit_btn:
    if not api_key:
        st.error("エラー：左側のサイドバーに「APIキー」を入力してください。（取得方法は上部の「🔰 はじめてご利用の方へ」をご参照ください）")
    elif not history or not job_title:
        st.warning("「簡単な職歴」と求人の「職種」は最低限入力してください。")
    else:
        # Gemini APIの設定
        genai.configure(api_key=api_key)
        # 最新の高速・高精度モデルを指定
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        あなたは求職者の支援に特化した，経験豊富で温かいキャリアコンサルタントであり，プロのライターです。
        以下の【求職者情報】と【求人情報】，および【志望動機作成の参考ガイドライン】を読み込み，求職者が自信を持って応募に進めるよう，添削後の志望動機およびアドバイス一式を出力してください。
        具体的な出力内容は，以下の【出力要件】に従ってください。

        【求職者情報】
        - 年齢：{age}
        - 性別：{gender}
        - 簡単な職歴：{history}
        - こだわった事/評価された事/夢中になった事：{episodes}
        - 強み/価値観：{strengths}
        - 作成した志望動機（ドラフト）：{draft}

        【求人情報】
        - 職種：{job_title}
        - 雇用形態：{emp_type}
        - 仕事内容：{job_desc}
        - 必要な免許・資格・スキル：{requirements}

        【志望動機作成の参考ガイドライン】
        添削の際は，求職者の職歴と求人情報の職種を比較し，「経験者」か「未経験者」かを判断した上で，以下の構成を柔軟に参考にして展開してください（毎回完全に当てはめる必要はありません）。
        書き出し（第一印象）で担当者を惹きつけ，締めくくりで「戦力としてどう能力を発揮できるか」をイメージさせることを意識してください。

        [パターン1：かなえたいことから記載する場合]
        ・経験者：①転職でかなえたいこと/きっかけ → ②なぜ応募企業なら実現できるか → ③発揮したい能力
        ・未経験：①かなえたいこと/未経験職種への理由 → ②なぜ応募企業か → ③発揮したい能力/短期間で戦力になる意欲
        [パターン2：応募企業への熱意から記載する場合]
        ・経験者：①入社したい理由 → ②培ってきた経験 → ③発揮したい能力
        ・未経験：①入社したい理由 → ②汎用できるスキル/自己啓発 → ③短期間で戦力になる意欲

        【AIへの特別な指示（作成のスタンス）】
        ・ドラフト補完：もし入力された志望動機（ドラフト）が空欄や箇条書き，極端に短い場合でも，入力された他の情報（職歴，エピソード，強み）を紡ぎ合わせ，ゼロから説得力のある文章を構築すること。
        ・架け橋の発見：求職者の「過去の経験・強み」と求人の「仕事内容」の共通点（ポータブルスキル）を見つけ出し，それを軸に「なぜこの仕事で活躍できるのか」の根拠を明確にすること。
        ・人間らしさ：AI特有の無難な定型文の多用を避け，求職者が入力したエピソードの生きた語彙をそのまま活かし，体温を感じるオリジナリティのある文章に仕上げること。
        ・想像部分の明示（太字化）：求職者の入力情報に具体的な実績や数字が不足しており，説得力を持たせるためにAIが仮のエピソードや成果を想像して補完する場合は，必ずその部分を「**」（Markdownの太字）で囲んで出力すること。（例：「前職では**業務効率化に取り組み，作業時間を20％削減しました**。」）

        【出力要件】
        以下の4つのセクションに分けて出力してください。

        1. 求職者へのポジティブなフィードバック
        - 提出された情報を肯定し，「今回の求人にどう活かせそうか」を添えて，応募への背中を押す温かい励ましの言葉を150文字程度で記載してください。

        2. 添削後の志望動機（履歴書用）
        以下の【制約条件】と【重要：年齢別の表現ルール】を必ず守って出力してください。
        【制約条件】
        ・指定文字数：250文字～300文字以内で作成すること
        ・言葉遣い：丁寧な「です・ます」調で，ビジネス文書としての格式を保つこと
        ・文章構成：これまでの経験，実績を具体的にアピールし，何ができるのか，今後何をやりたいのかを含めること
        ・使用禁止フレーズ：「未経験ですが」「御社で学ばせていただきたい」などの受け身の言葉は絶対に使用しないこと
        ・文末の挨拶文：文末に「どうぞよろしくお願い申し上げます。」等の挨拶文は入れないこと
        ・企業名の表記：応募先企業名を入れる場合は，履歴書等の書面を想定し「貴社」（自然な文脈であれば「御社」も可）とすること
        ・転職者の視点：応募者は転職者であるため，これまで培った経験を魅力ある文にして志望動機にすること。
        ・読点：文章中の読点には必ず「，」を使用すること（「、」は使用しないこと）
        ・注意書きの追記：もし太字で想像・補完した箇所がある場合は，志望動機の文章の最後に改行を入れ，「※【太字】の部分はAIが作成した例文（仮の成果・エピソード）です。必ずご自身の実際の経験に合わせて書き換えてからご使用ください。」と必ず明記すること。
        【重要：年齢別の表現ルール】
        ・求職者が34歳以下の場合は，「自分の強みを活かして貢献したい」「スキルを身につけて長く働きたい」「頑張ります」などのポテンシャルや熱意をアピールする表現を使用しても構いません。
        ・求職者が35歳以上の場合は，上記の幼稚に見える表現は一切使用しないでください。代わりに，これまでの経験を即戦力としてどう具体的に活かせるか，プロフェッショナルとしての貢献に焦点を当てた，落ち着きと説得力のある大人の表現にしてください。

        3. 志望動機の修正のポイント
        - どのような意図で構成したのか，どの強みを強調したのかをキャリアコンサルタント視点で3箇条書きで解説してください。

        4. 面接官に突っ込まれそうな点へのアドバイス
        - この経歴や志望動機から，面接でさらに深掘りされそうな質問を2つ予想し，どう答えると良いか（回答の方向性）を温かいトーンでアドバイスしてください。
        """

        with st.spinner('キャリアコンサルタントAIが添削中です... 少しお待ちください。'):
            try:
                response = model.generate_content(prompt)
                st.success("添削が完了しました！")
                st.markdown("---")
                # AIの回答を新デザインの枠（result-box）に入れて表示します
                st.markdown("<div class='result-box'>", unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota" in error_msg:
                    st.error("エラー：APIの利用制限に達しました。1分ほど待つか、新しいAPIキーを取得して再度お試しください。")
                else:
                    st.error(f"予期せぬエラーが発生しました。詳細: {e}")

# ==================================================
# 共通最下部：ポータルサイトへの戻りボタン
# ==================================================
st.markdown("---")
st.link_button("🏠 C.HARIGOMA キャリア支援ポータルへ戻る", "https://harigoma-career.streamlit.app/")
