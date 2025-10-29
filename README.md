# リハビリ訪問予定表作成アプリ - デプロイ手順

## 📦 このリポジトリに含まれるファイル

- `app.py` - Streamlitアプリのメインコード
- `requirements.txt` - 必要なPythonライブラリ一覧
- `packages.txt` - 必要なシステムパッケージ（日本語フォント）
- `.gitignore` - Gitで無視するファイル一覧
- `README.md` - このファイル（デプロイ手順）

---

## 🚀 デプロイ手順（20分で完了）

### ステップ1: GitHubにリポジトリを作成

1. [GitHub](https://github.com/) にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名を入力（例: `rehab-calendar-app`）
4. 「Public」を選択（重要！）
5. 「Create repository」をクリック

### ステップ2: ファイルをアップロード

1. 作成したリポジトリのページで「uploading an existing file」をクリック
2. 以下の5つのファイルをドラッグ&ドロップ:
   - `app.py`
   - `requirements.txt`
   - `packages.txt`
   - `.gitignore`
   - `README.md`
3. 下の方にある「Commit changes」をクリック

### ステップ3: Streamlit Cloudでデプロイ

1. [Streamlit Cloud](https://share.streamlit.io/) にアクセス
2. 「Sign up」をクリック → 「Continue with GitHub」でログイン
3. 「New app」をクリック
4. 以下を選択:
   - **Repository**: あなたのリポジトリ名（例: `username/rehab-calendar-app`）
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. 「Deploy!」をクリック

### ステップ4: URLを共有

- デプロイが完了すると、URLが表示されます（例: `https://your-app.streamlit.app`）
- このURLをスタッフに共有すれば、誰でもアクセスできます！

---

## 🎯 完成後の使い方

### スタッフ側（利用者）
1. 共有されたURLをブラウザで開く
2. 年・月を選択
3. 振替があれば入力
4. 「PDFを作成」→「PDFをダウンロード」

### あなた側（管理者）
- 特に何もする必要なし
- アプリは24時間365日稼働
- 無料で使い続けられる

---

## 💡 よくある質問

**Q: お金はかかりますか？**  
A: 完全無料です。Streamlit Cloudは個人利用なら永久無料です。

**Q: リポジトリは公開（Public）にしないとダメですか？**  
A: はい、Streamlit Cloudの無料プランは公開リポジトリのみ対応です。ただし、URLを知っている人しかアクセスできないので問題ありません。

**Q: 後からコードを修正できますか？**  
A: できます！GitHubでファイルを編集すると、自動的にアプリも更新されます。

**Q: スマホからも使えますか？**  
A: 使えます！URLを開くだけで、スマホ・タブレットからも利用可能です。

**Q: 複数人が同時に使っても大丈夫？**  
A: 大丈夫です！各ユーザーが独立して操作できます。

---

## 🔧 トラブルシューティング

**デプロイがエラーになる場合:**
1. `requirements.txt` のファイル名が正しいか確認
2. `app.py` のファイル名が正しいか確認
3. リポジトリが「Public」になっているか確認

**アプリが動かない場合:**
1. Streamlit Cloudのログを確認
2. エラーメッセージを読む
3. 必要に応じてファイルを修正してGitHubに再アップロード

---

## 📞 サポート

問題が解決しない場合は、Claude（私）に相談してください！

---

作成者: Claude  
作成日: 2025年10月
