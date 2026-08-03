# Mouse Pointer Theme Maker

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (Brasil)](README.pt-BR.md)

캐릭터, 오리지널 IP 또는 시각적 아이디어를 macOS / Windows용 완성형 마우스 포인터 테마로 만듭니다. 설치 전에 항상 고해상도 전체 미리보기를 먼저 확인합니다.

**3가지 스타일 · 실용적인 8가지 상태 · 운영체제별 패키지**

## 테마 갤러리

### Kaozai · 레트로 픽셀

단순한 픽셀 필터가 아니라 16/32비트 게임 그래픽 방식으로 새롭게 설계했습니다.

![Kaozai 레트로 픽셀 8상태 테마](examples/kaozai-retro-pixel/preview.png)

### Kaomeier · 치비 애니메이션

파란 곰 모자, 연한 파란색 양갈래 머리, 교복을 유지한 귀엽고 표정이 풍부한 Q버전입니다.

![Kaomeier 치비 애니메이션 8상태 테마](examples/kaomeier-chibi-anime/preview.png)

### Palace Drama · 추상 표현

과장된 동작, 시각적 은유, 초현실적인 유머로 추상 스타일의 폭을 보여 줍니다.

![궁중 드라마 추상 표현 8상태 테마](examples/zhenhuan-abstract-expression/preview.png)

> 빨간 십자가는 실제 핫스팟 검토용이며 설치되는 포인터 이미지에는 포함되지 않습니다.

## 사용 흐름

1. **macOS** 또는 **Windows 10/11** 선택.
2. 캐릭터 이름, 오리지널 마스코트 또는 참고 이미지와 스타일 제공.
3. 8가지 상태가 담긴 고해상도 PNG 확인.
4. 승인 후 선택한 운영체제의 패키지만 받기.

승인 전에는 `.cape`, `.cur` 또는 설치 압축 파일을 만들지 않습니다.

## 3가지 스타일

| 스타일 | 설명 |
| --- | --- |
| `retro-pixel` | 선명한 실루엣과 의도적인 색 블록을 가진 16/32비트 픽셀 아트 |
| `chibi-anime` | 큰 표정, 깨끗한 선, 통일된 소품의 귀여운 Q버전 캐릭터 |
| `abstract-expression` | 과장, 시각적 은유, 초현실적 유머, 밈 같은 반응 |

기본 상태는 `normal`, `text`, `action`, `forbidden`, `busy`, `open_hand`, `resize_horizontal`, `resize_vertical`입니다. 8개 원본 그림은 macOS 51개 식별자와 Windows 15개 역할로 확장됩니다.

## Codex Skill 설치

```bash
git clone https://github.com/kaomei/mouse-pointer-theme-maker.git
mkdir -p ~/.codex/skills
cp -R mouse-pointer-theme-maker ~/.codex/skills/mouse-pointer-theme-maker
```

Codex를 다시 시작한 뒤 다음과 같이 요청하세요.

```text
Use $mouse-pointer-theme-maker.
Computer: Windows
Style: abstract-expression
Theme: 이 참고 캐릭터로 완성형 포인터 테마를 만들어 주세요.
```

## 운영체제별 제공 방식

macOS에서는 승인된 그림을 `.cape`로 만듭니다. 적용하려면 타사 [Mousecape SwiftUI Releases](https://github.com/sdmj76/Mousecape-swiftUI/releases)가 필요합니다. 이 저장소는 Mousecape 앱을 포함하거나 재배포하지 않습니다. 상업적 사용을 포함하여 Mousecape 자체 라이선스를 확인하세요.

Windows에서는 15개의 `.cur`, 현재 사용자용 PowerShell 설치 스크립트, 복원 스크립트를 제공합니다. 관리자 권한은 필요하지 않습니다.

## 품질과 제한

- 미리보기는 2440×1388 이상의 PNG입니다.
- 32×32 아이콘을 확대하지 않고 320×320 원본으로 카드를 만듭니다.
- 핫스팟, 투명 여백, 잘림과 잔여 선을 검사합니다.
- macOS와 Windows는 별도로 패키징합니다.
- 일부 앱은 자체 포인터를 사용하므로 낮은 빈도의 상태가 나타나지 않을 수 있습니다.
- 공개 권한이 있는 이미지만 사용하세요. 캐릭터 이름 지정은 공식 라이선스를 의미하지 않습니다.

## 기여 / 라이선스

Issue와 Pull Request를 환영합니다. 타사 앱 바이너리를 추가하지 말고 `python3 -m unittest discover -s tests -v`를 실행하세요.

Skill 소스는 [MIT License](LICENSE)로 제공됩니다. 예시 캐릭터 이미지는 각 제작자의 권리에 따르며 기능 데모 용도입니다.
