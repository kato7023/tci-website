# 株式会社TCI 公式Webサイト

`https://tci-pile.com` で公開している、株式会社TCIのコーポレートサイト。

静的なHTML・CSSのみで構成し、GitHub Pagesで配信している。ビルド工程もフレームワークも使わない。表示速度と、数年後でも壊れず手を入れられることを優先している。

## 構成

```text
index.html            サイト本体（CSSとJSON-LDを内包した1ページ構成）
CNAME                 独自ドメイン設定。GitHub Pagesが読む
robots.txt            クローラー向け
sitemap.xml           サイトマップ
assets/
  tci-logo.png            ロゴ（マーク＋TCi＋タグライン）ヒーロー用
  tci-logo-mark.png       ロゴマークのみ。ヘッダー用
  og-image.png            SNS共有用 1200x630
  apple-touch-icon.png    iOSホーム画面用 180x180
  favicon.ico             ファビコン 16/32/48
  source/
    tci-logo-master.png   ロゴ原本 1536x1024。サイトからは参照しない
tools/
  build-assets.py      原本から公開用画像一式を生成するスクリプト
```

## ローカルでの確認

`index.html` をブラウザーで直接開けば表示できるが、公開時と同じ絶対パスの挙動を確認するにはローカルサーバー経由が確実。

```bash
python -m http.server 8000
# http://localhost:8000 を開く
```

## ロゴ画像を作り直すとき

原本 `assets/source/tci-logo-master.png` を差し替えてから実行する。

```bash
python tools/build-assets.py
```

`Pillow` が必要（`pip install pillow`）。原本の背景はごく薄いグレーのグラデーションなので、スクリプト側で純白へ寄せてから余白を切り落としている。白背景のページ上で継ぎ目が出ないようにするため。

## 公開の仕組み

- GitHub Pages、`main` ブランチのルートから配信
- `main` へpushすると自動で反映される（数十秒〜数分）
- 独自ドメインは `CNAME` ファイルとGitHub側のCustom Domain設定の両方で成立している。**`CNAME` を消すとカスタムドメインが外れる**

### DNS

`tci-pile.com` のDNSはムームードメインで管理している。

| 種別 | ホスト | 値 |
|---|---|---|
| A | （空欄＝apex） | `185.199.108.153` / `185.199.109.153` / `185.199.110.153` / `185.199.111.153` |
| CNAME | `www` | `kato7023.github.io` |

**このドメインはGoogle Workspaceのメールでも使っている。** DNSを触るときにMXレコードと `google-site-verification` のTXTレコードを消すと会社メールが止まる。追加のみを行う。

## 掲載内容についての注意

このリポジトリーは公開されている。ここに置いてよいのは、公開Webサイトに必要な情報だけ。

- 開発中サービスの名称・仕様、アルゴリズム、設計ロジック、学習データ
- 協力会社名・開発会社名・パートナー名
- 開発費・送金・収益モデル・価格・売上計画
- 工法の詳細、認定取得計画、市場シェア目標
- 認証情報、`.env`、口座情報、契約書、個人情報

以上は**サイトにもリポジトリーにも置かない**。会社概要・事業領域・研究開発中である旨までを公開範囲とする。

社内向けの作業記録（`ChatLog/`・`Docs/`）は `.gitignore` で除外している。
