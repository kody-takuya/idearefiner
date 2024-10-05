
import streamlit as st
import openai

# OpenAI APIキーの設定
openai.api_key = st.secrets['idearefiner']['OPENAI_API_KEY']

def generate_metrics(theme):
    prompt = f"""
        以下の課題「{theme}」に対して策定された戦略を、多方面から評価します。まずは戦略の良し悪しを評価するために考慮すべきポイント5つ、列記してください。
        各ポイントは1行で簡潔に表現し、説明は一切不要です。
        """
    response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
            {"role": "system", "content": "あなたはビジネス戦略の専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    metrics = response.choices[0].message.content.strip().split("\n")
    return metrics[:5] # リストとして返す

def generate_ideas(theme, metrics):
    metrics_str = "\n".join(metrics)
    prompt = f"""
                ビジネス戦略「{theme}」に関して、以下の評価指標を考慮した5つの革新的なアイデアを生成してください。アイデアだけを出力してください。
                各アイデアは1〜2文で簡潔に説明してください。\n\n評価指標:\n{metrics_str}
            """

    response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
            {"role": "system", "content": "あなたはビジネス戦略の専門家です。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    ideas = response.choices[0].message.content.strip().split("\n\n")
    return ideas[:5]  # 最大5つのアイデアを返す

def refine_metrics(theme, ideas, evaluations, current_metrics):
       ideas_with_scores = [f"アイデア: {idea}\n評価: {evaluation}/10" for idea, evaluation in zip(ideas, evaluations)]
       ideas_str = "\n\n".join(ideas_with_scores)
       current_metrics_str = "\n".join(current_metrics)
       
       prompt = f"""
                   テーマ「{theme}」に関する以下のアイデアと評価、および現在の評価指標を考慮して、より適切な5つの新しい評価指標を生成してください。
                   各指標は1行で簡潔に表現し、説明は一切不要です。
                   
                   現在の評価指標:
                   {current_metrics_str}
                   
                   アイデアと評価:
                   {ideas_str}
                   
                   評価は10点満点で評価されています。評価が高かったアイデアの良いところを見つけ、評価が低いアイデアを二度と策定しないような指標を策定してください。
                   
                   新しい評価指標:
               """
       response = openai.chat.completions.create(
               model="gpt-4o",
               messages=[
               {"role": "system", "content": "あなたはビジネス戦略の専門家です。"},
               {"role": "user", "content": prompt}
           ]
       )
       
       new_metrics = response.choices[0].message.content.strip().split("\n")
       return prompt, new_metrics[:5]  # プロンプトと最大5つの新しいメトリクスを返す

def main():
    st.title("Strategy Refiner")

    # セッション状態の初期化
    if 'theme' not in st.session_state:
        st.session_state.theme = ""
    if 'metrics' not in st.session_state:
        st.session_state.metrics = [""] * 5
    if 'ideas' not in st.session_state:
        st.session_state.ideas = [""] * 5
    if 'evaluations' not in st.session_state:
        st.session_state.evaluations = [0] * 5
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ""

    # テーマ入力
    st.session_state.theme = st.text_input("Theme", st.session_state.theme)

    # 評価軸生成ボタン
    if st.button("評価軸生成"):
        if st.session_state.theme:
            with st.spinner("指標を生成中..."):
                st.session_state.metrics = generate_metrics(st.session_state.theme)
            st.success("評価軸が生成されました。")
        else:
            st.warning("テーマを入力してください。")

    # 評価指標の表示と編集
    st.subheader("評価指標")
    for i in range(5):
        st.session_state.metrics[i] = st.text_input(f"Metrics {i+1}", st.session_state.metrics[i], key=f"metric_{i}")

    # アイデア生成ボタン
    if st.button("アイデア生成"):
        if st.session_state.theme and any(st.session_state.metrics):
            with st.spinner("アイデアを生成中..."):
                st.session_state.ideas = generate_ideas(st.session_state.theme, st.session_state.metrics)
            st.success("アイデアが生成されました。")
        else:
            st.warning("テーマと少なくとも1つの評価指標を入力してください。")

    # アイデアの表示、編集、評価
    st.subheader("アイデアと評価")
    for i in range(5):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.session_state.ideas[i] = st.text_area(f"Idea {i+1}", st.session_state.ideas[i], height=100, key=f"idea_{i}")
        with col2:
            st.session_state.evaluations[i] = st.number_input(f"評価 {i+1}", min_value=0, max_value=10, value=st.session_state.evaluations[i], step=1, key=f"eval_{i}")

    # 評価軸修正ボタン
    if st.button("評価軸修正"):
        if st.session_state.theme and any(st.session_state.ideas) and any(st.session_state.evaluations):
            with st.spinner("評価軸を修正中..."):
                prompt, new_metrics = refine_metrics(st.session_state.theme, st.session_state.ideas, st.session_state.evaluations, st.session_state.metrics)
                st.session_state.metrics = new_metrics
                st.session_state.prompt = prompt
            st.success("評価軸が更新されました。")
        else:
            st.warning("テーマ、アイデア、評価が必要です。")   

    st.markdown("---")
    st.caption("注意: このアプリケーションを使用するには、有効なOpenAI APIキーが必要です。")

if __name__ == "__main__":
    main()
