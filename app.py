import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.font_manager as fm
import calendar
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import io
import warnings
warnings.filterwarnings('ignore')

# 日本語フォント設定
try:
    import japanize_matplotlib
    japanize_matplotlib.japanize()
except:
    # 代替フォント設定
    try:
        font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
        font_prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
    except:
        # それでもダメな場合はデフォルト
        plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP', 'DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False

# ページ設定
st.set_page_config(
    page_title="リハビリ訪問予定表作成アプリ",
    page_icon="📅",
    layout="centered"
)

# カスタムCSS
st.markdown("""
<style>
    /* メインコンテンツの余白調整 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* タイトルのスタイル */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* セクションヘッダーのスタイル */
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* セレクトボックスのスタイル */
    .stSelectbox label {
        font-weight: 600;
        color: #2c3e50;
        font-size: 0.95rem;
    }
    
    /* ボタンのホバーエフェクト */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* 情報ボックスのスタイル */
    .stInfo, .stSuccess, .stWarning, .stError {
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* ダウンロードボタンのスタイル */
    .stDownloadButton button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 10px;
    }
    
    .stDownloadButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* キャプションのスタイル */
    .caption {
        color: #7f8c8d;
        font-size: 0.85rem;
    }
    
    /* 区切り線のスタイル */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# セッションステートの初期化
if 'transfers' not in st.session_state:
    st.session_state.transfers = []

# タイトル
st.title("📅 リハビリ訪問予定表作成アプリ")
st.markdown("<p style='color: #7f8c8d; font-size: 1.1rem; margin-top: -10px;'>月次の訪問スケジュールを簡単にPDF化</p>", unsafe_allow_html=True)
st.markdown("---")

# カレンダー設定セクション
st.header("📆 カレンダー設定")
st.markdown("<br>", unsafe_allow_html=True)

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
st.markdown("<br>", unsafe_allow_html=True)

# 振替設定セクション
st.header("🔄 振替設定")
st.caption("📌 振替がない場合はそのまま「PDFを作成」ボタンを押してください")
st.markdown("<br>", unsafe_allow_html=True)

# その月の月曜日と水曜日を取得
def get_mondays_and_wednesdays(year, month):
    calendar.setfirstweekday(6)  # 日曜始まり
    cal = calendar.monthcalendar(year, month)
    mondays = []
    wednesdays = []
    
    for week in cal:
        if week[1] != 0:  # 月曜日
            mondays.append(week[1])
        if week[3] != 0:  # 水曜日
            wednesdays.append(week[3])
    
    return sorted(mondays + wednesdays)

# 指定した日付の週の平日を取得
def get_weekdays_in_same_week(year, month, day):
    from datetime import date, timedelta
    
    target_date = date(year, month, day)
    weekday = target_date.weekday()  # 0=月曜, 6=日曜
    
    # その週の月曜日を取得
    monday = target_date - timedelta(days=weekday)
    
    # 月曜〜金曜を取得
    weekdays = []
    for i in range(5):  # 月〜金
        d = monday + timedelta(days=i)
        # 同じ月の日付のみ
        if d.month == month and d.day != day:  # 振替元は除外
            weekdays.append(d.day)
    
    return sorted(weekdays)

# 振替元の選択肢を取得
transfer_options = get_mondays_and_wednesdays(year, month)

col1, col2, col3 = st.columns([1.5, 1.5, 4])

with col1:
    if transfer_options:
        transfer_from = st.selectbox(
            "振替元（日）",
            options=transfer_options,
            format_func=lambda x: f"{x}日",
            key="transfer_from_select"
        )
    else:
        st.warning("訪問日がありません")
        transfer_from = None

with col2:
    if transfer_from:
        # 振替元の週の平日を取得
        weekday_options = get_weekdays_in_same_week(year, month, transfer_from)
        
        if weekday_options:
            transfer_to = st.selectbox(
                "振替先（日）",
                options=weekday_options,
                format_func=lambda x: f"{x}日 ({['月','火','水','木','金','土','日'][calendar.weekday(year, month, x)]})",
                key="transfer_to_select"
            )
        else:
            st.warning("振替可能な日がありません")
            transfer_to = None
    else:
        st.info("振替元を選択してください")
        transfer_to = None

with col3:
    st.write("**時間設定**")
    st.caption("定時: 9:00-17:30")
    
    time_row1 = st.columns([1, 1, 1])
    
    with time_row1[0]:
        start_hour = st.selectbox(
            "開始時",
            options=list(range(9, 18)),  # 9-17時
            index=2,  # デフォルト11時
            format_func=lambda x: f"{x}時",
            key="start_hour"
        )
    
    with time_row1[1]:
        start_min = st.selectbox(
            "開始分",
            options=list(range(0, 60, 5)),  # 0-55分、5分刻み
            index=4,  # デフォルト20分
            format_func=lambda x: f"{x:02d}分",
            key="start_min"
        )
    
    with time_row1[2]:
        duration = st.selectbox(
            "訪問時間",
            options=[40, 60],
            index=0,  # デフォルト40分
            format_func=lambda x: f"{x}分間",
            key="duration"
        )
    
    # 終了時刻を自動計算
    start_total_min = start_hour * 60 + start_min
    end_total_min = start_total_min + duration
    end_hour = end_total_min // 60
    end_min = end_total_min % 60
    
    # 終了時刻の表示
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1rem; 
                border-radius: 10px; 
                text-align: center;
                margin-top: 1rem;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <p style='color: white; font-size: 1.2rem; font-weight: 700; margin: 0;'>
            ⏰ {start_hour}:{start_min:02d} ～ {end_hour}:{end_min:02d}
        </p>
        <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem; margin: 0.3rem 0 0 0;'>
            訪問時間: {duration}分間
        </p>
    </div>
    """, unsafe_allow_html=True)

# 時間文字列を生成
transfer_time = f"{start_hour}:{start_min:02d}-{end_hour}:{end_min:02d}"

# 定時チェック（17:30まで）
if end_hour > 17 or (end_hour == 17 and end_min > 30):
    st.error("⚠️ 終了時刻が定時（17:30）を超えています")
    time_valid = False
else:
    time_valid = True

st.markdown("<br>", unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("➕ 振替を追加", use_container_width=True, type="primary"):
        # バリデーション
        if transfer_from is None or transfer_to is None:
            st.error("❌ 振替元と振替先を選択してください")
        elif not time_valid:
            st.error("❌ 終了時刻が定時を超えています")
        else:
            # 既に同じ振替が登録されていないかチェック
            if any(t[0] == transfer_from for t in st.session_state.transfers):
                st.warning("⚠️ この日付の振替は既に登録されています")
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
st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.transfers:
    st.markdown("**📋 登録された振替一覧**")
    for i, (from_day, to_day, time) in enumerate(st.session_state.transfers, 1):
        from_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, from_day)]
        to_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, to_day)]
        
        col_info, col_del = st.columns([9, 1])
        with col_info:
            st.markdown(f"""
            <div style='background: #f8f9fa; 
                        padding: 0.8rem 1rem; 
                        border-radius: 8px; 
                        border-left: 4px solid #667eea;
                        margin-bottom: 0.5rem;'>
                <span style='font-size: 1rem; font-weight: 600; color: #2c3e50;'>
                    {i}. {from_day}日({from_weekday}) → {to_day}日({to_weekday})
                </span>
                <span style='color: #7f8c8d; margin-left: 1rem;'>
                    {time}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col_del:
            if st.button("🗑️", key=f"del_{i}", help="削除"):
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
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<style>
    div[data-testid="stButton"] button[kind="primary"] {
        height: 60px;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)
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
    2. **振替元**を選択（その月の月曜日・水曜日から選択）
    3. **振替先**を選択（振替元と同じ週の平日から選択）
    4. **開始時刻**と**訪問時間**（40分/60分）を選択 → 終了時刻は自動計算！
    5. **「振替を追加」ボタン**をクリック
    6. 複数の振替がある場合は繰り返す
    7. **「PDFを作成」ボタン**をクリック
    
    ### 振替を間違えた場合
    - 各振替の右側にある **❌ボタン** で個別削除
    - **「全てクリア」ボタン** で振替を全てリセット
    
    ### 💡 ポイント
    - **振替元**: その月の訪問日（月・水）のみ選択可能
    - **振替先**: 振替元と同じ週の平日（月〜金）から選択可能
    - **時間設定**: 開始時刻（9:00〜17:00）+ 訪問時間（40分/60分）で自動計算
    - 終了時刻は自動で表示されるので入力ミスなし！
    - 振替先には曜日も表示されるので分かりやすい！
    """)

st.markdown("---")

st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 1rem 0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        💡 月曜日（11:20-12:00）と水曜日（11:00-11:40）は自動的に訪問日になります
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
        振替は開始時刻+訪問時間で設定 | 作成者: Claude
    </p>
</div>
""", unsafe_allow_html=True)
