"""
SleepAlign - 寝姿勢評価プロトタイプ
パターンC（ハイブリッド方式）+ 方針D（上面ベース相対評価）

使い方:
  python3 evaluate.py 写真のパス
  python3 evaluate.py 写真のパス --debug  (詳細ログ付き)
"""

import anthropic
import base64
import sys
import json
import mimetypes
import os
from PIL import Image, ImageDraw, ImageFont


SYSTEM_PROMPT = """あなたは寝具専門店の寝姿勢評価アシスタントです。
マットレスの上に寝ている人の写真を分析し、寝姿勢とマットレスの相性を評価します。

## 評価の原則

1. **上面ベースの相対評価**: 体の上面輪郭しか見えないため、絶対的な沈み込み量は判定しない。
   上面の輪郭ポイント同士の相対関係（ズレ・傾き）で評価する。
2. **評価基準は身体ラインの直線性**: マットレス水平面との比較ではなく、
   身体の複数ポイントを結ぶ直線からのズレで「寝姿勢の綺麗さ」を判断する。
3. **服の影響を考慮**: 服を着ていても体のシルエットは認識できる。
   ただし肩・腰周りは服の影響が大きいことを念頭に置く。

## 仰向け寝の評価ポイント

- **顎の位置が最重要**: 適切な寝姿勢では「顎が軽く引けている」状態。
  - 顎が上がっている = 頭が低すぎる（枕が低い/ない）→ 首に負担
  - 顎が引けすぎている = 頭が高すぎる（枕が高い）→ 気道圧迫
- 枕なしの場合、頭がマットレスに対して低くなり顎が上がるのが典型。
  「頭が高い」と誤判定しないこと。
- 腰部の沈み込みが大きすぎると骨盤が下がり、腰痛の原因になる。

## 横向き寝の評価ポイント

- **肩の沈み込みが最重要**: 横向き寝では肩がマットレスに適切に沈み込むことで、
  背骨が一直線に保たれる。
  - 肩の沈み込みが不足（マットレスが硬い）→ 肩が持ち上がる → 頭が下に落ちる
  - 肩の沈み込みが過剰（マットレスが柔らかい）→ 肩が沈みすぎる → 頭が上に浮く
- **因果関係を重視**: 「頭が落ちている」は結果であり、原因は「肩の沈み込み不足」。
  根本原因を特定して報告すること。
- 腰の浮きも重要だが、横向き寝では肩の沈み込みの方が支配的な要因。"""

EVALUATION_PROMPT = """添付された写真は、マットレスの上に寝ている人を真横から撮影したものです。
3段階で分析を行ってください。

【第1段階: 寝姿勢の種類と全体把握】
まず、仰向け寝か横向き寝かを判定してください。
次に、体全体のシルエット（輪郭）を認識し、
体の上側の輪郭と下側の輪郭の中間を通る「体軸中心線」を想定してください。

【第2段階: キーポイントの評価】

■ 仰向け寝の場合:
- 顎の位置を最優先で確認（顎が引けているか、上がっているか）
- 顎が上がっている = 頭が低すぎる状態。枕なしや低い枕で起きやすい
- 腰部の沈み込み具合を確認

■ 横向き寝の場合:
- 肩の沈み込みを最優先で確認（肩がマットレスに十分沈み込んでいるか）
- 肩が十分沈み込んでいないと、肩が上がり → 結果として頭が下に落ちる
- 「頭が落ちている」は結果。原因（肩の沈み込み不足等）を特定すること
- 腰の浮きも確認するが、肩の沈み込みが最も支配的な要因

【第3段階: 5区間の詳細チェック】
体軸中心線に沿って、以下の5区間を評価してください。

【第4段階: プロットポイントの座標指定】
写真上の以下6つの部位について、体軸中心線上の位置をピクセル座標(x, y)で指定してください。
写真の左上が(0, 0)です。体の上面輪郭の最高点ではなく、上面と下面の中間点（体の厚みの中心）を推定してください。

- head: 後頭部（頭の中心）
- neck: 首の付け根
- shoulder: 肩（仰向け: 肩の最も高い点、横向き: 肩の中心）
- waist: 腰（ウエストの位置）
- pelvis: 骨盤（お尻の最も幅広い位置）
- knee: 膝

以下のJSON形式で回答してください。JSONのみを出力し、それ以外のテキストは含めないでください。

{
  "sleeping_position": "仰向け / 横向き",
  "center_line_shape": "直線型 / 上凸型 / 下凸型 / S字型 / 折れ曲がり型 のいずれか",
  "center_line_summary": "中心線の概要 50字以内",
  "key_observation": {
    "primary_issue": "最も重要な問題点を1文で（仰向け: 顎の位置、横向き: 肩の沈み込み中心に）",
    "cause": "その問題の原因（マットレスが硬い/柔らかい、枕が高い/低い/なし 等）",
    "effect": "結果として体のどこにどう影響しているか"
  },
  "plot_points": {
    "head":     {"x": 0, "y": 0},
    "neck":     {"x": 0, "y": 0},
    "shoulder": {"x": 0, "y": 0},
    "waist":    {"x": 0, "y": 0},
    "pelvis":   {"x": 0, "y": 0},
    "knee":     {"x": 0, "y": 0}
  },
  "sections": {
    "head_to_neck": {
      "tilt": "水平 / やや上向き / やや下向き / 明確に上向き / 明確に下向き",
      "note": "気になる点があれば30字以内"
    },
    "neck_to_shoulder": {
      "tilt": "同上",
      "note": ""
    },
    "shoulder_to_waist": {
      "tilt": "同上",
      "note": ""
    },
    "waist_to_pelvis": {
      "tilt": "同上",
      "note": ""
    },
    "pelvis_to_knee": {
      "tilt": "同上",
      "note": ""
    }
  },
  "floating_areas": "浮いている箇所の説明。なければ「なし」",
  "sinking_areas": "沈み込んでいる箇所の説明。なければ「なし」",
  "neck_continuity": "背骨のラインと自然に連続 / やや折れ曲がり / 明確な角度変化",
  "straight_line_deviation": {
    "description": "頭〜膝を結ぶ直線からのズレの説明 100字以内",
    "worst_section": "最もズレが大きい区間名（根本原因の区間を指定すること）",
    "deviation_direction": "上にズレ / 下にズレ / ほぼなし"
  },
  "overall_rating": "良好 / やや注意 / 要改善",
  "mattress_feedback": "このマットレスとの相性について 100字以内",
  "recommendation": "改善が必要な場合の具体的なアドバイス 100字以内"
}"""


def load_image(path, max_long_side=1024):
    """画像ファイルを読み込み、縮小してbase64エンコード。元サイズとスケール比も返す"""
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
        print(f"エラー: 対応していない画像形式です ({mime_type})")
        print("対応形式: JPEG, PNG, WebP, GIF")
        sys.exit(1)

    img = Image.open(path)
    orig_w, orig_h = img.size

    # 長辺をmax_long_sideに縮小
    long_side = max(orig_w, orig_h)
    if long_side > max_long_side:
        scale = max_long_side / long_side
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
    else:
        scale = 1.0
        new_w, new_h = orig_w, orig_h
        img_resized = img

    # 縮小画像をbase64エンコード
    import io
    buf = io.BytesIO()
    img_resized.save(buf, format="JPEG", quality=90)
    data = base64.standard_b64encode(buf.getvalue()).decode("utf-8")

    return "image/jpeg", data, (orig_w, orig_h), (new_w, new_h)


def evaluate(image_path, debug=False):
    """寝姿勢を評価"""
    client = anthropic.Anthropic()

    mime_type, image_data, orig_size, resized_size = load_image(image_path)

    if debug:
        print(f"画像: {image_path}")
        print(f"元サイズ: {orig_size[0]}x{orig_size[1]}")
        print(f"縮小後: {resized_size[0]}x{resized_size[1]}")
        print(f"データサイズ: {len(image_data)} bytes (base64)")
        print("---")
        print("APIリクエスト送信中...")

    # 縮小後のサイズをプロンプトに埋め込む
    size_info = f"\n\n※この画像のサイズは {resized_size[0]}x{resized_size[1]} ピクセルです。座標はこのサイズに基づいて指定してください。"
    prompt_with_size = EVALUATION_PROMPT + size_info

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt_with_size,
                    },
                ],
            }
        ],
    )

    raw_text = response.content[0].text

    if debug:
        print(f"トークン使用量: 入力={response.usage.input_tokens}, 出力={response.usage.output_tokens}")
        print("---")
        print("生の応答:")
        print(raw_text)
        print("---")

    # JSONをパース
    try:
        # ```json ... ``` で囲まれている場合を処理
        text = raw_text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]
        result = json.loads(text)
    except json.JSONDecodeError:
        print("警告: JSON解析に失敗しました。生のテキストを表示します。")
        print(raw_text)
        return None

    # 座標を元画像サイズにスケールアップ
    if "plot_points" in result and resized_size != orig_size:
        scale_x = orig_size[0] / resized_size[0]
        scale_y = orig_size[1] / resized_size[1]
        if debug:
            print(f"座標スケール: x={scale_x:.2f}, y={scale_y:.2f}")
        for name, pt in result["plot_points"].items():
            pt["x"] = int(pt["x"] * scale_x)
            pt["y"] = int(pt["y"] * scale_y)

    return result


def draw_plot(image_path, result, output_path):
    """評価結果のプロットポイントと基準線を写真上に描画して保存"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    points = result.get("plot_points", {})
    if not points:
        print("警告: プロットポイントが含まれていません。画像生成をスキップします。")
        return None

    # ポイント名と日本語ラベルの対応
    labels = {
        "head": "頭",
        "neck": "首",
        "shoulder": "肩",
        "waist": "腰",
        "pelvis": "骨盤",
        "knee": "膝",
    }
    point_order = ["head", "neck", "shoulder", "waist", "pelvis", "knee"]

    # 座標リストを構築
    coords = []
    for name in point_order:
        p = points.get(name)
        if p:
            coords.append((name, p["x"], p["y"]))

    if len(coords) < 2:
        print("警告: プロットポイントが不足しています。")
        return None

    # 画像サイズに応じた描画サイズ
    w, h = img.size
    dot_r = max(8, w // 150)       # 点の半径
    line_w = max(3, w // 400)      # 線の太さ
    font_size = max(16, w // 60)   # フォントサイズ

    # フォントの読み込み（日本語対応フォントを試行）
    font = None
    font_paths = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
        "/System/Library/Fonts/HiraginoSans-W4.otf",
        "/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, font_size)
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()

    # 6点を結ぶ線を描画（白、半透明感を出すために太線）
    xy_list = [(c[1], c[2]) for c in coords]
    for i in range(len(xy_list) - 1):
        draw.line([xy_list[i], xy_list[i + 1]], fill=(255, 255, 255, 230), width=line_w)

    # 頭〜膝の基準直線を描画（黄色の破線風 = 細い線）
    if len(xy_list) >= 2:
        x0, y0 = xy_list[0]
        x1, y1 = xy_list[-1]
        draw.line([(x0, y0), (x1, y1)], fill=(255, 255, 0, 180), width=max(2, line_w // 2))

    # 各ポイントに赤い点とラベルを描画
    for name, x, y in coords:
        draw.ellipse(
            [x - dot_r, y - dot_r, x + dot_r, y + dot_r],
            fill=(255, 50, 50),
            outline=(255, 255, 255),
            width=2,
        )
        label = labels.get(name, name)
        draw.text((x + dot_r + 4, y - font_size // 2), label, fill=(255, 255, 255), font=font)

    # 判定結果を左上に表示
    rating = result.get("overall_rating", "")
    rating_mark = {"良好": "○", "やや注意": "△", "要改善": "×"}
    mark = rating_mark.get(rating, "")
    header = f"SleepAlign  {mark} {rating}"
    draw.rectangle([(0, 0), (w, font_size + 16)], fill=(0, 0, 0, 180))
    draw.text((10, 6), header, fill=(255, 255, 255), font=font)

    img.save(output_path, quality=95)
    return output_path


def display_result(result):
    """評価結果を見やすく表示"""
    print("=" * 50)
    print("  SleepAlign 寝姿勢評価レポート")
    print("=" * 50)

    pos = result.get('sleeping_position', '不明')
    print(f"\n■ 寝姿勢: {pos}")
    print(f"■ 体軸中心線: {result['center_line_shape']}")
    print(f"  {result['center_line_summary']}")

    if 'key_observation' in result:
        ko = result['key_observation']
        print(f"\n■ 主要所見:")
        print(f"  問題: {ko['primary_issue']}")
        print(f"  原因: {ko['cause']}")
        print(f"  影響: {ko['effect']}")

    print("\n■ 区間別評価:")
    section_names = {
        "head_to_neck": "頭〜首",
        "neck_to_shoulder": "首〜肩",
        "shoulder_to_waist": "肩〜腰",
        "waist_to_pelvis": "腰〜骨盤",
        "pelvis_to_knee": "骨盤〜膝",
    }
    for key, name in section_names.items():
        s = result["sections"][key]
        note = f" ({s['note']})" if s.get("note") else ""
        print(f"  {name:8s}: {s['tilt']}{note}")

    print(f"\n■ マットレスとの関係:")
    print(f"  浮き:     {result['floating_areas']}")
    print(f"  沈み込み: {result['sinking_areas']}")
    print(f"  首の連続性: {result['neck_continuity']}")

    dev = result["straight_line_deviation"]
    print(f"\n■ 直線性からのズレ:")
    print(f"  {dev['description']}")
    print(f"  最大ズレ区間: {dev['worst_section']} ({dev['deviation_direction']})")

    rating_mark = {"良好": "○", "やや注意": "△", "要改善": "×"}
    mark = rating_mark.get(result["overall_rating"], "?")
    print(f"\n■ 総合判定: {mark} {result['overall_rating']}")
    print(f"  {result['mattress_feedback']}")

    if result.get("recommendation"):
        print(f"\n■ アドバイス:")
        print(f"  {result['recommendation']}")

    print("\n" + "=" * 50)


def main():
    if len(sys.argv) < 2:
        print("使い方: python3 evaluate.py 写真のパス [--debug]")
        print("例:     python3 evaluate.py photo.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    debug = "--debug" in sys.argv

    try:
        result = evaluate(image_path, debug=debug)
    except anthropic.AuthenticationError:
        print("エラー: APIキーが正しくありません。")
        print("環境変数 ANTHROPIC_API_KEY を確認してください。")
        sys.exit(1)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {image_path}")
        sys.exit(1)

    if result:
        display_result(result)

        # プロット画像を生成
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_dir = os.path.join(os.path.dirname(image_path) or ".", "results")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}_plot.jpg")
        saved = draw_plot(image_path, result, output_path)
        if saved:
            print(f"\nプロット画像を保存しました: {saved}")


if __name__ == "__main__":
    main()
