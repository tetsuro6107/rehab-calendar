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
    page_title="リハビリ訪問予定表",
    page_icon="📅",
    layout="centered"
)

# 超スタイリッシュなCSS
st.markdown("""
<style>
    /* 全体設定 */
    .main .block-container {
        padding: 2rem 1.5rem;
        max-width: 1000px;
    }
    
    /* タイトル */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* セクションヘッダー */
    h2 {
        color: #2c3e50;
        font-weight: 800;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 1rem;
        border-bottom: 4px solid;
        border-image: linear-gradient(90deg, #667eea 0%, #764ba2 100%) 1;
        font-size: 1.8rem;
    }
    
    /* セレクトボックス */
    .stSelectbox label {
        font-weight: 700;
        color: #2c3e50;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
    }
    
    .stSelectbox > div > div {
        border-radius: 14px;
        border: 2px solid #e3e8ef;
        background: white;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .stSelectbox > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        transform: translateY(-1px);
    }
    
    /* セレクトボックス内のテキストを濃く */
    .stSelectbox div[data-baseweb="select"] > div {
        color: #1a202c !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    /* セレクトボックスの選択された値 */
    .stSelectbox div[data-baseweb="select"] span {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* ドロップダウンリスト内のテキスト */
    .stSelectbox ul[role="listbox"] li {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    /* ドロップダウンリストの背景 */
    .stSelectbox ul[role="listbox"] {
        background: white !important;
        border: 2px solid #e3e8ef !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15) !important;
        border-radius: 12px !important;
    }
    
    /* ドロップダウンのホバー */
    .stSelectbox ul[role="listbox"] li:hover {
        background: #f0f4ff !important;
        color: #667eea !important;
        font-weight: 700 !important;
    }
    
    /* ボタン */
    .stButton button {
        border-radius: 14px;
        font-weight: 700;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        letter-spacing: 0.5px;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.1rem;
        padding: 0.7rem 2rem;
        height: 55px;
    }
    
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.35);
    }
    
    /* ダウンロードボタン */
    .stDownloadButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 1.25rem !important;
        padding: 1.2rem 3rem !important;
        border-radius: 16px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* メッセージボックス */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        padding: 1.2rem;
        font-weight: 600;
        border-left: 5px solid;
    }
    
    /* 区切り線 */
    hr {
        margin: 3rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, rgba(102, 126, 234, 0.3) 50%, transparent 100%);
    }
</style>
""", unsafe_allow_html=True)

# セッション状態の初期化
if 'transfers' not in st.session_state:
    st.session_state.transfers = []

# タイトル
st.title("📅 リハビリ訪問予定表")
st.markdown("""
<div style='text-align: center; margin: -10px 0 30px 0;'>
    <p style='color: #7f8c8d; font-size: 1.2rem; font-weight: 500;'>
        月次スケジュールを数クリックでPDF化 ✨
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# カレンダー設定
st.header("📆 カレンダー設定")
col1, col2 = st.columns(2)

with col1:
    year = st.selectbox(
        "年",
        options=[2024, 2025, 2026, 2027, 2028],
        index=1
    )

with col2:
    month = st.selectbox(
        "月",
        options=list(range(1, 13)),
        index=datetime.now().month - 1
    )

st.markdown("---")

# 振替設定セクション
st.header("🔄 振替設定")

# スタイリッシュなカードデザイン
st.markdown("""
<div style='background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%);
            padding: 2.5rem 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.06);
            margin: 2rem 0;
            border: 1px solid rgba(102, 126, 234, 0.08);'>
    <p style='color: #7f8c8d; font-size: 0.95rem; font-weight: 600; margin: 0 0 1.5rem 0; text-align: center;'>
        💡 振替がない場合は、このセクションをスキップして「PDFを作成」ボタンへ
    </p>
</div>
""", unsafe_allow_html=True)

# 関数定義
def get_mondays_and_wednesdays(year, month):
    calendar.setfirstweekday(6)
    cal = calendar.monthcalendar(year, month)
    mondays = []
    wednesdays = []
    
    for week in cal:
        if week[1] != 0:
            mondays.append(week[1])
        if week[3] != 0:
            wednesdays.append(week[3])
    
    return sorted(mondays + wednesdays)

def get_weekdays_in_same_week(year, month, day):
    from datetime import date, timedelta
    
    target_date = date(year, month, day)
    weekday = target_date.weekday()
    monday = target_date - timedelta(days=weekday)
    
    weekdays = []
    for i in range(5):
        d = monday + timedelta(days=i)
        if d.month == month and d.day != day:
            weekdays.append(d.day)
    
    return sorted(weekdays)

transfer_options = get_mondays_and_wednesdays(year, month)

# グリッドレイアウト
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.05rem; margin-bottom:0.5rem;'>振替元（訪問日）</p>", unsafe_allow_html=True)
    if transfer_options:
        transfer_from = st.selectbox(
            "振替元を選択",
            options=transfer_options,
            format_func=lambda x: f"{x}日",
            key="transfer_from_select",
            label_visibility="collapsed"
        )
    else:
        st.warning("⚠️ 訪問日がありません")
        transfer_from = None

with col2:
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.05rem; margin-bottom:0.5rem;'>振替先（平日）</p>", unsafe_allow_html=True)
    if transfer_from:
        weekday_options = get_weekdays_in_same_week(year, month, transfer_from)
        
        if weekday_options:
            transfer_to = st.selectbox(
                "振替先を選択",
                options=weekday_options,
                format_func=lambda x: f"{x}日 ({['月','火','水','木','金','土','日'][calendar.weekday(year, month, x)]})",
                key="transfer_to_select",
                label_visibility="collapsed"
            )
        else:
            st.warning("⚠️ 振替可能な日がありません")
            transfer_to = None
    else:
        st.info("👆 まず振替元を選択してください")
        transfer_to = None

# 時間設定
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.05rem; margin-bottom:0.8rem;'>⏰ 時間設定</p>", unsafe_allow_html=True)

time_col1, time_col2, time_col3 = st.columns(3)

with time_col1:
    start_hour = st.selectbox(
        "開始時",
        options=list(range(9, 18)),
        index=2,
        format_func=lambda x: f"{x}時",
        key="start_hour"
    )

with time_col2:
    start_min = st.selectbox(
        "開始分",
        options=list(range(0, 60, 5)),
        index=4,
        format_func=lambda x: f"{x:02d}分",
        key="start_min"
    )

with time_col3:
    duration = st.selectbox(
        "訪問時間",
        options=[40, 60],
        index=0,
        format_func=lambda x: f"{x}分",
        key="duration"
    )

# 終了時刻計算
start_total_min = start_hour * 60 + start_min
end_total_min = start_total_min + duration
end_hour = end_total_min // 60
end_min = end_total_min % 60

# 時間表示（超スタイリッシュ）
st.markdown(f"""
<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            padding: 1.5rem 2rem; 
            border-radius: 16px; 
            text-align: center;
            margin: 1.5rem 0;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            border: 3px solid rgba(255,255,255,0.4);
            position: relative;
            overflow: hidden;'>
    <div style='position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
                background: radial-gradient(circle at top right, rgba(255,255,255,0.1), transparent);'>
    </div>
    <p style='color: white; font-size: 2rem; font-weight: 900; margin: 0; 
              letter-spacing: 2px; position: relative; z-index: 1;'>
        {start_hour}:{start_min:02d} ～ {end_hour}:{end_min:02d}
    </p>
    <p style='color: rgba(255,255,255,0.95); font-size: 1.1rem; margin: 0.5rem 0 0 0; 
              font-weight: 700; position: relative; z-index: 1;'>
        📋 訪問時間: {duration}分
    </p>
</div>
""", unsafe_allow_html=True)

# バリデーション
transfer_time = f"{start_hour}:{start_min:02d}-{end_hour}:{end_min:02d}"
time_valid = not (end_hour > 17 or (end_hour == 17 and end_min > 30))

if not time_valid:
    st.error("⚠️ 終了時刻が定時（17:30）を超えています")

st.markdown("<br>", unsafe_allow_html=True)

# ボタン
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("➕ 振替を追加", use_container_width=True, type="primary"):
        if transfer_from is None or transfer_to is None:
            st.error("❌ 振替元と振替先を選択してください")
        elif not time_valid:
            st.error("❌ 終了時刻が定時を超えています")
        else:
            if any(t[0] == transfer_from for t in st.session_state.transfers):
                st.warning("⚠️ この日付の振替は既に登録されています")
            else:
                st.session_state.transfers.append((transfer_from, transfer_to, transfer_time))
                st.success(f"✅ {transfer_from}日 → {transfer_to}日を追加しました")
                st.rerun()

with col_btn2:
    if st.button("🗑️ 全てクリア", use_container_width=True):
        st.session_state.transfers = []
        st.rerun()

# 登録された振替
st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.transfers:
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.1rem; margin-bottom:1rem;'>📋 登録された振替</p>", unsafe_allow_html=True)
    for i, (from_day, to_day, time) in enumerate(st.session_state.transfers, 1):
        from_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, from_day)]
        to_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, to_day)]
        
        col_info, col_del = st.columns([8.5, 1.5])
        with col_info:
            st.markdown(f"""
            <div style='background: white;
                        padding: 1.2rem 1.5rem; 
                        border-radius: 14px; 
                        border-left: 6px solid;
                        border-image: linear-gradient(180deg, #667eea 0%, #764ba2 100%) 1;
                        margin-bottom: 0.8rem;
                        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
                        transition: all 0.3s ease;'>
                <span style='font-size: 1.1rem; font-weight: 800; color: #2c3e50;'>
                    {i}. {from_day}日({from_weekday}) <span style='color: #667eea; font-size: 1.3rem;'>→</span> {to_day}日({to_weekday})
                </span>
                <span style='color: #7f8c8d; margin-left: 1.5rem; font-weight: 600; font-size: 1rem;'>
                    🕐 {time}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{i}", help="削除", use_container_width=True):
                st.session_state.transfers.pop(i-1)
                st.rerun()
else:
    st.markdown("<p style='color: #95a5a6; font-style: italic; text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;'>振替なし</p>", unsafe_allow_html=True)

st.markdown("---")

# PDF作成関数
def create_pdf(year, month, transfers_list):
    monday_time = "11:20-12:00"
    wednesday_time = "11:00-11:40"
    
    calendar.setfirstweekday(6)  # 日曜始まり
    cal = calendar.monthcalendar(year, month)
    
    canceled_dates = [t[0] for t in transfers_list]
    makeup_visits = {t[1]: t[2] for t in transfers_list}
    
    monday_visits = []
    wednesday_visits = []
    
    for week in cal:
        if week[1] != 0 and week[1] not in canceled_dates:  # 月曜日
            monday_visits.append(week[1])
        if week[3] != 0 and week[3] not in canceled_dates:  # 水曜日
            wednesday_visits.append(week[3])
    
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        fig, ax = plt.subplots(figsize=(11.7, 8.3))
        ax.set_xlim(0, 7)
        ax.set_ylim(0, len(cal) + 2)
        ax.axis('off')
        
        # タイトル
        title = f"{year}年{month}月 リハビリ訪問予定表"
        ax.text(3.5, len(cal) + 1.5, title, ha='center', va='center', 
                fontsize=24, fontweight='bold')
        
        # 曜日ヘッダー
        weekdays = ['日', '月', '火', '水', '木', '金', '土']
        for i, day in enumerate(weekdays):
            color = 'red' if i == 0 else 'blue' if i == 6 else 'black'
            ax.text(i + 0.5, len(cal) + 0.5, day, ha='center', va='center',
                   fontsize=16, fontweight='bold', color=color)
        
        # カレンダーグリッド
        for week_num, week in enumerate(cal):
            y = len(cal) - week_num
            
            for day_num, day in enumerate(week):
                x = day_num
                
                # セルの枠線
                rect = plt.Rectangle((x, y-1), 1, 1, fill=False, 
                                    edgecolor='gray', linewidth=1.5)
                ax.add_patch(rect)
                
                if day != 0:
                    # 日付の色
                    text_color = 'red' if day_num == 0 else 'blue' if day_num == 6 else 'black'
                    
                    # 日付を表示
                    ax.text(x + 0.15, y - 0.2, str(day), ha='left', va='top',
                           fontsize=14, fontweight='bold', color=text_color)
                    
                    # 訪問情報を追加
                    visit_info = []
                    
                    # 月曜日の訪問
                    if day_num == 1 and day in monday_visits:
                        visit_info.append(f"訪問\n{monday_time}")
                    
                    # 水曜日の訪問
                    if day_num == 3 and day in wednesday_visits:
                        visit_info.append(f"訪問\n{wednesday_time}")
                    
                    # 振替訪問
                    if day in makeup_visits:
                        visit_info.append(f"振替\n{makeup_visits[day]}")
                    
                    # 休みの日
                    if day in canceled_dates:
                        ax.text(x + 0.5, y - 0.5, "休み", ha='center', va='center',
                               fontsize=12, fontweight='bold', color='red',
                               bbox=dict(boxstyle='round', facecolor='pink', alpha=0.5))
                    
                    # 訪問情報を表示
                    if visit_info:
                        info_text = '\n'.join(visit_info)
                        bg_color = 'lightblue' if day not in makeup_visits else 'lightyellow'
                        ax.text(x + 0.5, y - 0.5, info_text, ha='center', va='center',
                               fontsize=10, fontweight='bold',
                               bbox=dict(boxstyle='round', facecolor=bg_color, alpha=0.7))
        
        # 凡例
        legend_y = -0.5
        ax.text(0.5, legend_y, "■ 青背景: 通常訪問", ha='left', va='center',
               fontsize=11, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        ax.text(2.5, legend_y, "■ 黄背景: 振替訪問", ha='left', va='center',
               fontsize=11, bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
        ax.text(4.5, legend_y, "■ ピンク: 休み", ha='left', va='center',
               fontsize=11, bbox=dict(boxstyle='round', facecolor='pink', alpha=0.5))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    pdf_buffer.seek(0)
    return pdf_buffer, monday_visits, wednesday_visits, canceled_dates

# PDF作成ボタン
st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("📥 PDFを作成", use_container_width=True, type="primary"):
    with st.spinner("📄 PDF作成中..."):
        pdf_buffer, monday_visits, wednesday_visits, canceled_dates = create_pdf(
            year, month, st.session_state.transfers
        )
        
        st.success("✅ PDFが完成しました！")
        
        with st.expander("📋 作成内容を確認"):
            st.write(f"**月曜日の訪問:** {monday_visits}")
            st.write(f"**水曜日の訪問:** {wednesday_visits}")
            if canceled_dates:
                st.write(f"**休みの日:** {canceled_dates}")
                st.write(f"**振替日:** {[t[1] for t in st.session_state.transfers]}")
        
        st.download_button(
            label="📥 PDFをダウンロード",
            data=pdf_buffer,
            file_name=f"{year}年{month}月_リハビリ訪問予定表.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.markdown("---")

# 使い方
with st.expander("💡 使い方ガイド"):
    st.markdown("""
    ### 📝 基本的な流れ
    1. **年月を選択** → カレンダー設定
    2. **振替がなければスキップ** → 直接PDF作成へ
    3. **振替がある場合** → 振替情報を入力して追加
    4. **PDFを作成** → ダウンロード
    
    ### 🔄 振替の設定方法
    - **振替元**: 月・水曜日から選択
    - **振替先**: 同じ週の平日から選択
    - **時間**: 開始時刻 + 訪問時間で自動計算
    
    ### 💡 ポイント
    - 終了時刻は自動計算されるので入力ミスなし
    - 定時（9:00-17:30）を超えるとエラー表示
    - 同じ日の重複登録を自動チェック
    """)

# フッター
st.markdown("""
<div style='text-align: center; margin-top: 3rem; padding: 2rem 0; 
            background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 16px;'>
    <p style='color: #7f8c8d; font-size: 0.95rem; font-weight: 600; margin: 0;'>
        💡 月曜日（11:20-12:00）と水曜日（11:00-11:40）は自動的に訪問日になります
    </p>
    <p style='color: #95a5a6; font-size: 0.85rem; margin: 0.8rem 0 0 0;'>
        Created with ❤️ by Claude
    </p>
</div>
""", unsafe_allow_html=True)
