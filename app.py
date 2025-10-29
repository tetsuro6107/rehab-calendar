import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import japanize_matplotlib
import calendar
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import io

# ページ設定
st.set_page_config(
    page_title="リハビリ訪問予定表作成アプリ",
    page_icon="📅",
    layout="centered"
)

# セッションステートの初期化
if 'transfers' not in st.session_state:
    st.session_state.transfers = []

# タイトル
st.title("📅 リハビリ訪問予定表作成アプリ")
st.markdown("---")

# カレンダー設定セクション
st.header("📆 カレンダー設定")

col1, col2 = st.columns(2)

with col1:
    year = st.selectbox(
        "年",
        options=[2024, 2025, 2026, 2027, 2028],
        index=1  # 2025をデフォルト
    )

with col2:
    month = st.selectbox(
        "月",
        options=list(range(1, 13)),
        index=datetime.now().month - 1
    )

st.markdown("---")

# 振替設定セクション
st.header("🔄 振替設定（オプション）")
st.caption("振替がない場合はそのまま「PDFを作成」ボタンを押してください")

col1, col2, col3 = st.columns(3)

with col1:
    transfer_from = st.number_input(
        "振替元（日）",
        min_value=1,
        max_value=31,
        value=1,
        step=1
    )

with col2:
    transfer_to = st.number_input(
        "振替先（日）",
        min_value=1,
        max_value=31,
        value=1,
        step=1
    )

with col3:
    transfer_time = st.text_input(
        "時間",
        value="11:20-12:00"
    )

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("➕ 振替を追加", use_container_width=True, type="primary"):
        if transfer_from < 1 or transfer_from > 31 or transfer_to < 1 or transfer_to > 31:
            st.error("❌ 日付は1-31の範囲で入力してください")
        else:
            st.session_state.transfers.append((transfer_from, transfer_to, transfer_time))
            st.success(f"✅ 振替を追加しました: {transfer_from}日 → {transfer_to}日 ({transfer_time})")
            st.rerun()

with col_btn2:
    if st.button("🗑️ 全てクリア", use_container_width=True):
        st.session_state.transfers = []
        st.success("🗑️ 振替を全てクリアしました")
        st.rerun()

# 登録された振替の表示
if st.session_state.transfers:
    st.info("**登録された振替:**")
    for i, (from_day, to_day, time) in enumerate(st.session_state.transfers, 1):
        col_del, col_info = st.columns([1, 9])
        with col_info:
            st.write(f"{i}. {from_day}日 → {to_day}日 ({time})")
        with col_del:
            if st.button("❌", key=f"del_{i}"):
                st.session_state.transfers.pop(i-1)
                st.rerun()
else:
    st.caption("振替なし")

st.markdown("---")

# PDF作成関数
def create_pdf(year, month, transfers_list):
    # カレンダー計算
    monday_time = "11:20-12:00"
    wednesday_time = "11:00-11:40"
    
    calendar.setfirstweekday(6)
    cal = calendar.monthcalendar(year, month)
    
    canceled_dates = [t[0] for t in transfers_list]
    makeup_visits = {t[1]: t[2] for t in transfers_list}
    
    monday_visits = []
    wednesday_visits = []
    
    for week in cal:
        if week[1] != 0 and week[1] not in canceled_dates:
            monday_visits.append(week[1])
        if week[3] != 0 and week[3] not in canceled_dates:
            wednesday_visits.append(week[3])
    
    # PDF作成
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        fig, ax = plt.subplots(figsize=(11, 14))
        ax.axis('off')
        
        plt.text(0.5, 0.97, f'{year}年{month}月 リハビリ訪問予定表', 
                ha='center', va='top', fontsize=20, fontweight='bold')
        
        plt.text(0.1, 0.92, '【通常の訪問時間】', 
                ha='left', va='top', fontsize=12, fontweight='bold')
        plt.text(0.12, 0.895, f'・月曜日：{monday_time}', 
                ha='left', va='top', fontsize=11, fontweight='bold')
        plt.text(0.12, 0.87, f'・水曜日：{wednesday_time}', 
                ha='left', va='top', fontsize=11, fontweight='bold')
        
        if canceled_dates or makeup_visits:
            plt.text(0.1, 0.83, '【振替予定】', 
                    ha='left', va='top', fontsize=12, fontweight='bold', color='red')
            y_pos = 0.805
            for cancel_date in canceled_dates:
                weekday = calendar.weekday(year, month, cancel_date)
                weekday_names = ['月', '火', '水', '木', '金', '土', '日']
                weekday_name = weekday_names[weekday]
                
                makeup_info = ""
                for makeup_day, makeup_time_str in makeup_visits.items():
                    makeup_weekday = calendar.weekday(year, month, makeup_day)
                    makeup_weekday_name = weekday_names[makeup_weekday]
                    makeup_info = f" → {month}月{makeup_day}日({makeup_weekday_name}) {makeup_time_str}"
                    break
                
                plt.text(0.12, y_pos, f'{month}月{cancel_date}日({weekday_name}){makeup_info}', 
                        ha='left', va='top', fontsize=11, fontweight='bold', color='red')
                y_pos -= 0.025
        
        start_y = 0.75
        cell_width = 0.13
        cell_height = 0.11
        start_x = 0.05
        
        days = ['日', '月', '火', '水', '木', '金', '土']
        day_colors = ['red', 'black', 'black', 'black', 'black', 'black', 'blue']
        
        for i, (day, color) in enumerate(zip(days, day_colors)):
            x = start_x + i * cell_width + cell_width / 2
            plt.text(x, start_y, day, ha='center', va='center', 
                    fontsize=14, fontweight='bold', color=color)
        
        for i in range(8):
            ax.plot([start_x + i * cell_width, start_x + i * cell_width], 
                   [start_y - 0.02, start_y - 0.02 - cell_height * 6], 
                   color='gray', linewidth=0.5)
        
        for i in range(7):
            ax.plot([start_x, start_x + cell_width * 7], 
                   [start_y - 0.02 - i * cell_height, start_y - 0.02 - i * cell_height], 
                   color='gray', linewidth=0.5)
        
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                
                x = start_x + day_num * cell_width + 0.01
                y = start_y - 0.04 - week_num * cell_height
                
                date_color = 'black'
                if day_num == 0:
                    date_color = 'red'
                elif day_num == 6:
                    date_color = 'blue'
                
                plt.text(x, y, str(day), ha='left', va='top', 
                        fontsize=13, color=date_color, fontweight='bold')
                
                visit_text = ""
                visit_color = 'green'
                
                if day in canceled_dates:
                    visit_text = "リハビリ\nお休み"
                    visit_color = 'red'
                elif day in makeup_visits:
                    visit_text = f"振替訪問\n{makeup_visits[day]}"
                    visit_color = 'red'
                elif day in monday_visits:
                    visit_text = f"訪問予定\n{monday_time}"
                elif day in wednesday_visits:
                    visit_text = f"訪問予定\n{wednesday_time}"
                
                if visit_text:
                    plt.text(x + cell_width / 2 - 0.01, y - 0.04, visit_text, 
                            ha='center', va='top', fontsize=11, color=visit_color, fontweight='bold')
        
        note_y = start_y - 0.02 - cell_height * 6 - 0.05
        plt.text(0.1, note_y, '※ 急な変更が生じた場合は、事前にご連絡させていただきます。', 
                ha='left', va='top', fontsize=10, fontweight='bold')
        plt.text(0.1, note_y - 0.03, '※ ご不明な点がございましたら、お気軽にお問い合わせください。', 
                ha='left', va='top', fontsize=10, fontweight='bold')
        
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    pdf_buffer.seek(0)
    return pdf_buffer, monday_visits, wednesday_visits, canceled_dates

# PDF作成ボタン
if st.button("📥 PDFを作成", use_container_width=True, type="primary"):
    with st.spinner("PDFを作成中..."):
        pdf_buffer, monday_visits, wednesday_visits, canceled_dates = create_pdf(
            year, month, st.session_state.transfers
        )
        
        st.success("✅ PDFを作成しました！")
        
        # 作成内容の表示
        with st.expander("📋 作成内容を確認"):
            st.write(f"**月曜日の訪問日:** {monday_visits}")
            st.write(f"**水曜日の訪問日:** {wednesday_visits}")
            if canceled_dates:
                st.write(f"**お休みの日:** {canceled_dates}")
                st.write(f"**振替訪問日:** {[t[1] for t in st.session_state.transfers]}")
        
        # ダウンロードボタン
        st.download_button(
            label="📥 PDFをダウンロード",
            data=pdf_buffer,
            file_name=f"{year}年{month}月_リハビリ訪問予定表.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")

# 使い方説明
with st.expander("💡 使い方"):
    st.markdown("""
    ### 基本的な使い方
    1. **年と月を選択**
    2. 振替がなければそのまま**「PDFを作成」ボタン**をクリック
    3. **「PDFをダウンロード」ボタン**でダウンロード
    
    ### 振替がある場合
    1. **年と月を選択**
    2. **振替元**、**振替先**、**時間**を入力
    3. **「振替を追加」ボタン**をクリック
    4. 複数の振替がある場合は繰り返す
    5. **「PDFを作成」ボタン**をクリック
    
    ### 振替を間違えた場合
    - 各振替の右側にある **❌ボタン** で個別削除
    - **「全てクリア」ボタン** で振替を全てリセット
    """)

st.caption("作成者: Claude | 月曜日（11:20-12:00）と水曜日（11:00-11:40）は自動的に訪問日になります")
