# Mouse Pointer Theme Maker

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (Brasil)](README.pt-BR.md)

Transforme um personagem, mascote original ou ideia visual em um tema completo de ponteiros para macOS ou Windows — sempre com uma prévia nítida antes da instalação.

**Três estilos · Oito estados úteis · Um pacote específico para cada sistema**

## Galeria de temas

### Kaozai · Pixel retrô

Arte redesenhada como um jogo de 16/32 bits, não apenas uma imagem com filtro pixelado.

![Tema Kaozai em pixel retrô com oito estados](examples/kaozai-retro-pixel/preview.png)

### Kaomeier · Anime chibi

Uma versão Q polida, com capuz de urso azul, tranças azul-claras, uniforme e reações expressivas.

![Tema Kaomeier em anime chibi com oito estados](examples/kaomeier-chibi-anime/preview.png)

### Palace Drama · Expressão abstrata

Gestos exagerados, metáforas visuais e humor surreal mostram que o estilo abstrato vai além da paródia.

![Tema de drama palaciano em expressão abstrata com oito estados](examples/zhenhuan-abstract-expression/preview.png)

> A cruz vermelha indica o hotspot real para revisão. Ela nunca aparece no ponteiro instalado.

## Da ideia ao tema instalável

1. Escolha **macOS** ou **Windows 10/11**.
2. Envie o nome do personagem, um mascote original ou uma imagem de referência e escolha o estilo.
3. Revise uma prévia PNG em alta resolução com os oito estados.
4. Depois da aprovação, receba apenas o pacote do sistema escolhido.

Nenhum `.cape`, `.cur` ou arquivo de instalação é criado antes da aprovação explícita.

## Três estilos

| Estilo | Descrição |
| --- | --- |
| `retro-pixel` | Pixel art de 16/32 bits criada de propósito, com silhuetas nítidas e blocos de cor |
| `chibi-anime` | Personagens Q fofos, expressões grandes, linhas limpas e acessórios consistentes |
| `abstract-expression` | Exagero, metáfora visual, humor surreal, energia popular ou reações de meme |

Os oito estados são `normal`, `text`, `action`, `forbidden`, `busy`, `open_hand`, `resize_horizontal` e `resize_vertical`. As oito artes originais são expandidas para 51 identificadores no macOS e 15 funções no Windows.

## Instalar a Skill no Codex

```bash
git clone https://github.com/kaomei/mouse-pointer-theme-maker.git
mkdir -p ~/.codex/skills
cp -R mouse-pointer-theme-maker ~/.codex/skills/mouse-pointer-theme-maker
```

Reinicie o Codex e use, por exemplo:

```text
Use $mouse-pointer-theme-maker.
Computer: macOS
Style: retro-pixel
Theme: transforme meu mascote azul em um tema completo de ponteiros.
```

## Entrega por sistema

No macOS, a arte aprovada vira um tema `.cape`. A aplicação exige o projeto de terceiros [Mousecape SwiftUI Releases](https://github.com/sdmj76/Mousecape-swiftUI/releases). Este repositório nunca inclui ou redistribui o aplicativo Mousecape. Consulte a licença própria do Mousecape, especialmente em fluxos comerciais.

No Windows, o resultado contém 15 arquivos `.cur`, um instalador PowerShell opcional para o usuário atual e um script de restauração. Não é necessário acesso de administrador.

## Qualidade e limitações

- Prévia PNG de 2440×1388 ou maior.
- Os cartões vêm da arte-fonte de 320×320; ícones de 32×32 nunca são ampliados.
- Hotspots, margens transparentes, cortes e linhas residuais são validados.
- macOS e Windows são sempre empacotados separadamente.
- Alguns aplicativos desenham seus próprios ponteiros e podem não mostrar estados pouco frequentes.
- Publique apenas imagens que você tenha o direito de usar. Informar o nome de um personagem não representa licença oficial.

## Contribuição / Licença

Issues e Pull Requests são bem-vindos. Não adicione binários de aplicativos de terceiros e execute `python3 -m unittest discover -s tests -v`.

O código da Skill usa a [MIT License](LICENSE). A arte dos personagens de exemplo continua sujeita aos direitos de seus criadores e é exibida apenas como demonstração.
