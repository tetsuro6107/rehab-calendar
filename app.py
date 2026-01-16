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

# モード選択のデフォルト値
if 'mode' not in st.session_state:
    st.session_state.mode = "通常モード"

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

# モード選択セクション
st.header("⚙️ モード選択")
st.markdown("""
<div style='background: linear-gradient(145deg, #fff3e0 0%, #ffffff 100%);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.06);
            margin: 2rem 0;
            border: 1px solid rgba(255, 152, 0, 0.2);'>
    <p style='color: #e65100; font-size: 0.95rem; font-weight: 600; margin: 0; text-align: center;'>
        💡 訪問のタイプを選択してください
    </p>
</div>
""", unsafe_allow_html=True)

mode = st.radio(
    "モードを選択",
    options=["通常モード", "特指示モード"],
    index=0,
    key="mode_select",
    horizontal=True,
    help="通常モード: 週1〜3回の定期訪問 | 特指示モード: 集中的な訪問（最大14日間）"
)

# モードの説明
if mode == "通常モード":
    st.info("📅 **通常モード**: 週1〜3回の定期訪問を設定します")
else:
    st.info("🏥 **特指示モード**: 特別訪問看護指示書に基づく集中的な訪問（最大14日間）を設定します")

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

# モードによって表示を切り替え
if mode == "通常モード":
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
    
# 特指示モードの設定
if mode == "特指示モード":
    # 特指示モード設定セクション
    st.header("🏥 特別訪問看護指示設定")
    st.markdown("""
    <div style='background: linear-gradient(145deg, #ffebee 0%, #ffffff 100%);
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.06);
                margin: 2rem 0;
                border: 1px solid rgba(244, 67, 54, 0.2);'>
        <p style='color: #c62828; font-size: 0.95rem; font-weight: 600; margin: 0; text-align: center;'>
            💡 特別訪問看護指示書に基づく集中的な訪問を設定します（最大14日間）
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 期間設定
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.15rem; margin-bottom:1rem;'>📆 訪問期間</p>", unsafe_allow_html=True)
    
    import calendar as cal_lib
    cal_lib.setfirstweekday(6)
    
    # その月の日付リストを作成
    max_day = cal_lib.monthrange(year, month)[1]
    day_options = list(range(1, max_day + 1))
    
    col_period1, col_period2 = st.columns(2)
    
    with col_period1:
        toku_start_day = st.selectbox(
            "開始日",
            options=day_options,
            index=0,
            format_func=lambda x: f"{x}日",
            key="toku_start_day"
        )
    
    with col_period2:
        # 終了日は開始日から最大14日後まで
        max_end_day = min(toku_start_day + 13, max_day)
        end_day_options = list(range(toku_start_day, max_end_day + 1))
        
        toku_end_day = st.selectbox(
            "終了日",
            options=end_day_options,
            index=min(13, len(end_day_options) - 1),  # デフォルト14日間
            format_func=lambda x: f"{x}日",
            key="toku_end_day"
        )
    
    # 期間の日数を計算
    toku_days_count = toku_end_day - toku_start_day + 1
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #ef5350 0%, #e57373 100%); 
                padding: 0.8rem 1.5rem; 
                border-radius: 12px; 
                text-align: center;
                margin: 1rem 0;'>
        <p style='color: white; font-size: 1.1rem; font-weight: 700; margin: 0;'>
            📅 {month}月{toku_start_day}日 〜 {month}月{toku_end_day}日（{toku_days_count}日間）
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if toku_days_count > 14:
        st.error("⚠️ 特別訪問看護指示期間は最大14日間です")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # カレンダー表示とチェックボックス
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.15rem; margin-bottom:1rem;'>📅 訪問日を選択</p>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: linear-gradient(145deg, #fff3e0 0%, #ffffff 100%);
                padding: 1.5rem;
                border-radius: 16px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                margin: 1rem 0;
                border: 1px solid rgba(255, 152, 0, 0.3);'>
        <p style='color: #e65100; font-size: 0.9rem; font-weight: 600; margin: 0; text-align: center;'>
            💡 訪問する日にチェックを入れてください（平日のみ選択可能）
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 期間内の日付リスト（平日のみ）
    import datetime
    period_days = []
    weekday_names = ['月', '火', '水', '木', '金', '土', '日']
    
    for day in range(toku_start_day, toku_end_day + 1):
        date_obj = datetime.date(year, month, day)
        weekday = date_obj.weekday()  # 0=月曜, 6=日曜
        if weekday < 5:  # 平日（月〜金）のみ
            period_days.append({
                'day': day,
                'weekday': weekday,
                'weekday_name': weekday_names[weekday]
            })
    
    # session_stateで選択された日付を管理
    if 'toku_selected_days' not in st.session_state:
        st.session_state.toku_selected_days = {}
    
    # カレンダー形式で表示（7列）
    st.markdown("<div style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # 1週間ごとに表示
    for week_start in range(0, len(period_days), 5):
        week_days = period_days[week_start:week_start + 5]
        cols = st.columns(5)
        
        for i, day_info in enumerate(week_days):
            with cols[i]:
                day = day_info['day']
                weekday_name = day_info['weekday_name']
                
                # チェックボックス
                is_checked = st.checkbox(
                    f"{day}日 ({weekday_name})",
                    value=day in st.session_state.toku_selected_days,
                    key=f"toku_day_{day}"
                )
                
                # 選択状態を更新
                if is_checked and day not in st.session_state.toku_selected_days:
                    # 新しく選択された
                    st.session_state.toku_selected_days[day] = {
                        'time': '11:00-11:40',
                        'staff': staff_list[0] if staff_list else '未設定'
                    }
                elif not is_checked and day in st.session_state.toku_selected_days:
                    # 選択解除された
                    del st.session_state.toku_selected_days[day]
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 選択された日付の数を表示
    selected_count = len(st.session_state.toku_selected_days)
    if selected_count > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #ef5350 0%, #e57373 100%); 
                    padding: 0.8rem 1.5rem; 
                    border-radius: 12px; 
                    text-align: center;
                    margin: 1rem 0;'>
            <p style='color: white; font-size: 1.1rem; font-weight: 700; margin: 0;'>
                ✅ 選択された訪問日: {selected_count}日間
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 各訪問日の時間・スタッフ設定
        st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.15rem; margin:1.5rem 0 1rem 0;'>⏰ 各訪問日の設定</p>", unsafe_allow_html=True)
        
        for day in sorted(st.session_state.toku_selected_days.keys()):
            date_obj = datetime.date(year, month, day)
            weekday_name = weekday_names[date_obj.weekday()]
            
            st.markdown(f"<p style='font-weight:700; color:#2c3e50; font-size:1.05rem; margin:1rem 0 0.5rem 0;'>📌 {month}月{day}日 ({weekday_name})</p>", unsafe_allow_html=True)
            
            col_time, col_staff = st.columns([2, 1])
            
            with col_time:
                time_col1, time_col2, time_col3 = st.columns(3)
                
                with time_col1:
                    start_hour = st.selectbox(
                        "開始時",
                        options=list(range(9, 18)),
                        index=2,  # デフォルト: 11時
                        format_func=lambda x: f"{x}時",
                        key=f"toku_hour_{day}"
                    )
                
                with time_col2:
                    start_min = st.selectbox(
                        "開始分",
                        options=list(range(0, 60, 5)),
                        index=0,  # デフォルト: 00分
                        format_func=lambda x: f"{x:02d}分",
                        key=f"toku_min_{day}"
                    )
                
                with time_col3:
                    duration = st.selectbox(
                        "訪問時間",
                        options=[40, 60],
                        index=0,  # デフォルト: 40分
                        format_func=lambda x: f"{x}分",
                        key=f"toku_duration_{day}"
                    )
                
                # 終了時刻計算
                end_total = start_hour * 60 + start_min + duration
                end_hour = end_total // 60
                end_min = end_total % 60
                time_str = f"{start_hour}:{start_min:02d}-{end_hour}:{end_min:02d}"
                
                # session_stateに保存
                st.session_state.toku_selected_days[day]['time'] = time_str
            
            with col_staff:
                if staff_list:
                    selected_staff = st.selectbox(
                        "担当スタッフ",
                        options=staff_list,
                        index=0,
                        key=f"toku_staff_{day}"
                    )
                    st.session_state.toku_selected_days[day]['staff'] = selected_staff
                else:
                    st.info("💡 スタッフ未設定")
                    st.session_state.toku_selected_days[day]['staff'] = "未設定"
            
            # 設定内容の表示
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ef5350 0%, #e57373 100%); 
                        padding: 0.6rem 1.2rem; 
                        border-radius: 10px; 
                        margin: 0.5rem 0 0.5rem 0;'>
                <p style='color: white; font-size: 0.95rem; font-weight: 600; margin: 0;'>
                    🕐 {time_str} | 👤 {st.session_state.toku_selected_days[day]['staff']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 1.5rem; margin: 1rem 0 0.5rem 0;'>
            <p style='color: #95a5a6; font-size: 1rem; font-weight: 600; margin: 0;'>
                👆 訪問日を選択してください
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 通常モード用のダミー値を設定
    visit_count = 0
    visit1_weekday = None
    visit1_time = None
    visit1_days = []
    visit1_staff = None
    visit2_weekday = None
    visit2_time = None
    visit2_days = []
    visit2_staff = None
    visit3_weekday = None
    visit3_time = None
    visit3_days = []
    visit3_staff = None

st.markdown("---")

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

# 通常モードの場合のみ訪問日を計算
if mode == "通常モード":
    # 定期訪問日1の日付を取得
    visit1_days = get_visit_days(year, month, visit1_weekday)
    
    # 訪問回数に応じて訪問日を追加
    if visit_count >= 2:
        visit2_days = get_visit_days(year, month, visit2_weekday)
    else:
        visit2_days = []
    
    # 週3回の場合は訪問日3も追加
    if visit_count >= 3:
        visit3_days = get_visit_days(year, month, visit3_weekday)
    else:
        visit3_days = []
else:
    # 特指示モードの場合はダミー値
    visit1_days = []
    visit2_days = []
    visit3_days = []

# キャンセル・振替設定セクション（通常モードのみ）
if mode == "通常モード":
    st.header("📅 キャンセル・振替設定")

    # その月のカレンダーを表示
    st.markdown("<p style='font-weight:700; color:#2c3e50; font-size:1.1rem; margin:1.5rem 0 1rem 0;'>📆 今月のカレンダー</p>", unsafe_allow_html=True)

    import calendar as cal_module
    cal_module.setfirstweekday(6)  # 日曜始まり
    month_calendar = cal_module.monthcalendar(year, month)

    # カレンダーのヘッダー
    calendar_header = "| 日 | 月 | 火 | 水 | 木 | 金 | 土 |"
    calendar_separator = "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"

    # カレンダーの行を生成
    calendar_rows = []
    for week in month_calendar:
        row = "|"
        for i, day in enumerate(week):
            if day == 0:
                row += "   |"
            else:
                # 訪問日をマーク
                is_visit_day = False
                if day in visit1_days:
                    is_visit_day = True
                elif visit_count >= 2 and day in visit2_days:
                    is_visit_day = True
                elif visit_count >= 3 and day in visit3_days:
                    is_visit_day = True
                
                if is_visit_day:
                    row += f" **{day}** 🏥|"
                elif i == 0:  # 日曜日
                    row += f" <span style='color:red'>{day}</span>|"
                elif i == 6:  # 土曜日
                    row += f" <span style='color:blue'>{day}</span>|"
                else:
                    row += f" {day}|"
        calendar_rows.append(row)

    calendar_md = calendar_header + "\n" + calendar_separator + "\n" + "\n".join(calendar_rows)

    st.markdown(calendar_md, unsafe_allow_html=True)
    st.markdown("<p style='color: #7f8c8d; font-size: 0.85rem; margin: 0.5rem 0 1.5rem 0; text-align: center;'>🏥 = 定期訪問日</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 説明カード
    st.markdown("""
    <div style='background: linear-gradient(145deg, #e8f5e9 0%, #ffffff 100%);
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 8px 30px rgba(0,0,0,0.06);
                margin: 2rem 0;
                border: 1px solid rgba(76, 175, 80, 0.2);'>
        <p style='color: #2e7d32; font-size: 0.95rem; font-weight: 600; margin: 0; text-align: center;'>
            💡 振替先で「キャンセル」を選ぶと振替なしでお休みになります
        </p>
    </div>
    """, unsafe_allow_html=True)

    # transfer_optionsを計算
    if visit_count >= 2:
        transfer_options = sorted(visit1_days + visit2_days)
    else:
        transfer_options = sorted(visit1_days)

    if visit_count >= 3:
        transfer_options = sorted(visit1_days + visit2_days + visit3_days)

    # グリッドレイアウト
    col1, col2 = st.columns([1, 1])

    # is_cancel変数を初期化
    is_cancel = False
    time_valid = True  # 初期値を設定
    transfer_time = ""  # 初期値を設定

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
            # 同じ週の平日を取得
            weekday_options = get_weekdays_in_same_week(year, month, transfer_from)
            
            # 表示用のオプションリストを作成（キャンセルを含む）
            display_options = ["❌ キャンセル（振替なし）"]
            for day in weekday_options:
                weekday_name = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, day)]
                display_options.append(f"{day}日 ({weekday_name})")
            
            # セレクトボックスで表示
            selected_option = st.selectbox(
                "振替先を選択",
                options=display_options,
                key="transfer_to_select",
                label_visibility="collapsed"
            )
            
            # 選択された値に応じて処理
            if selected_option == "❌ キャンセル（振替なし）":
                transfer_to = None
                is_cancel = True
            else:
                # 日付部分を抽出（例: "13日 (火)" → 13）
                day_str = selected_option.split("日")[0]
                transfer_to = int(day_str)
                is_cancel = False
        else:
            st.info("👆 まず振替元を選択してください")
            transfer_to = None
            is_cancel = False
    
    # 時間設定（キャンセルでない場合のみ表示）
    if transfer_from and not is_cancel:
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
    else:
        # キャンセルの場合：時間設定不要
        transfer_time = ""
        time_valid = True
        if transfer_from and is_cancel:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("ℹ️ キャンセルの場合は時間設定は不要です")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ボタン
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        button_label = "➕ 追加"
        if st.button(button_label, use_container_width=True, type="primary"):
            if transfer_from is None:
                st.error("❌ 振替元（訪問日）を選択してください")
            elif is_cancel:
                # キャンセルの場合は即座に追加
                if any(t[0] == transfer_from for t in st.session_state.transfers):
                    st.warning("⚠️ この日付は既に登録されています")
                else:
                    st.session_state.transfers.append((transfer_from, None, ""))
                    st.success(f"✅ {transfer_from}日をキャンセルしました")
                    st.rerun()
            elif transfer_to is None:
                st.error("❌ 振替先を選択してください")
            elif not time_valid:
                st.error("❌ 終了時刻が定時を超えています")
            else:
                # 振替の追加
                if any(t[0] == transfer_from for t in st.session_state.transfers):
                    st.warning("⚠️ この日付は既に登録されています")
                else:
                    st.session_state.transfers.append((transfer_from, transfer_to, transfer_time))
                    st.success(f"✅ {transfer_from}日 → {transfer_to}日を追加しました")
                    st.rerun()
    
    with col_btn2:
        if st.button("🗑️ 全てクリア", use_container_width=True):
            st.session_state.transfers = []
            st.rerun()
    
    # 登録された振替/キャンセル
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.transfers:
        st.markdown(f"<p style='font-weight:700; color:#2c3e50; font-size:1.1rem; margin-bottom:1rem;'>📋 登録された内容</p>", unsafe_allow_html=True)
        for i, (from_day, to_day, time) in enumerate(st.session_state.transfers, 1):
            from_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, from_day)]
            
            col_info, col_del = st.columns([8.5, 1.5])
            with col_info:
                if to_day is not None:
                    # 振替あり
                    to_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, to_day)]
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
                else:
                    # キャンセルのみ
                    st.markdown(f"""
                    <div style='background: white;
                                padding: 1.2rem 1.5rem; 
                                border-radius: 14px; 
                                border-left: 6px solid #e74c3c;
                                margin-bottom: 0.8rem;
                                box-shadow: 0 3px 10px rgba(0,0,0,0.08);
                                transition: all 0.3s ease;'>
                        <span style='font-size: 1.1rem; font-weight: 800; color: #2c3e50;'>
                            {i}. {from_day}日({from_weekday}) <span style='color: #e74c3c; font-weight: 900;'>❌ キャンセル</span>
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{i}", help="削除", use_container_width=True):
                    st.session_state.transfers.pop(i-1)
                    st.rerun()
    else:
        st.markdown(f"<p style='color: #95a5a6; font-style: italic; text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 12px;'>登録なし</p>", unsafe_allow_html=True)
    
    # 通常モードのみここまで
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
    # to_dayがNoneでない場合のみ振替訪問として追加（キャンセルのみは除外）
    makeup_visits = {t[1]: t[2] for t in transfers_list if t[1] is not None}
    
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
                
                if to_day is not None:
                    # 振替あり
                    to_weekday = ['月','火','水','木','金','土','日'][calendar.weekday(year, month, to_day)]
                    text = f"{month}月{from_day}日({from_weekday}) → {month}月{to_day}日({to_weekday}) {time}"
                else:
                    # キャンセルのみ
                    text = f"{month}月{from_day}日({from_weekday}) キャンセル"
                
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
                    ax.text(x + 0.05, y - 0.1, str(day), ha='left', va='top',
                           fontsize=13, fontweight='bold', color=text_color)
                    
                    # 訪問・振替・休みの情報
                    # 休みの日
                    if day in canceled_dates:
                        ax.text(x + 0.5, y - 0.5, "リハビリ\nお休み", ha='center', va='center',
                               fontsize=12, fontweight='bold', color='red')
                    
                    # 通常の訪問日
                    elif day in visit1_actual_days:
                        visit_text = f"{visit1_config['time']}\n{visit1_config['staff']}"
                        ax.text(x + 0.5, y - 0.55, visit_text, ha='center', va='center',
                               fontsize=12, fontweight='bold', color='green')
                    
                    elif day in visit2_actual_days:
                        visit_text = f"{visit2_config['time']}\n{visit2_config['staff']}"
                        ax.text(x + 0.5, y - 0.55, visit_text, ha='center', va='center',
                               fontsize=12, fontweight='bold', color='green')
                    
                    elif day in visit3_actual_days:
                        visit_text = f"{visit3_config['time']}\n{visit3_config['staff']}"
                        ax.text(x + 0.5, y - 0.55, visit_text, ha='center', va='center',
                               fontsize=12, fontweight='bold', color='green')
                    
                    # 振替訪問
                    if day in makeup_visits:
                        ax.text(x + 0.5, y - 0.5, f"振替訪問\n{makeup_visits[day]}", ha='center', va='center',
                               fontsize=11, fontweight='bold', color='red')
        
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

# 特指示モード用PDF作成関数
def create_toku_pdf(year, month, start_day, end_day, selected_days_data):
    """
    特別訪問看護指示書用のPDF作成
    selected_days_data = {
        10: {'time': '11:00-11:40', 'staff': '樫下'},
        11: {'time': '14:00-14:40', 'staff': '田中'},
        ...
    }
    """
    calendar.setfirstweekday(6)  # 日曜始まり
    cal = calendar.monthcalendar(year, month)
    
    # 訪問日のリスト
    visit_days = sorted(selected_days_data.keys())
    
    pdf_buffer = io.BytesIO()
    
    with PdfPages(pdf_buffer) as pdf:
        fig, ax = plt.subplots(figsize=(11.7, 8.3))
        ax.set_xlim(0, 7)
        ax.set_ylim(0, len(cal) + 3.5)
        ax.axis('off')
        
        # タイトル
        title = f"{year}年{month}月 特別訪問看護指示書 訪問予定表"
        ax.text(3.5, len(cal) + 3, title, ha='center', va='center', 
                fontsize=22, fontweight='bold', color='red')
        
        # 特指示期間の表示
        days_count = end_day - start_day + 1
        ax.text(0.2, len(cal) + 2.3, f"【特別訪問看護指示期間】", ha='left', va='center',
               fontsize=12, fontweight='bold', color='red')
        ax.text(0.4, len(cal) + 1.95, f"{month}月{start_day}日 〜 {month}月{end_day}日（{days_count}日間）", 
               ha='left', va='center', fontsize=11, color='red')
        
        # 訪問内容の表示
        y_visit_info = len(cal) + 1.65
        ax.text(0.2, y_visit_info, "【訪問内容】", ha='left', va='center',
               fontsize=12, fontweight='bold', color='red')
        
        y_visit_info -= 0.3
        
        import datetime
        weekday_names = ['月', '火', '水', '木', '金', '土', '日']
        
        for day in visit_days:
            date_obj = datetime.date(year, month, day)
            weekday_name = weekday_names[date_obj.weekday()]
            info = selected_days_data[day]
            
            ax.text(0.4, y_visit_info, f"・{month}/{day}({weekday_name})：{info['time']}（{info['staff']}）", 
                   ha='left', va='center', fontsize=11, color='red')
            y_visit_info -= 0.25
        
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
                    ax.text(x + 0.05, y - 0.1, str(day), ha='left', va='top',
                           fontsize=13, fontweight='bold', color=text_color)
                    
                    # 特指示期間内の訪問日
                    if day in selected_days_data:
                        info = selected_days_data[day]
                        visit_text = f"{info['time']}\n{info['staff']}"
                        ax.text(x + 0.5, y - 0.55, visit_text, ha='center', va='center',
                               fontsize=12, fontweight='bold', color='red')
        
        # フッター
        ax.text(0.2, -0.5, "※ 特別訪問看護指示書に基づく訪問です。", 
               ha='left', va='center', fontsize=10, color='red', fontweight='bold')
        ax.text(0.2, -0.75, "※ 急な変更が生じた場合は、事前にご連絡させていただきます。", 
               ha='left', va='center', fontsize=10)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    pdf_buffer.seek(0)
    return pdf_buffer, visit_days

# PDF作成ボタン
st.markdown("<br>", unsafe_allow_html=True)
if st.button("📥 PDFを作成", use_container_width=True, type="primary"):
    with st.spinner("📄 PDF作成中..."):
        if mode == "通常モード":
            # 通常モードのPDF作成
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
                    st.write(f"**振替日:** {[t[1] for t in st.session_state.transfers if t[1] is not None]}")
            
            st.download_button(
                label="📥 PDFをダウンロード",
                data=pdf_buffer,
                file_name=f"{year}年{month}月_リハビリ訪問予定表.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        else:
            # 特指示モードのPDF作成
            if len(st.session_state.toku_selected_days) == 0:
                st.error("⚠️ 訪問日が選択されていません")
            else:
                # 選択された日付と設定を取得
                selected_days_data = st.session_state.toku_selected_days
                
                pdf_buffer, visit_days = create_toku_pdf(
                    year, month, toku_start_day, toku_end_day, selected_days_data
                )
                
                st.success("✅ PDFが完成しました！")
                
                with st.expander("📋 作成内容を確認"):
                    st.write(f"**期間:** {month}月{toku_start_day}日 〜 {month}月{toku_end_day}日")
                    st.write(f"**訪問日数:** {len(selected_days_data)}日間")
                    st.write(f"**訪問日:** {sorted(visit_days)}")
                    
                    import datetime
                    weekday_names = ['月', '火', '水', '木', '金', '土', '日']
                    for day in sorted(selected_days_data.keys()):
                        date_obj = datetime.date(year, month, day)
                        weekday_name = weekday_names[date_obj.weekday()]
                        info = selected_days_data[day]
                        st.write(f"**{month}/{day}({weekday_name}):** {info['time']} - {info['staff']}")
                
                st.download_button(
                    label="📥 PDFをダウンロード",
                    data=pdf_buffer,
                    file_name=f"{year}年{month}月_特別訪問看護指示書_訪問予定表.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

st.markdown("---")

# 使い方
with st.expander("💡 使い方ガイド"):
    st.markdown("""
    ### 📝 基本的な流れ
    1. **年月を選択** → カレンダー設定
    2. **モードを選択** → 通常モード or 特指示モード
    3. **スタッフ名を登録** → 最大3名まで登録可能
    4. **訪問設定** → モードに応じて設定
    5. **キャンセル・振替を追加** → 通常モードのみ
    6. **PDFを作成** → ダウンロード
    
    ### ⚙️ モード選択
    **通常モード:**
    - 週1〜3回の定期訪問
    - キャンセル・振替機能あり
    - 毎月のカレンダー作成に最適
    
    **特指示モード:**
    - 特別訪問看護指示書に基づく訪問
    - 最大14日間の集中的な訪問
    - 週1〜5回まで柔軟に設定可能
    - 各訪問日の曜日・時間・スタッフを個別設定
    - キャンセル・振替機能なし
    
    ### 👥 スタッフ設定
    - **スタッフ登録**: 最大3名まで登録可能
    - 各訪問日に担当スタッフを割り当て
    - PDFのカレンダーに担当者名が表示されます
    
    ### 📅 通常モード設定
    - **訪問回数**: 週1回、週2回、週3回から選択
    - **週1回**: 訪問日1のみ設定
    - **週2回**: 訪問日1と2を設定
    - **週3回**: 訪問日1、2、3を設定
    - 各訪問日に担当スタッフを選択
    - デフォルト: 月曜日 11:20-12:00 / 水曜日 11:00-11:40
    - 訪問時間は40分/60分から選択
    
    ### 🏥 特指示モード設定
    - **期間設定**: 開始日と終了日を選択（最大14日間）
    - **訪問日選択**: カレンダーから訪問する日をチェック（平日のみ）
    - **各訪問日の設定**:
      - チェックした日付ごとに個別設定
      - 時間: 開始時刻と訪問時間を設定
      - スタッフ: 担当スタッフを選択
    - **柔軟な設定**: 週によって回数が変わってもOK
      - 例: 1週目は4回、2週目は2回など
    - **完全カスタマイズ**: 必要な日だけ選択できる
    
    ### 🔄 キャンセル・振替設定（通常モードのみ）
    **振替先で選択:**
    - **❌ キャンセル（振替なし）**: その日は休みになる
    - **平日を選択**: 別の日に振り替える（時間も設定）
    
    **使い分け:**
    - 単純に休みたい → 振替先で「キャンセル」を選択
    - 別の日に移したい → 振替先で平日を選択 + 時間設定
    
    ### 💡 ポイント
    - モード切り替えで通常訪問と特指示訪問に対応
    - カレンダー表示で日付を確認しながら設定
    - 特指示モードは日付単位で完全にカスタマイズ可能
    - 担当スタッフがカレンダーに明記される
    - 終了時刻は自動計算されるので入力ミスなし
    """)

# フッター
st.markdown("""
<div style='text-align: center; margin-top: 3rem; padding: 2rem 0; 
            background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%);
            border-radius: 16px;'>
    <p style='color: #7f8c8d; font-size: 0.95rem; font-weight: 600; margin: 0;'>
        💡 通常モード：週1〜3回の定期訪問 | 特指示モード：日付選択で柔軟な訪問計画（最大14日間）
    </p>
    <p style='color: #95a5a6; font-size: 0.85rem; margin: 0.8rem 0 0 0;'>
        Created with ❤️ by Claude
    </p>
</div>
""", unsafe_allow_html=True)
