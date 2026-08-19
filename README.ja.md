# Mouse Pointer Theme Maker

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (Brasil)](README.pt-BR.md)

キャラクター、オリジナル IP、またはイメージを、macOS / Windows 用の完全なマウスポインターテーマに変換します。インストール前に、必ず高解像度プレビューを確認できます。

**3つのスタイル · 実用的な8状態 · OS別パッケージ**

## テーマギャラリー

### Kaozai · レトロピクセル

単純なピクセル化フィルターではなく、16/32-bit ゲーム素材として再設計した作品です。

![Kaozai レトロピクセル 8状態テーマ](examples/kaozai-retro-pixel/preview.png)

### Kaomeier · ちびアニメ

青いクマ帽子、ライトブルーの三つ編み、制服を活かした、表情豊かな Q 版セットです。

![Kaomeier ちびアニメ 8状態テーマ](examples/kaomeier-chibi-anime/preview.png)

### Palace Drama · アブストラクト表現

誇張、視覚的メタファー、シュールなユーモアを使った表現スタイルです。

![宮廷ドラマ アブストラクト表現 8状態テーマ](examples/zhenhuan-abstract-expression/preview.png)

> 赤い十字はホットスポット確認用です。実際のポインター画像には含まれません。

## 使い方

1. **macOS** または **Windows 10/11** を選択。
2. キャラクター名、オリジナル画像、参考画像とスタイルを指定。
3. 8状態をまとめた高解像度 PNG を確認。
4. 承認後、選択した OS のパッケージだけを受け取る。

承認前に `.cape`、`.cur`、インストールアーカイブは作成しません。

## 3つのスタイル

| スタイル | 内容 |
| --- | --- |
| `retro-pixel` | 輪郭と色面を意図的に設計した 16/32-bit ピクセルアート |
| `chibi-anime` | 大きな表情、きれいな線、統一アクセサリーのちびキャラ |
| `abstract-expression` | 誇張、視覚的メタファー、シュールな笑い、ミーム的反応 |

8つの基本状態は `normal`、`text`、`action`、`forbidden`、`busy`、`open_hand`、`resize_horizontal`、`resize_vertical` です。これらは macOS の51識別子と Windows の15役割に展開されます。

## Codex Skill のインストール

```bash
git clone https://github.com/kaomei/mouse-pointer-theme-maker.git
mkdir -p ~/.codex/skills
cp -R mouse-pointer-theme-maker ~/.codex/skills/mouse-pointer-theme-maker
```

Codex を再起動し、次のように依頼します。

```text
Use $mouse-pointer-theme-maker.
Computer: macOS
Style: chibi-anime
Theme: この参考キャラクターを完全なポインターテーマにしてください。
```

## OS別出力

macOS では承認済み画像を `.cape` にします。適用には第三者製の [Mousecape SwiftUI Releases](https://github.com/sdmj76/Mousecape-swiftUI/releases) が必要です。本リポジトリは Mousecape アプリを同梱・再配布しません。商用利用を含め、Mousecape 側のライセンスを確認してください。

Windows では15個の `.cur`、現在ユーザー用の PowerShell インストーラー、復元スクリプトを生成します。管理者権限は不要です。

## 品質と制限

- プレビューは 2440×1388 以上の PNG。
- 32×32 を拡大せず、320×320 の元画像からカードを生成。
- ホットスポットと透明な安全余白を検証。
- macOS と Windows は別々に出力。
- アプリによっては独自ポインターを描画するため、一部状態が表示されない場合があります。
- 権利を持つ画像だけを公開してください。キャラクター名の指定は公式許諾を意味しません。

## Contribution / License

Issue と Pull Request を歓迎します。第三者アプリのバイナリを追加せず、`python3 -m unittest discover -s tests -v` を実行してください。

Skill のソースコードは [MIT License](LICENSE) です。サンプルキャラクター画像は各制作者の権利に従い、機能デモとしてのみ掲載されています。
