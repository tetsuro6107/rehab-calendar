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

# スタッフ名のデフォルト値を設定
if 'staff1' not in st.session_state:
    st.session_state.staff1 = ""
if 'staff2' not in st.session_state:
    st.session_state.staff2 = ""
if 'staff3' not in st.session_state:
    st.session_state.staff3 = ""

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

# スタッフ設定セクション
st.header("👥 スタッフ設定")
st.markdown("""
<div style='background: linear-gradient(145deg, #e3f2fd 0%, #ffffff 100%);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.06);
            margin: 2rem 0;
            border: 1px solid rgba(33, 150, 243, 0.2);'>
    <p style='color: #1565c0; font-size: 0.95rem; font-weight: 600; margin: 0; text-align: center;'>
        💡 訪問を担当するスタッフの名前を登録してください
    </p>
</div>
""", unsafe_allow_html=True)

# スタッフ名の入力
col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    staff1 = st.text_input(
        "スタッフ1（例: 田中太郎）",
        placeholder="スタッフ名を入力",
        key="staff1_input",
        max_chars=20
    )

with col_s2:
    staff2 = st.text_input(
        "スタッフ2（例: 佐藤花子）",
        placeholder="スタッフ名を入力",
        key="staff2_input",
        max_chars=20
    )

with col_s3:
    staff3 = st.text_input(
        "スタッフ3（例: 鈴木一郎）",
        placeholder="スタッフ名を入力",
        key="staff3_input",
        max_chars=20
    )

# スタッフリストを作成（入力されたもののみ）
staff_list = []
if staff1.strip():
    staff_list.append(staff1.strip())
if staff2.strip():
    staff_list.append(staff2.strip())
if staff3.strip():
    staff_list.append(staff3.strip())

# 最低1人は必要
if not staff_list:
    st.warning("⚠️ 最低1人のスタッフ名を入力してください")

st.markdown("---")

# 定期訪問設定セクション
st.header("📅 定期訪問設定")
st.markdown("""
<div style='background: linear-gradient(145deg, #e8f5e9 0%, #ffffff 100%);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.06);
            margin: 2rem 0;
            border: 1px solid rgba(76, 175, 80, 0.2);'>
    <p style='color: #2e7d32; font-size: 0.95rem; font-weight: 600; margin: 0; text-align: center;'>
        💡 毎週の訪問回数と訪問日を設定してください
    </p>
</div>
""", unsafe_allow_html=True)

# 訪問回数選択
st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.15rem; margin-bottom:1rem;'>📊 週の訪問回数</p>", unsafe_allow_html=True)

visit_count = st.selectbox(
    "訪問回数を選択",
    options=[1, 2, 3],
    format_func=lambda x: f"週{x}回",
    index=1,  # デフォルト: 週2回
    key="visit_count",
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# 訪問日1
st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.1rem; margin-bottom:0.5rem;'>🔹 定期訪問日 1</p>", unsafe_allow_html=True)

col_v1_day, col_v1_time = st.columns([1, 2])

with col_v1_day:
    visit1_weekday = st.selectbox(
        "曜日",
        options=['月曜日', '火曜日', '水曜日', '木曜日', '金曜日'],
        index=0,  # デフォルト: 月曜日
        key="visit1_weekday"
    )

with col_v1_time:
    v1_col1, v1_col2, v1_col3 = st.columns(3)
    
    with v1_col1:
        visit1_start_hour = st.selectbox(
            "開始時",
            options=list(range(9, 18)),
            index=2,  # デフォルト: 11時
            format_func=lambda x: f"{x}時",
            key="visit1_start_hour"
        )
    
    with v1_col2:
        visit1_start_min = st.selectbox(
            "開始分",
            options=list(range(0, 60, 5)),
            index=4,  # デフォルト: 20分
            format_func=lambda x: f"{x:02d}分",
            key="visit1_start_min"
        )
    
    with v1_col3:
        visit1_duration = st.selectbox(
            "訪問時間",
            options=[40, 60],
            index=0,  # デフォルト: 40分
            format_func=lambda x: f"{x}分",
            key="visit1_duration"
        )

# 訪問日1の担当スタッフ選択
st.markdown("<p style='font-weight:600; color:#2c3e50; font-size:0.95rem; margin:0.8rem 0 0.3rem 0;'>👤 担当スタッフ</p>", unsafe_allow_html=True)

if staff_list:
    visit1_staff = st.selectbox(
        "担当スタッフを選択",
        options=staff_list,
        index=0,
        key="visit1_staff",
        label_visibility="collapsed"
    )
else:
    st.info("💡 スタッフ設定でスタッフ名を入力してください")
    visit1_staff = "未設定"

# 訪問日1の終了時刻計算
v1_end_total = visit1_start_hour * 60 + visit1_start_min + visit1_duration
v1_end_hour = v1_end_total // 60
v1_end_min = v1_end_total % 60
visit1_time = f"{visit1_start_hour}:{visit1_start_min:02d}-{v1_end_hour}:{v1_end_min:02d}"

st.markdown(f"""
<div style='background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%); 
            padding: 0.8rem 1.5rem; 
            border-radius: 12px; 
            text-align: center;
            margin: 1rem 0;'>
    <p style='color: white; font-size: 1.1rem; font-weight: 700; margin: 0;'>
        📌 {visit1_weekday} {visit1_time}
    </p>
    <p style='color: rgba(255,255,255,0.95); font-size: 0.95rem; font-weight: 600; margin: 0.3rem 0 0 0;'>
        👤 担当: {visit1_staff}
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 訪問日2（週2回以上の場合のみ表示）
if visit_count >= 2:
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.1rem; margin-bottom:0.5rem;'>🔹 定期訪問日 2</p>", unsafe_allow_html=True)

    col_v2_day, col_v2_time = st.columns([1, 2])

    with col_v2_day:
        visit2_weekday = st.selectbox(
            "曜日",
            options=['月曜日', '火曜日', '水曜日', '木曜日', '金曜日'],
            index=2,  # デフォルト: 水曜日
            key="visit2_weekday"
        )

    with col_v2_time:
        v2_col1, v2_col2, v2_col3 = st.columns(3)
        
        with v2_col1:
            visit2_start_hour = st.selectbox(
                "開始時",
                options=list(range(9, 18)),
                index=2,  # デフォルト: 11時
                format_func=lambda x: f"{x}時",
                key="visit2_start_hour"
            )
        
        with v2_col2:
            visit2_start_min = st.selectbox(
                "開始分",
                options=list(range(0, 60, 5)),
                index=0,  # デフォルト: 00分
                format_func=lambda x: f"{x:02d}分",
                key="visit2_start_min"
            )
        
        with v2_col3:
            visit2_duration = st.selectbox(
                "訪問時間",
                options=[40, 60],
                index=0,  # デフォルト: 40分
                format_func=lambda x: f"{x}分",
                key="visit2_duration"
            )

    # 訪問日2の担当スタッフ選択
    st.markdown("<p style='font-weight:600; color:#2c3e50; font-size:0.95rem; margin:0.8rem 0 0.3rem 0;'>👤 担当スタッフ</p>", unsafe_allow_html=True)
    
    if staff_list:
        visit2_staff = st.selectbox(
            "担当スタッフを選択",
            options=staff_list,
            index=min(1, len(staff_list)-1) if len(staff_list) > 1 else 0,
            key="visit2_staff",
            label_visibility="collapsed"
        )
    else:
        st.info("💡 スタッフ設定でスタッフ名を入力してください")
        visit2_staff = "未設定"

    # 訪問日2の終了時刻計算
    v2_end_total = visit2_start_hour * 60 + visit2_start_min + visit2_duration
    v2_end_hour = v2_end_total // 60
    v2_end_min = v2_end_total % 60
    visit2_time = f"{visit2_start_hour}:{visit2_start_min:02d}-{v2_end_hour}:{v2_end_min:02d}"

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%); 
                padding: 0.8rem 1.5rem; 
                border-radius: 12px; 
                text-align: center;
                margin: 1rem 0;'>
        <p style='color: white; font-size: 1.1rem; font-weight: 700; margin: 0;'>
            📌 {visit2_weekday} {visit2_time}
        </p>
        <p style='color: rgba(255,255,255,0.95); font-size: 0.95rem; font-weight: 600; margin: 0.3rem 0 0 0;'>
            👤 担当: {visit2_staff}
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # 週1回の場合はダミー値
    visit2_weekday = None
    visit2_time = None
    visit2_start_hour = None
    visit2_start_min = None
    visit2_duration = None
    visit2_staff = None

st.markdown("<br>", unsafe_allow_html=True)

# 訪問日3（週3回の場合のみ表示）
if visit_count >= 3:
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.1rem; margin-bottom:0.5rem;'>🔹 定期訪問日 3</p>", unsafe_allow_html=True)

    col_v3_day, col_v3_time = st.columns([1, 2])

    with col_v3_day:
        visit3_weekday = st.selectbox(
            "曜日",
            options=['月曜日', '火曜日', '水曜日', '木曜日', '金曜日'],
            index=4,  # デフォルト: 金曜日
            key="visit3_weekday"
        )

    with col_v3_time:
        v3_col1, v3_col2, v3_col3 = st.columns(3)
        
        with v3_col1:
            visit3_start_hour = st.selectbox(
                "開始時",
                options=list(range(9, 18)),
                index=2,  # デフォルト: 11時
                format_func=lambda x: f"{x}時",
                key="visit3_start_hour"
            )
        
        with v3_col2:
            visit3_start_min = st.selectbox(
                "開始分",
                options=list(range(0, 60, 5)),
                index=0,  # デフォルト: 00分
                format_func=lambda x: f"{x:02d}分",
                key="visit3_start_min"
            )
        
        with v3_col3:
            visit3_duration = st.selectbox(
                "訪問時間",
                options=[40, 60],
                index=0,  # デフォルト: 40分
                format_func=lambda x: f"{x}分",
                key="visit3_duration"
            )

    # 訪問日3の担当スタッフ選択
    st.markdown("<p style='font-weight:600; color:#2c3e50; font-size:0.95rem; margin:0.8rem 0 0.3rem 0;'>👤 担当スタッフ</p>", unsafe_allow_html=True)
    
    if staff_list:
        visit3_staff = st.selectbox(
            "担当スタッフを選択",
            options=staff_list,
            index=min(2, len(staff_list)-1) if len(staff_list) > 2 else 0,
            key="visit3_staff",
            label_visibility="collapsed"
        )
    else:
        st.info("💡 スタッフ設定でスタッフ名を入力してください")
        visit3_staff = "未設定"

    # 訪問日3の終了時刻計算
    v3_end_total = visit3_start_hour * 60 + visit3_start_min + visit3_duration
    v3_end_hour = v3_end_total // 60
    v3_end_min = v3_end_total % 60
    visit3_time = f"{visit3_start_hour}:{visit3_start_min:02d}-{v3_end_hour}:{v3_end_min:02d}"

    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%); 
                padding: 0.8rem 1.5rem; 
                border-radius: 12px; 
                text-align: center;
                margin: 1rem 0;'>
        <p style='color: white; font-size: 1.1rem; font-weight: 700; margin: 0;'>
            📌 {visit3_weekday} {visit3_time}
        </p>
        <p style='color: rgba(255,255,255,0.95); font-size: 0.95rem; font-weight: 600; margin: 0.3rem 0 0 0;'>
            👤 担当: {visit3_staff}
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # 訪問日3が無効の場合のダミー値
    visit3_weekday = None
    visit3_time = None
    visit3_start_hour = None
    visit3_start_min = None
    visit3_duration = None
    visit3_staff = None

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
def get_visit_days(year, month, weekday_name):
    """指定した曜日の日付リストを取得"""
    weekday_map = {
        '月曜日': 1, '火曜日': 2, '水曜日': 3,
        '木曜日': 4, '金曜日': 5
    }
    
    weekday_num = weekday_map[weekday_name]
    
    calendar.setfirstweekday(6)  # 日曜始まり
    cal = calendar.monthcalendar(year, month)
    days = []
    
    for week in cal:
        if week[weekday_num] != 0:
            days.append(week[weekday_num])
    
    return sorted(days)

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

# 定期訪問日1の日付を取得
visit1_days = get_visit_days(year, month, visit1_weekday)

# 訪問回数に応じて訪問日を追加
if visit_count >= 2:
    visit2_days = get_visit_days(year, month, visit2_weekday)
    transfer_options = sorted(visit1_days + visit2_days)
else:
    visit2_days = []
    transfer_options = sorted(visit1_days)

# 週3回の場合は訪問日3も追加
if visit_count >= 3:
    visit3_days = get_visit_days(year, month, visit3_weekday)
    transfer_options = sorted(visit1_days + visit2_days + visit3_days)
else:
    visit3_days = []

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
def create_pdf(year, month, transfers_list, visit1_config, visit2_config=None, visit3_config=None):
    """
    visit1_config = {'weekday': '月曜日', 'time': '11:20-12:00', 'days': [3, 10, 17, 24]}
    visit2_config = {'weekday': '水曜日', 'time': '11:00-11:40', 'days': [5, 12, 19, 26]} or None
    visit3_config = {'weekday': '金曜日', 'time': '14:00-15:00', 'days': [7, 14, 21, 28]} or None
    """
    calendar.setfirstweekday(6)  # 日曜始まり
    cal = calendar.monthcalendar(year, month)
    
    canceled_dates = [t[0] for t in transfers_list]
    makeup_visits = {t[1]: t[2] for t in transfers_list}
    
    # 休みを除いた訪問日リスト
    visit1_actual_days = [d for d in visit1_config['days'] if d not in canceled_dates]
    
    if visit2_config:
        visit2_actual_days = [d for d in visit2_config['days'] if d not in canceled_dates]
    else:
        visit2_actual_days = []
    
    if visit3_config:
        visit3_actual_days = [d for d in visit3_config['days'] if d not in canceled_dates]
    else:
        visit3_actual_days = []
    
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        fig, ax = plt.subplots(figsize=(11.7, 8.3))
        ax.set_xlim(0, 7)
        ax.set_ylim(0, len(cal) + 3.5)
        ax.axis('off')
        
        # タイトル
        title = f"{year}年{month}月 リハビリ訪問予定表"
        ax.text(3.5, len(cal) + 3, title, ha='center', va='center', 
                fontsize=24, fontweight='bold')
        
        # 通常の訪問時間
        ax.text(0.2, len(cal) + 2.3, "【通常の訪問時間】", ha='left', va='center',
               fontsize=12, fontweight='bold')
        
        y_visit_info = len(cal) + 1.95
        ax.text(0.4, y_visit_info, f"・{visit1_config['weekday']}：{visit1_config['time']}", 
               ha='left', va='center', fontsize=11)
        
        if visit2_config:
            y_visit_info -= 0.3
            ax.text(0.4, y_visit_info, f"・{visit2_config['weekday']}：{visit2_config['time']}", 
                   ha='left', va='center', fontsize=11)
        
        if visit3_config:
            y_visit_info -= 0.3
            ax.text(0.4, y_visit_info, f"・{visit3_config['weekday']}：{visit3_config['time']}", 
                   ha='left', va='center', fontsize=11)
        
        振替_y_start = y_visit_info - 0.35
        
        # 振替予定
        if transfers_list:
            ax.text(0.2, 振替_y_start, "【振替予定】", ha='left', va='center',
                   fontsize=12, fontweight='bold', color='red')
            
            y_offset = 振替_y_start - 0.3
            for from_day, to_day, time in transfers_list:
                from_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, from_day)]
                to_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, to_day)]
                
                text = f"{month}月{from_day}日({from_weekday}) → {month}月{to_day}日({to_weekday}) {time}"
                ax.text(0.5, y_offset, text, ha='left', va='center',
                       fontsize=11, color='red', fontweight='bold')
                y_offset -= 0.25
        
        # 曜日ヘッダー
        weekdays = ['日', '月', '火', '水', '木', '金', '土']
        for i, day in enumerate(weekdays):
            color = 'red' if i == 0 else 'blue' if i == 6 else 'black'
            ax.text(i + 0.5, len(cal) + 0.3, day, ha='center', va='center',
                   fontsize=14, fontweight='bold', color=color)
        
        # カレンダーグリッド
        for week_num, week in enumerate(cal):
            y = len(cal) - week_num
            
            for day_num, day in enumerate(week):
                x = day_num
                
                # セルの枠線
                rect = plt.Rectangle((x, y-1), 1, 1, fill=False, 
                                    edgecolor='black', linewidth=1.2)
                ax.add_patch(rect)
                
                if day != 0:
                    # 日付の色
                    text_color = 'red' if day_num == 0 else 'blue' if day_num == 6 else 'black'
                    
                    # 日付を表示（左上）
                    ax.text(x + 0.1, y - 0.1, str(day), ha='left', va='top',
                           fontsize=13, fontweight='bold', color=text_color)
                    
                    # 訪問・振替・休みの情報
                    # 休みの日
                    if day in canceled_dates:
                        ax.text(x + 0.5, y - 0.8, "リハビリ\nお休み", ha='center', va='center',
                               fontsize=10, fontweight='bold', color='red')
                    
                    # 通常の訪問日
                    elif day in visit1_actual_days:
                        visit_text = f"{visit1_config['time']}\n{visit1_config['staff']}"
                        ax.text(x + 0.5, y - 0.8, visit_text, ha='center', va='center',
                               fontsize=10, fontweight='bold', color='green')
                    
                    elif day in visit2_actual_days:
                        visit_text = f"{visit2_config['time']}\n{visit2_config['staff']}"
                        ax.text(x + 0.5, y - 0.8, visit_text, ha='center', va='center',
                               fontsize=10, fontweight='bold', color='green')
                    
                    elif day in visit3_actual_days:
                        visit_text = f"{visit3_config['time']}\n{visit3_config['staff']}"
                        ax.text(x + 0.5, y - 0.8, visit_text, ha='center', va='center',
                               fontsize=10, fontweight='bold', color='green')
                    
                    # 振替訪問
                    if day in makeup_visits:
                        ax.text(x + 0.5, y - 0.8, f"振替訪問\n{makeup_visits[day]}", ha='center', va='center',
                               fontsize=9, fontweight='bold', color='red')
        
        # フッター
        ax.text(0.2, -0.5, "※ 急な変更が生じた場合は、事前にご連絡させていただきます。", 
               ha='left', va='center', fontsize=10)
        ax.text(0.2, -0.75, "※ ご不明な点がございましたら、お気軽にお問い合わせください。", 
               ha='left', va='center', fontsize=10)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    pdf_buffer.seek(0)
    return pdf_buffer, visit1_actual_days, visit2_actual_days, visit3_actual_days, canceled_dates

# PDF作成ボタン
st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("📥 PDFを作成", use_container_width=True, type="primary"):
    with st.spinner("📄 PDF作成中..."):
        # 定期訪問の設定を準備
        visit1_config = {
            'weekday': visit1_weekday,
            'time': visit1_time,
            'days': visit1_days,
            'staff': visit1_staff
        }
        
        # 週2回以上の場合
        if visit_count >= 2:
            visit2_config = {
                'weekday': visit2_weekday,
                'time': visit2_time,
                'days': visit2_days,
                'staff': visit2_staff
            }
        else:
            visit2_config = None
        
        # 週3回の場合
        if visit_count >= 3:
            visit3_config = {
                'weekday': visit3_weekday,
                'time': visit3_time,
                'days': visit3_days,
                'staff': visit3_staff
            }
        else:
            visit3_config = None
        
        pdf_buffer, visit1_actual, visit2_actual, visit3_actual, canceled_dates = create_pdf(
            year, month, st.session_state.transfers, visit1_config, visit2_config, visit3_config
        )
        
        st.success("✅ PDFが完成しました！")
        
        with st.expander("📋 作成内容を確認"):
            st.write(f"**{visit1_weekday}の訪問:** {visit1_actual}")
            if visit_count >= 2:
                st.write(f"**{visit2_weekday}の訪問:** {visit2_actual}")
            if visit_count >= 3:
                st.write(f"**{visit3_weekday}の訪問:** {visit3_actual}")
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
    2. **スタッフ名を登録** → 最大3名まで登録可能
    3. **訪問回数を選択** → 週1回、週2回、週3回から選択
    4. **定期訪問日を設定** → 曜日・時間・担当スタッフを選択
    5. **振替がなければスキップ** → 直接PDF作成へ
    6. **振替がある場合** → 振替情報を入力して追加
    7. **PDFを作成** → ダウンロード
    
    ### 👥 スタッフ設定
    - **スタッフ登録**: 最大3名まで登録可能
    - 各訪問日に担当スタッフを割り当て
    - PDFのカレンダーに担当者名が表示されます
    
    ### 📅 定期訪問設定
    - **訪問回数**: 週1回、週2回、週3回から選択
    - **週1回**: 訪問日1のみ設定
    - **週2回**: 訪問日1と2を設定
    - **週3回**: 訪問日1、2、3を設定
    - 各訪問日に担当スタッフを選択
    - デフォルト: 月曜日 11:20-12:00 / 水曜日 11:00-11:40
    - 訪問時間は40分/60分から選択
    
    ### 🔄 振替の設定方法
    - **振替元**: 定期訪問日から選択
    - **振替先**: 同じ週の平日から選択
    - **時間**: 開始時刻 + 訪問時間で自動計算
    
    ### 💡 ポイント
    - 週1回～週3回まで柔軟に対応
    - 担当スタッフがカレンダーに明記される
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
        💡 週1回～週3回の訪問に対応 | スタッフ名をカレンダーに表示
    </p>
    <p style='color: #95a5a6; font-size: 0.85rem; margin: 0.8rem 0 0 0;'>
        Created with ❤️ by Claude
    </p>
</div>
""", unsafe_allow_html=True)
