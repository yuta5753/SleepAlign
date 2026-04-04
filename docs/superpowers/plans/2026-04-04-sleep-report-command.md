# `/sleep-report` コマンド 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GPTsの「睡眠解析・改善提案レポート」アシスタントを、Claude Codeのスラッシュコマンド `/sleep-report` として再構築する。

**Architecture:** カスタムコマンド（`~/.claude/commands/sleep-report.md`）がメインのプロンプトファイル。HTMLテンプレート3つ（メイン1枚目・2枚目・詳細版）をプロジェクト内に配置し、コマンド実行時にClaudeがテンプレートを読み込み、解析データで埋めてHTML出力する。

**Tech Stack:** Claude Code custom commands (markdown prompt), HTML/CSS (A4印刷対応), SVG (チャート類)

**Spec:** `docs/superpowers/specs/2026-04-04-sleep-report-command-design.md`

---

## ファイル構成

```
/Users/tsujiyuuta/SleepAlign/
  templates/
    sleep-report-main-page1.html   ← メインレポート1枚目テンプレート
    sleep-report-main-page2.html   ← メインレポート2枚目テンプレート
    sleep-report-detail.html       ← 詳細版テンプレート

~/.claude/commands/
  sleep-report.md                  ← スラッシュコマンド本体
```

出力先（実行時に自動作成）：
```
~/Desktop/claude-outputs/nemunemu/sleep-report/YYYYMMDD_レポート/
  sleep-report-main.html
  sleep-report-detail.html
```

---

## Task 1: プロジェクト構造のセットアップ

**Files:**
- Create: `templates/` ディレクトリ

- [ ] **Step 1: テンプレートディレクトリを作成**

```bash
mkdir -p /Users/tsujiyuuta/SleepAlign/templates
```

- [ ] **Step 2: .gitignore に出力先と一時ファイルを追加**

Create: `/Users/tsujiyuuta/SleepAlign/.gitignore`

```
.superpowers/
*.pdf
```

- [ ] **Step 3: コミット**

```bash
cd /Users/tsujiyuuta/SleepAlign
git init
git add .gitignore
git commit -m "chore: initialize project structure with gitignore"
```

---

## Task 2: メインレポート1枚目 HTMLテンプレート

承認済みデザイン（案C: ダッシュボード型＋★評価＋2カラム融合）をベースに、プレースホルダー付きテンプレートを作成する。

**Files:**
- Create: `templates/sleep-report-main-page1.html`

- [ ] **Step 1: テンプレートHTMLを作成**

`/Users/tsujiyuuta/SleepAlign/templates/sleep-report-main-page1.html` に以下を書く。
プレースホルダーは `{{PLACEHOLDER_NAME}}` 形式。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>睡眠解析レポート</title>
<style>
  @page { size: A4; margin: 15mm 12mm; }
  @media print {
    body { background: white; padding: 0; }
    .page { box-shadow: none; border-radius: 0; }
  }
  body {
    font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'Meiryo', sans-serif;
    background: #e8eaed;
    display: flex;
    justify-content: center;
    padding: 20px;
    margin: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .page {
    width: 595px;
    min-height: 842px;
    background: white;
    padding: 28px 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    box-sizing: border-box;
  }

  /* Header */
  .header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding-bottom:10px; border-bottom:3px solid #2c5f8a; }
  .header-title { font-size:20px; font-weight:bold; color:#2c5f8a; }
  .header-sub { font-size:9px; color:#aaa; letter-spacing:1px; }
  .header-right { text-align:right; font-size:10px; color:#666; line-height:1.6; }

  /* Score cards */
  .score-row { display:flex; gap:10px; margin-bottom:14px; }
  .score-card { flex:1; border-radius:8px; padding:12px 10px; text-align:center; }
  .score-card.blue { background:#e8f4f8; }
  .score-card.orange { background:#fff3e0; }
  .score-card.green { background:#e8f5e9; }
  .score-label { font-size:10px; color:#666; margin-bottom:2px; }
  .score-value { font-size:30px; font-weight:bold; }
  .score-card.blue .score-value { color:#2c5f8a; }
  .score-card.orange .score-value { color:#e67e22; font-size:20px; }
  .score-card.green .score-value { color:#27ae60; font-size:20px; }
  .score-unit { font-size:9px; color:#999; }

  /* Section title */
  .section-title { font-size:12px; font-weight:bold; color:#2c5f8a; margin:12px 0 6px; padding-left:8px; border-left:3px solid #2c5f8a; }

  /* Top grid: summary + balance */
  .top-grid { display:flex; gap:10px; margin-bottom:12px; }
  .summary-box, .balance-box { flex:1; background:#f5f7fa; border-radius:8px; padding:10px; }
  .metric-row { display:flex; justify-content:space-between; align-items:center; padding:4px 0; border-bottom:1px solid #eee; font-size:11px; }
  .metric-row:last-child { border:none; }
  .metric-label { color:#555; }
  .metric-value { font-weight:bold; color:#2c5f8a; }
  .metric-ideal { font-size:9px; color:#aaa; margin-left:4px; }
  .balance-row { display:flex; justify-content:space-between; align-items:center; padding:4px 0; border-bottom:1px solid #eee; font-size:11px; }
  .balance-row:last-child { border:none; }
  .balance-stars { color:#2c5f8a; font-size:13px; letter-spacing:1px; }
  .balance-comment { font-size:9px; color:#999; }

  /* Mid grid: direction + awakening + jetlag */
  .mid-grid { display:flex; gap:8px; margin-bottom:12px; }
  .mid-card { flex:1; background:#f5f7fa; border-radius:8px; padding:10px; }
  .mid-card-title { font-size:10px; font-weight:bold; color:#2c5f8a; margin-bottom:4px; }
  .bar-wrap { margin-bottom:4px; }
  .bar-label { display:flex; justify-content:space-between; font-size:9px; color:#666; margin-bottom:2px; }
  .bar-bg { height:10px; background:#e0e7ef; border-radius:3px; }
  .bar-fill { height:100%; border-radius:3px; }
  .jetlag-highlight { display:flex; align-items:center; gap:8px; }
  .jetlag-value { font-size:24px; font-weight:bold; color:#e67e22; line-height:1; }
  .jetlag-unit { font-size:10px; color:#e67e22; }
  .jetlag-text { font-size:9px; color:#666; line-height:1.4; }
  .direction-legend { font-size:9px; line-height:1.7; }
  .direction-legend span { display:inline-block; width:8px; height:8px; border-radius:2px; margin-right:3px; vertical-align:middle; }

  /* Two column: PSS + Habit */
  .two-col { display:flex; gap:10px; margin-bottom:12px; }
  .col { flex:1; }
  .mini-table { width:100%; font-size:10px; border-collapse:collapse; }
  .mini-table th { background:#2c5f8a; color:white; padding:4px 6px; text-align:left; font-weight:normal; font-size:9px; }
  .mini-table td { padding:4px 6px; border-bottom:1px solid #eee; }
  .eval-badge { display:inline-block; padding:1px 6px; border-radius:10px; font-size:9px; }
  .eval-good { background:#e8f5e9; color:#27ae60; }
  .eval-warn { background:#fff3e0; color:#e67e22; }
  .eval-info { background:#e8f4f8; color:#2c5f8a; }

  /* Proposal */
  .proposal-box { background:#f8fafe; border-radius:8px; padding:12px; border-left:4px solid #2c5f8a; margin-bottom:12px; }
  .proposal-title { font-size:11px; font-weight:bold; color:#2c5f8a; margin-bottom:8px; }
  .proposal-item { display:flex; gap:6px; align-items:start; margin-bottom:6px; font-size:11px; line-height:1.5; }
  .proposal-num { background:#2c5f8a; color:white; border-radius:50%; width:18px; height:18px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:10px; font-weight:bold; }
  .proposal-sub { font-size:9px; color:#999; margin-top:1px; }

  /* Product recommendation */
  .product-row { display:flex; gap:10px; }
  .product-card { flex:1; border:1px solid #e0e7ef; border-radius:8px; padding:10px; text-align:center; }
  .product-title { font-size:9px; color:#2c5f8a; font-weight:bold; margin-bottom:4px; }
  .product-image { background:#f5f7fa; border-radius:6px; height:40px; display:flex; align-items:center; justify-content:center; font-size:9px; color:#aaa; margin-bottom:4px; }
  .product-name { font-size:10px; color:#555; }
  .product-comment { font-size:9px; color:#999; }
</style>
</head>
<body>
<div class="page">
  <!-- ヘッダー -->
  <div class="header">
    <div>
      <div class="header-title">睡眠解析レポート</div>
      <div class="header-sub">SLEEP ANALYSIS REPORT</div>
    </div>
    <div class="header-right">
      ねむりの相談所<br>
      測定期間：{{PERIOD_START}} 〜 {{PERIOD_END}}（{{PERIOD_DAYS}}日間）
    </div>
  </div>

  <!-- スコアカード -->
  <div class="score-row">
    <div class="score-card blue">
      <div class="score-label">総合スコア</div>
      <div class="score-value">{{TOTAL_SCORE}}</div>
      <div class="score-unit">/100</div>
    </div>
    <div class="score-card orange">
      <div class="score-label">ストレスリスク</div>
      <div class="score-value">{{STRESS_RISK}}</div>
      <div class="score-unit">PSS: {{STRESS_LEVEL}}</div>
    </div>
    <div class="score-card green">
      <div class="score-label">生活習慣</div>
      <div class="score-value">{{HABIT_GRADE}}</div>
      <div class="score-unit">{{HABIT_COMMENT}}</div>
    </div>
  </div>

  <!-- 睡眠サマリー ＆ バランス評価 -->
  <div class="section-title">睡眠サマリー ＆ バランス評価</div>
  <div class="top-grid">
    <div class="summary-box">
      <div class="metric-row">
        <span class="metric-label">平均睡眠時間</span>
        <span><span class="metric-value">{{AVG_SLEEP_TIME}}</span><span class="metric-ideal">理想 {{IDEAL_SLEEP_TIME}}</span></span>
      </div>
      <div class="metric-row">
        <span class="metric-label">寝つき平均</span>
        <span><span class="metric-value">{{AVG_ONSET_TIME}}</span><span class="metric-ideal">理想 10分</span></span>
      </div>
      <div class="metric-row">
        <span class="metric-label">寝返り回数</span>
        <span><span class="metric-value">{{AVG_TURNOVER}}</span><span class="metric-ideal">適正 20〜30</span></span>
      </div>
      <div class="metric-row">
        <span class="metric-label">活動量平均</span>
        <span><span class="metric-value">{{AVG_ACTIVITY}}</span><span class="metric-ideal">理想 3以上</span></span>
      </div>
    </div>
    <div class="balance-box">
      {{BALANCE_ROWS}}
    </div>
  </div>

  <!-- 中段3列: 体の向き / 覚醒回数 / ジェットラグ -->
  <div class="mid-grid">
    <div class="mid-card">
      <div class="mid-card-title">体の向き</div>
      <div style="display:flex; align-items:center; gap:6px;">
        {{DIRECTION_SVG}}
        <div class="direction-legend">
          {{DIRECTION_LEGEND}}
        </div>
      </div>
    </div>
    <div class="mid-card">
      <div class="mid-card-title">覚醒回数</div>
      {{AWAKENING_BARS}}
    </div>
    <div class="mid-card" style="background:#fff8f0; border:1px solid #fce4c0;">
      <div class="mid-card-title" style="color:#e67e22;">ソーシャルジェットラグ</div>
      <div class="jetlag-highlight">
        <div>
          <div class="jetlag-value">{{JETLAG_VALUE}}</div>
          <div class="jetlag-unit">{{JETLAG_UNIT}}</div>
        </div>
        <div class="jetlag-text">{{JETLAG_COMMENT}}</div>
      </div>
    </div>
  </div>

  <!-- PSS ＋ 生活習慣 2カラム -->
  <div class="two-col">
    <div class="col">
      <div class="section-title">ストレス（PSS）</div>
      <table class="mini-table">
        <tr><th>指標</th><th>結果</th></tr>
        {{PSS_ROWS}}
      </table>
    </div>
    <div class="col">
      <div class="section-title">生活習慣（54点版）</div>
      <table class="mini-table">
        <tr><th>カテゴリ</th><th>点数</th><th></th></tr>
        {{HABIT_ROWS}}
      </table>
      <div style="text-align:right; font-size:10px; color:#666; margin-top:3px;">総合 {{HABIT_TOTAL}}/54　<strong>評価: {{HABIT_GRADE}}</strong></div>
    </div>
  </div>

  <!-- 改善提案 -->
  <div class="proposal-box">
    <div class="proposal-title">改善提案（優先度順）</div>
    {{PROPOSAL_TOP3}}
  </div>

  <!-- おすすめ商品 -->
  <div class="product-row">
    <div class="product-card">
      <div class="product-title">おすすめ商品 1</div>
      <div class="product-image">商品画像（スタッフ挿入）</div>
      <div class="product-name">{{PRODUCT1_NAME}}</div>
      <div class="product-comment">{{PRODUCT1_COMMENT}}</div>
    </div>
    <div class="product-card">
      <div class="product-title">おすすめ商品 2</div>
      <div class="product-image">商品画像（スタッフ挿入）</div>
      <div class="product-name">{{PRODUCT2_NAME}}</div>
      <div class="product-comment">{{PRODUCT2_COMMENT}}</div>
    </div>
  </div>
</div>
</body>
</html>
```

- [ ] **Step 2: ブラウザでプレビュー確認**

```bash
open /Users/tsujiyuuta/SleepAlign/templates/sleep-report-main-page1.html
```

プレースホルダーが `{{...}}` のまま表示されることを目視で確認。レイアウト・余白・A4サイズ感が適切かチェック。

- [ ] **Step 3: コミット**

```bash
cd /Users/tsujiyuuta/SleepAlign
git add templates/sleep-report-main-page1.html
git commit -m "feat: add main report page 1 HTML template with dashboard layout"
```

---

## Task 3: メインレポート2枚目 HTMLテンプレート

追加提案5つ＋画像貼付枠4つ＋年齢別理想睡眠時間表＋免責文。

**Files:**
- Create: `templates/sleep-report-main-page2.html`

- [ ] **Step 1: テンプレートHTMLを作成**

`/Users/tsujiyuuta/SleepAlign/templates/sleep-report-main-page2.html` に以下を書く。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>睡眠解析レポート - 2</title>
<style>
  @page { size: A4; margin: 15mm 12mm; }
  @media print {
    body { background: white; padding: 0; }
    .page { box-shadow: none; border-radius: 0; }
  }
  body {
    font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'Meiryo', sans-serif;
    background: #e8eaed;
    display: flex;
    justify-content: center;
    padding: 20px;
    margin: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .page {
    width: 595px;
    min-height: 842px;
    background: white;
    padding: 28px 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    box-sizing: border-box;
  }

  /* Header (compact, page 2) */
  .header-compact { display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; padding-bottom:8px; border-bottom:2px solid #2c5f8a; }
  .header-compact-title { font-size:14px; font-weight:bold; color:#2c5f8a; }
  .header-compact-right { font-size:9px; color:#999; }

  /* Section title */
  .section-title { font-size:12px; font-weight:bold; color:#2c5f8a; margin:14px 0 8px; padding-left:8px; border-left:3px solid #2c5f8a; }

  /* Additional proposals */
  .proposal-list { margin-bottom:16px; }
  .proposal-item { display:flex; gap:6px; align-items:start; margin-bottom:6px; font-size:11px; line-height:1.5; }
  .proposal-num { background:#5a9fd4; color:white; border-radius:50%; width:18px; height:18px; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:10px; font-weight:bold; }
  .proposal-sub { font-size:9px; color:#999; margin-top:1px; }

  /* Image grid */
  .image-grid { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:16px; }
  .image-slot { flex:1 1 calc(50% - 5px); min-width:240px; border:1px solid #e0e7ef; border-radius:8px; overflow:hidden; }
  .image-slot-title { background:#f5f7fa; padding:6px 10px; font-size:10px; font-weight:bold; color:#2c5f8a; }
  .image-slot-body { height:160px; display:flex; align-items:center; justify-content:center; font-size:10px; color:#bbb; background:#fafafa; }

  /* Sleep time table */
  .sleep-table { width:100%; border-collapse:collapse; font-size:10px; margin-bottom:16px; }
  .sleep-table th { background:#2c5f8a; color:white; padding:5px 8px; text-align:center; font-weight:normal; }
  .sleep-table td { padding:5px 8px; border-bottom:1px solid #eee; text-align:center; }
  .sleep-table tr:nth-child(even) td { background:#f9fbfd; }

  /* Disclaimer */
  .disclaimer { background:#f9f9f9; border-radius:6px; padding:10px 14px; font-size:9px; color:#999; line-height:1.6; margin-top:auto; }
</style>
</head>
<body>
<div class="page">
  <!-- ヘッダー (コンパクト) -->
  <div class="header-compact">
    <div class="header-compact-title">睡眠解析レポート（2/2）</div>
    <div class="header-compact-right">ねむりの相談所 ｜ {{PERIOD_START}} 〜 {{PERIOD_END}}</div>
  </div>

  <!-- 追加の改善提案 -->
  <div class="section-title">追加の改善提案（できそうなことから）</div>
  <div class="proposal-list">
    {{PROPOSAL_ADDITIONAL5}}
  </div>

  <!-- 画像貼付枠 -->
  <div class="section-title">測定結果</div>
  <div class="image-grid">
    <div class="image-slot">
      <div class="image-slot-title">体圧測定</div>
      <div class="image-slot-body">{{BODY_PRESSURE_IMAGE}}</div>
    </div>
    <div class="image-slot">
      <div class="image-slot-title">PIMAPITTA</div>
      <div class="image-slot-body">{{PIMAPITTA_IMAGE}}</div>
    </div>
    <div class="image-slot">
      <div class="image-slot-title">枕判定</div>
      <div class="image-slot-body">{{PILLOW_IMAGE}}</div>
    </div>
    <div class="image-slot">
      <div class="image-slot-title">マットレス判定</div>
      <div class="image-slot-body">{{MATTRESS_IMAGE}}</div>
    </div>
  </div>

  <!-- 年齢別理想睡眠時間表 -->
  <div class="section-title">年齢別 理想睡眠時間（参考）</div>
  <table class="sleep-table">
    <tr>
      <th>年齢</th>
      <th>10代</th>
      <th>20代</th>
      <th>30代</th>
      <th>40代</th>
      <th>50代</th>
      <th>60代</th>
      <th>70代以上</th>
    </tr>
    <tr>
      <td style="font-weight:bold; color:#2c5f8a;">理想</td>
      <td>8〜10h</td>
      <td>7〜9h</td>
      <td>7〜8.5h</td>
      <td>7〜8h</td>
      <td>6.5〜7.5h</td>
      <td>6〜7h</td>
      <td>5.5〜7h</td>
    </tr>
  </table>

  <!-- 免責文 -->
  <div class="disclaimer">
    ※本レポートは睡眠状態を把握し、生活習慣や睡眠環境の見直しのヒントを提供するものです。医療行為・診断を行うものではありません。体調不良が続く場合は医療機関へご相談ください。
  </div>
</div>
</body>
</html>
```

- [ ] **Step 2: ブラウザでプレビュー確認**

```bash
open /Users/tsujiyuuta/SleepAlign/templates/sleep-report-main-page2.html
```

画像枠のサイズ・バランス、年齢別表の表示、免責文の位置を確認。

- [ ] **Step 3: コミット**

```bash
cd /Users/tsujiyuuta/SleepAlign
git add templates/sleep-report-main-page2.html
git commit -m "feat: add main report page 2 template with image slots and sleep table"
```

---

## Task 4: 詳細版（別紙読み物）HTMLテンプレート

スタッフが抜粋して説明 ＋ お客様が持ち帰り一人読みできるデザイン。メインと同じ青ベースのテイスト。

**Files:**
- Create: `templates/sleep-report-detail.html`

- [ ] **Step 1: テンプレートHTMLを作成**

`/Users/tsujiyuuta/SleepAlign/templates/sleep-report-detail.html` に以下を書く。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>睡眠解析レポート 詳細版</title>
<style>
  @page { size: A4; margin: 15mm 12mm; }
  @media print {
    body { background: white; padding: 0; }
    .page { box-shadow: none; border-radius: 0; page-break-after: always; }
    .page:last-child { page-break-after: auto; }
  }
  body {
    font-family: 'Helvetica Neue', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'Meiryo', sans-serif;
    background: #e8eaed;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    padding: 20px;
    margin: 0;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .page {
    width: 595px;
    background: white;
    padding: 32px 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    box-sizing: border-box;
  }

  /* Header */
  .header { text-align:center; margin-bottom:20px; padding-bottom:14px; border-bottom:3px solid #2c5f8a; }
  .header-en { font-size:9px; color:#aaa; letter-spacing:2px; margin-bottom:4px; }
  .header-title { font-size:20px; font-weight:bold; color:#2c5f8a; }
  .header-subtitle { font-size:11px; color:#666; margin-top:6px; }

  /* Section */
  .section { margin-bottom:24px; }
  .section-title { font-size:14px; font-weight:bold; color:#2c5f8a; margin-bottom:10px; padding:6px 10px; background:#f0f5fa; border-radius:6px; border-left:4px solid #2c5f8a; }
  .section-body { font-size:12px; color:#444; line-height:1.8; padding:0 4px; }
  .section-body p { margin:0 0 8px; }

  /* Data table */
  .data-table { width:100%; border-collapse:collapse; font-size:10px; margin:10px 0; }
  .data-table th { background:#2c5f8a; color:white; padding:6px 8px; text-align:center; font-weight:normal; }
  .data-table td { padding:5px 8px; border-bottom:1px solid #eee; text-align:center; }
  .data-table tr:nth-child(even) td { background:#f9fbfd; }

  /* Highlight box */
  .highlight-box { background:#fff8f0; border:1px solid #fce4c0; border-radius:8px; padding:12px 14px; margin:10px 0; }
  .highlight-box-title { font-size:11px; font-weight:bold; color:#e67e22; margin-bottom:4px; }
  .highlight-box-body { font-size:11px; color:#555; line-height:1.7; }

  /* Info box */
  .info-box { background:#f0f5fa; border-radius:8px; padding:12px 14px; margin:10px 0; }
  .info-box-title { font-size:11px; font-weight:bold; color:#2c5f8a; margin-bottom:4px; }
  .info-box-body { font-size:11px; color:#555; line-height:1.7; }

  /* Proposal detail */
  .proposal-detail { margin:8px 0; padding:10px 14px; background:#f8fafe; border-radius:8px; border-left:3px solid #2c5f8a; }
  .proposal-detail-num { font-size:10px; color:#2c5f8a; font-weight:bold; margin-bottom:2px; }
  .proposal-detail-title { font-size:12px; font-weight:bold; color:#333; margin-bottom:4px; }
  .proposal-detail-body { font-size:11px; color:#555; line-height:1.7; }

  /* Glossary */
  .glossary-item { display:flex; gap:8px; margin-bottom:6px; font-size:11px; }
  .glossary-term { font-weight:bold; color:#2c5f8a; min-width:120px; flex-shrink:0; }
  .glossary-def { color:#555; line-height:1.6; }

  /* Disclaimer */
  .disclaimer { background:#f9f9f9; border-radius:6px; padding:10px 14px; font-size:9px; color:#999; line-height:1.6; margin-top:20px; }

  /* Page header (compact, for pages 2+) */
  .page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding-bottom:8px; border-bottom:2px solid #2c5f8a; font-size:10px; color:#999; }
</style>
</head>
<body>

<!-- ======= ページ1: 表紙 + 睡眠データ詳細 ======= -->
<div class="page">
  <div class="header">
    <div class="header-en">SLEEP ANALYSIS REPORT — DETAILED</div>
    <div class="header-title">睡眠解析レポート 詳細版</div>
    <div class="header-subtitle">ねむりの相談所 ｜ 測定期間：{{PERIOD_START}} 〜 {{PERIOD_END}}（{{PERIOD_DAYS}}日間）</div>
  </div>

  <div class="section">
    <div class="section-title">1. 睡眠データ詳細</div>
    <div class="section-body">
      {{SLEEP_DATA_DETAIL_TEXT}}
    </div>
    {{DAILY_DATA_TABLE}}
  </div>

  <div class="section">
    <div class="section-title">2. 入眠時の体の向き</div>
    <div class="section-body">
      {{SLEEP_DIRECTION_DETAIL}}
    </div>
  </div>

  <div class="section">
    <div class="section-title">3. ソーシャルジェットラグ 詳細</div>
    <div class="section-body">
      {{JETLAG_DETAIL_TEXT}}
    </div>
    {{JETLAG_DAILY_TABLE}}
    <div class="highlight-box">
      <div class="highlight-box-title">最もズレが大きかった日</div>
      <div class="highlight-box-body">{{JETLAG_MAX_DAY_DETAIL}}</div>
    </div>
  </div>
</div>

<!-- ======= ページ2: ストレス・生活習慣・提案詳細 ======= -->
<div class="page">
  <div class="page-header">
    <span>睡眠解析レポート 詳細版</span>
    <span>{{PERIOD_START}} 〜 {{PERIOD_END}}</span>
  </div>

  <div class="section">
    <div class="section-title">4. ストレスと睡眠の関連</div>
    <div class="section-body">
      {{STRESS_DETAIL_TEXT}}
    </div>
    <div class="info-box">
      <div class="info-box-title">PSS（知覚されたストレス尺度）とは？</div>
      <div class="info-box-body">{{PSS_EXPLANATION}}</div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">5. 生活習慣 カテゴリ別アドバイス</div>
    <div class="section-body">
      {{HABIT_CATEGORY_ADVICE}}
    </div>
  </div>

  <div class="section">
    <div class="section-title">6. 改善提案 詳細</div>
    {{PROPOSAL_ALL_DETAILS}}
  </div>
</div>

<!-- ======= ページ3: 用語集 + 免責 ======= -->
<div class="page">
  <div class="page-header">
    <span>睡眠解析レポート 詳細版</span>
    <span>{{PERIOD_START}} 〜 {{PERIOD_END}}</span>
  </div>

  <div class="section">
    <div class="section-title">7. 用語集</div>
    <div class="section-body">
      {{GLOSSARY_ITEMS}}
    </div>
  </div>

  <div class="disclaimer">
    ※本レポートは睡眠状態を把握し、生活習慣や睡眠環境の見直しのヒントを提供するものです。医療行為・診断を行うものではありません。体調不良が続く場合は医療機関へご相談ください。
  </div>
</div>

</body>
</html>
```

- [ ] **Step 2: ブラウザでプレビュー確認**

```bash
open /Users/tsujiyuuta/SleepAlign/templates/sleep-report-detail.html
```

3ページ構成が縦に並んで表示されることを確認。セクション見出しの視認性、印刷時のページ区切り（page-break）が適切か確認。

- [ ] **Step 3: コミット**

```bash
cd /Users/tsujiyuuta/SleepAlign
git add templates/sleep-report-detail.html
git commit -m "feat: add detailed report template with 7 sections across 3 pages"
```

---

## Task 5: スラッシュコマンド本体の作成

全ロジック（受付→解析→出力）を1つのコマンドファイルに記述する。

**Files:**
- Create: `~/.claude/commands/sleep-report.md`

- [ ] **Step 1: コマンドファイルを作成**

`/Users/tsujiyuuta/.claude/commands/sleep-report.md` に以下を書く。

````markdown
あなたは、ねむりの相談所（寝具専門店）の「睡眠解析・改善提案レポート」作成アシスタントです。
スタッフから受け取ったデータを解析し、HTMLレポートを2種類（メインレポートA4×2枚 ＋ 詳細版別紙）で出力します。

$ARGUMENTS

---

# 最重要ルール（安全・品質）

- 医療行為・診断はしない。断定しない（「〜の可能性」「〜が影響しているかもしれません」）
- 入力に個人情報（氏名・住所・電話・メール・生年月日・ID等）が含まれても、出力へ一切再掲しない（伏せ字もしない。そもそも書かない）
- 読み手が知識ゼロでも分かる表現。専門用語は短い言い換えを添える
- 矛盾があれば、主訴を先に扱いつつ「数値的にはここも気になるかもしれません」と併記

---

# Phase 1: 受付モード

## 起動メッセージ
コマンド起動時、以下を表示する：

```
【睡眠解析レポート作成】

データを全部添付してください。画像・Excel・PDFどれでも一度にまとめてOKです。

必要なデータ：
• 睡眠解析スクショ（日次 7〜20日分）
• 週間集計スクショ
• PSS・生活習慣チェック（Excel）
• コンサルティングシート（PDF）
• 体圧測定画像、PIMAPITTA画像（あれば）
```

## データ受領時の動作

1. 添付されたデータを自動で種類判別する
2. 以下のチェックリストを表示する：

```
【受領チェックリスト】
1) 睡眠解析（日次）…… ✅/⬜/❓  ○日分（期間：○/○〜○/○）
2) 週間集計 …… ✅/⬜/❓
3) PSS・生活習慣チェック …… ✅/⬜/❓
   - ネガティブ/ポジティブ/総合/リスク： ✅/⬜
   - 5カテゴリ点数+総合点+評価(A/B/C)： ✅/⬜
4) コンサルティングシート …… ✅/⬜/❓
5) 貼付用画像
   - 体圧測定 …… ✅/⬜
   - PIMAPITTA …… ✅/⬜
```

3. 確認事項を表示する：

```
【確認事項】
・睡眠解析は○日分でOKですか？
・期間は○/○〜○/○で合っていますか？
・特記事項があれば追記してください（任意）
```

4. 不足がある場合は「○○が不足しています。添付してください」と案内する
5. 画像から日付が読めない場合は❓として確認を求める
6. スタッフが「OK」と返信するまでPhase 2には進まない

---

# Phase 2: 解析

スタッフの確認OKを受けて解析を開始する。

## 睡眠指標（8項目を算出）

1. **平均睡眠時間**（h:mm）— 理想は年齢別レンジ
2. **寝つき平均時間**（分）— 理想10分前後
   - 優先順位：A)画面明記 → B)赤線/入眠開始 → C)寝つき評価(1-5)推定
   - 推定マッピング：5=0-10分, 4=10-20分, 3=20-30分, 2=30-45分, 1=45分以上
   - 推定時は必ず「推定」と表記。5分以内が多い場合は「睡眠負債の可能性」コメント
3. **寝返り回数平均** — 適正20〜30回
4. **活動量平均**（1〜5）— 理想3以上
5. **覚醒回数分布** — 0〜2回/3〜5回/5回以上の日数と割合
6. **就寝中の向き** — 仰向け/右/左/うつ伏せの%（睡眠中のみ集計）
7. **入眠の体の向き** — 多い向き＋代表的遷移
8. **ソーシャルジェットラグ** — 全日の入眠/起床/睡眠時間の中央値からの最大ズレ。主因を短文で説明

## 総合スコア算出（/100点）

| 項目 | 配点 | 算出 |
|---|---|---|
| 睡眠時間充足度 | 20点 | 理想時間範囲内=20, 30分不足ごとに-4, 1h以上不足=8以下 |
| 寝つき | 15点 | 10分=15, 5-15分=12, 15-20分=10, 20-30分=7, 30分以上=3 |
| リズム安定性 | 20点 | ジェットラグ0-30分=20, 30-60分=16, 1-2h=12, 2-3h=8, 3h以上=4 |
| 覚醒の少なさ | 15点 | 0-2回割合×15（例：80%なら12点） |
| 活動量 | 10点 | 平均3以上=10, 2.5-3=7, 2-2.5=5, 2未満=3 |
| 生活習慣 | 10点 | (54-点数)/54×10（低いほど良いので反転） |
| ストレス | 10点 | PSS0-13=10, 14-19=7, 20-26=5, 27以上=2 |

## PSS判定

- 0〜13：低リスク / 14〜26：中ストレス / 27以上：高ストレス
- コメント：睡眠指標との紐づけを1〜2行で

## 生活習慣チェック（54点版）

- カテゴリ配点：睡眠環境15/食事・飲料15/運動9/ストレス管理6/就寝・起床9
- 評価：A(19-28良好)/B(29-38やや問題)/C(39-54改善余地大)

## バランス評価（★4段階）

各指標を★1〜4で評価する：
- 睡眠時間：理想範囲内=★4, やや不足=★3, 不足=★2, 大幅不足=★1
- 寝つき：10分以内=★4, 10-20分=★3, 20-30分=★2, 30分以上=★1
- リズム安定：ジェットラグ30分以内=★4, 1h以内=★3, 2h以内=★2, 2h超=★1
- 覚醒：0-2回80%以上=★4, 60%以上=★3, 40%以上=★2, 40%未満=★1
- 活動量：3以上=★4, 2.5-3=★3, 2-2.5=★2, 2未満=★1
- 睡眠姿勢：仰向け60%以上=★4, 40-60%=★3, その他=★2（うつ伏せ多=★1）

## 総評と提案の生成

優先順：①睡眠分析結果 → ②生活習慣改善 → ③ストレス改善 → ④睡眠環境改善 → ⑤寝具提案

- **最優先3つ**：今すぐ・効果大・主訴に刺さるもの。具体的行動＋理由1行
- **追加候補5つ**：できそうな順。いつ・どれくらい・何を
- **おすすめ商品2つ**：寝具 or スリープテックに限定。商品カテゴリ案＋コメント下書き

## 前処理ルール

- 欠損日は除外し「欠損◯日」と注記
- 体の向きは睡眠中（グレー塗り範囲）のみ集計
- 時刻の日付跨ぎは自動補正
- 算出不可項目は「算出不可（理由）」と明記

---

# Phase 3: レポート出力

## 出力手順

1. テンプレートファイルを読む：
   - `/Users/tsujiyuuta/SleepAlign/templates/sleep-report-main-page1.html`
   - `/Users/tsujiyuuta/SleepAlign/templates/sleep-report-main-page2.html`
   - `/Users/tsujiyuuta/SleepAlign/templates/sleep-report-detail.html`

2. 各テンプレートの `{{PLACEHOLDER}}` を解析結果で置き換え、HTMLを生成する

3. 出力先ディレクトリを作成して保存する：
   ```
   ~/Desktop/claude-outputs/nemunemu/sleep-report/YYYYMMDD_レポート/
   ```

4. 以下のファイルを書き出す：
   - `sleep-report-main-page1.html`（メイン1枚目）
   - `sleep-report-main-page2.html`（メイン2枚目）
   - `sleep-report-detail.html`（詳細版）

5. ブラウザでプレビューを開く：
   ```bash
   open ~/Desktop/claude-outputs/nemunemu/sleep-report/YYYYMMDD_レポート/sleep-report-main-page1.html
   ```

6. スタッフに確認を促す：
   ```
   レポートが完成しました。ブラウザでプレビューを確認してください。
   修正が必要な場合はお知らせください。
   
   保存先：~/Desktop/claude-outputs/nemunemu/sleep-report/YYYYMMDD_レポート/
   - sleep-report-main-page1.html（メイン1枚目）
   - sleep-report-main-page2.html（メイン2枚目）
   - sleep-report-detail.html（詳細版）
   
   印刷する場合：各HTMLをブラウザで開き → 印刷（Ctrl+P / Cmd+P）
   ```

## プレースホルダー一覧

### メイン1枚目
| プレースホルダー | 内容 |
|---|---|
| `{{PERIOD_START}}` | 測定開始日（YYYY/MM/DD） |
| `{{PERIOD_END}}` | 測定終了日 |
| `{{PERIOD_DAYS}}` | 測定日数 |
| `{{TOTAL_SCORE}}` | 総合スコア（0-100の整数） |
| `{{STRESS_RISK}}` | ストレスリスク（低/中/高） |
| `{{STRESS_LEVEL}}` | PSS判定テキスト |
| `{{HABIT_GRADE}}` | 生活習慣評価（A/B/C） |
| `{{HABIT_COMMENT}}` | 生活習慣の短評 |
| `{{AVG_SLEEP_TIME}}` | 平均睡眠時間（例：6h50m） |
| `{{IDEAL_SLEEP_TIME}}` | 年齢別理想時間 |
| `{{AVG_ONSET_TIME}}` | 寝つき平均（例：約15分） |
| `{{AVG_TURNOVER}}` | 寝返り平均（例：22回） |
| `{{AVG_ACTIVITY}}` | 活動量平均（例：2.8） |
| `{{BALANCE_ROWS}}` | ★評価の行HTML（6行分） |
| `{{DIRECTION_SVG}}` | 体の向きドーナツチャートSVG |
| `{{DIRECTION_LEGEND}}` | 体の向き凡例HTML |
| `{{AWAKENING_BARS}}` | 覚醒回数バーチャートHTML |
| `{{JETLAG_VALUE}}` | ジェットラグ値（例：約3） |
| `{{JETLAG_UNIT}}` | 単位（例：時間） |
| `{{JETLAG_COMMENT}}` | ジェットラグのコメント |
| `{{PSS_ROWS}}` | PSS結果の行HTML |
| `{{HABIT_ROWS}}` | 生活習慣の行HTML |
| `{{HABIT_TOTAL}}` | 生活習慣合計点 |
| `{{PROPOSAL_TOP3}}` | 最優先3提案のHTML |
| `{{PRODUCT1_NAME}}` | おすすめ商品1名 |
| `{{PRODUCT1_COMMENT}}` | おすすめ商品1コメント |
| `{{PRODUCT2_NAME}}` | おすすめ商品2名 |
| `{{PRODUCT2_COMMENT}}` | おすすめ商品2コメント |

### メイン2枚目
| プレースホルダー | 内容 |
|---|---|
| `{{PROPOSAL_ADDITIONAL5}}` | 追加5提案のHTML |
| `{{BODY_PRESSURE_IMAGE}}` | 体圧測定画像（base64 or パス） |
| `{{PIMAPITTA_IMAGE}}` | PIMAPITTA画像 |
| `{{PILLOW_IMAGE}}` | 枕判定画像 |
| `{{MATTRESS_IMAGE}}` | マットレス判定画像 |

### 詳細版
| プレースホルダー | 内容 |
|---|---|
| `{{SLEEP_DATA_DETAIL_TEXT}}` | 睡眠データの解説文 |
| `{{DAILY_DATA_TABLE}}` | 日別データ一覧テーブルHTML |
| `{{SLEEP_DIRECTION_DETAIL}}` | 入眠時の向き詳細文 |
| `{{JETLAG_DETAIL_TEXT}}` | ジェットラグ解説文 |
| `{{JETLAG_DAILY_TABLE}}` | 日別ズレ一覧テーブルHTML |
| `{{JETLAG_MAX_DAY_DETAIL}}` | 最大ズレ日の詳細文 |
| `{{STRESS_DETAIL_TEXT}}` | ストレスと睡眠の関連文 |
| `{{PSS_EXPLANATION}}` | PSSの解説文 |
| `{{HABIT_CATEGORY_ADVICE}}` | 5カテゴリ別アドバイスHTML |
| `{{PROPOSAL_ALL_DETAILS}}` | 8提案の詳細HTML |
| `{{GLOSSARY_ITEMS}}` | 用語集HTML |

## HTMLパーツの生成ルール

### バランス評価の行（BALANCE_ROWS）
各行は以下のHTMLで生成する：
```html
<div class="balance-row">
  <span class="metric-label">【項目名】</span>
  <span class="balance-stars">【★/☆を4つ並べる】</span>
  <span class="balance-comment">【短評】</span>
</div>
```

### ドーナツチャートSVG（DIRECTION_SVG）
体の向き%からSVGを生成する。円周=2π×36≈226。各セグメントのstroke-dasharrayを%から算出：
```
セグメント長 = 226 × (% / 100)
offset = 前セグメントまでの累計長のマイナス値
```
色: 仰向け=#2c5f8a, 右=#5a9fd4, 左=#a3c4e0, うつ伏せ=#d0dde8

### 覚醒回数バー（AWAKENING_BARS）
各カテゴリの日数から%を算出し、バー幅に反映：
```html
<div class="bar-wrap">
  <div class="bar-label"><span>【カテゴリ】</span><span>【日数】日</span></div>
  <div class="bar-bg"><div class="bar-fill" style="width:【%】%; background:【色】;"></div></div>
</div>
```
色: 0-2回=#2c5f8a, 3-5回=#5a9fd4, 5回以上=#e67e22

### 提案のHTML（PROPOSAL_TOP3 / PROPOSAL_ADDITIONAL5）
```html
<div class="proposal-item">
  <span class="proposal-num">【番号】</span>
  <div>
    <div>【提案内容】</div>
    <div class="proposal-sub">【理由1行】</div>
  </div>
</div>
```

### PSS行（PSS_ROWS）
```html
<tr><td>【指標名】</td><td><span class="eval-badge 【eval-good/eval-warn/eval-info】">【結果】</span></td></tr>
```

### 生活習慣行（HABIT_ROWS）
```html
<tr><td>【カテゴリ】</td><td>【点数】/【配点】</td><td><span class="eval-badge 【eval-good/eval-warn】">【○/△】</span></td></tr>
```
評価基準：配点の50%未満=○(eval-good), 50%以上=△(eval-warn)

## 文体ルール（出力テキスト）
- 親しみのある丁寧な口語（硬い提案書口調は避ける）
- 「〜してみてください」「〜がおすすめです」のトーン
- 推定項目には必ず「推定」と明記し根拠を1行添える
````

- [ ] **Step 2: コマンドファイルの動作確認**

コマンドが正しく配置されたことを確認：

```bash
ls -la ~/.claude/commands/sleep-report.md
```

Claude Codeを再起動し、`/sleep-report` と入力して起動メッセージが表示されることを確認。

- [ ] **Step 3: コミット**

コマンドファイルはホームディレクトリにあるため、プロジェクト内にもコピーを保存する：

```bash
cp ~/.claude/commands/sleep-report.md /Users/tsujiyuuta/SleepAlign/commands/sleep-report.md
mkdir -p /Users/tsujiyuuta/SleepAlign/commands
cp ~/.claude/commands/sleep-report.md /Users/tsujiyuuta/SleepAlign/commands/sleep-report.md
cd /Users/tsujiyuuta/SleepAlign
git add commands/sleep-report.md
git commit -m "feat: add sleep-report slash command with full analysis and output logic"
```

---

## Task 6: サンプルデータで統合テスト

`~/Downloads/睡眠解析用元データ/` の実データを使って、コマンドの全フローを通しテストする。

**Files:**
- Read: `~/Downloads/睡眠解析用元データ/` 配下のファイル群
- Output: `~/Desktop/claude-outputs/nemunemu/sleep-report/YYYYMMDD_レポート/`

- [ ] **Step 1: `/sleep-report` を起動**

Claude Codeで `/sleep-report` と入力。起動メッセージが表示されることを確認。

- [ ] **Step 2: サンプルデータを添付**

以下のファイルを添付する：
- `~/Downloads/睡眠解析用元データ/睡眠解析結果/日別睡眠計測.png`
- `~/Downloads/睡眠解析用元データ/睡眠解析結果/日付睡眠計測２.png`
- `~/Downloads/睡眠解析用元データ/睡眠解析結果/スクリーンショット 2026-01-25 112555.png`
- `~/Downloads/睡眠解析用元データ/睡眠解析結果/週間集計 スクショ.png`（ファイル名に全角スペースが含まれる可能性あり）
- `~/Downloads/睡眠解析用元データ/睡眠解析結果/週間集計 すくしょ２.png`
- `~/Downloads/睡眠解析用元データ/PSS:生活習慣 回答結果集計.xlsx`
- `~/Downloads/睡眠解析用元データ/コンサルティングシート_専門店.pdf`
- `~/Downloads/睡眠解析用元データ/体圧測定結果.PNG`
- `~/Downloads/睡眠解析用元データ/PIMAPITTA解析結果/IMG_4494.PNG`
- `~/Downloads/睡眠解析用元データ/PIMAPITTA解析結果/IMG_4495.PNG`
- `~/Downloads/睡眠解析用元データ/PIMAPITTA解析結果/IMG_4496.PNG`

- [ ] **Step 3: チェックリスト確認**

チェックリストが表示されることを確認：
- 全項目に✅/⬜/❓が付いているか
- 日数と期間が正しく読み取れているか
- 確認事項が表示されているか

- [ ] **Step 4: 解析実行**

「OK」と返信し、解析が開始されることを確認。

- [ ] **Step 5: 出力確認**

以下を確認する：
- 出力先ディレクトリが作成されているか
- 3つのHTMLファイルが生成されているか
- ブラウザでプレビューが開くか

```bash
ls ~/Desktop/claude-outputs/nemunemu/sleep-report/
```

- [ ] **Step 6: メインレポート1枚目の品質確認**

ブラウザで開き以下を確認：
- [ ] 総合スコアが0-100の範囲内か
- [ ] ★評価が正しく表示されているか
- [ ] ドーナツチャートが正しく描画されているか
- [ ] 覚醒回数バーの比率が正しいか
- [ ] ジェットラグの値が妥当か
- [ ] PSS・生活習慣テーブルが正しいか
- [ ] 提案が3つ表示されているか
- [ ] おすすめ商品が2つ表示されているか
- [ ] 個人情報が一切含まれていないか
- [ ] 印刷プレビュー（Cmd+P）でA4に収まるか

- [ ] **Step 7: メインレポート2枚目の品質確認**

- [ ] 追加提案が5つ表示されているか
- [ ] 画像枠が4つあるか（画像が埋め込まれているか、または「スタッフ挿入」のプレースホルダーか）
- [ ] 年齢別睡眠時間表が正しいか
- [ ] 免責文が表示されているか

- [ ] **Step 8: 詳細版の品質確認**

- [ ] 7つのセクションが全て存在するか
- [ ] 日別データテーブルに全日分のデータがあるか
- [ ] ジェットラグ詳細に日別ズレと最大ズレ日があるか
- [ ] 文体が平易で読みやすいか
- [ ] 専門用語に言い換えが添えられているか
- [ ] 用語集が含まれているか
- [ ] 医療断定表現がないか
- [ ] 印刷プレビューでページ区切りが適切か

- [ ] **Step 9: 修正対応（必要な場合）**

テスト結果で問題があれば、テンプレートまたはコマンドファイルを修正して再テスト。

- [ ] **Step 10: コミット**

```bash
cd /Users/tsujiyuuta/SleepAlign
git add -A
git commit -m "test: complete integration test with sample data, fix any issues"
```

---

## Task 7: スタッフPC展開準備

**Files:**
- Finalize: `~/.claude/commands/sleep-report.md`
- Finalize: `templates/` ディレクトリ一式

- [ ] **Step 1: コマンドファイル内のパスを汎用化**

コマンドファイル内のテンプレートパスがスタッフPCでも動くか確認。
`/Users/tsujiyuuta/SleepAlign/templates/` は辻さんのPC固有パスなので、スタッフPCにコピーする際の手順を整理する。

スタッフPC展開手順：

```
1. スタッフPCにClaude Codeをインストール
2. Claudeアカウントでログイン
3. 以下のファイルをコピー：
   - ~/.claude/commands/sleep-report.md → スタッフPCの同じ場所
   - SleepAlignプロジェクト一式 → スタッフPCの任意の場所
4. sleep-report.md内のテンプレートパスをスタッフPCのパスに書き換え
5. /sleep-report で動作確認
```

- [ ] **Step 2: コマンドファイル内のパスを環境変数対応にする**

テンプレートパスを相対パス化する。コマンドファイル内の指示を以下に修正：

```
テンプレートファイルの場所を探す手順：
1. まず ~/SleepAlign/templates/ を確認
2. なければ ~/Desktop/SleepAlign/templates/ を確認
3. なければ「テンプレートが見つかりません。SleepAlignフォルダの場所を教えてください」と聞く
```

- [ ] **Step 3: 最終コミット**

```bash
cd /Users/tsujiyuuta/SleepAlign
git add -A
git commit -m "feat: finalize sleep-report command with portable template paths"
```
