# Fire Ash no navegador — estudo de compatibilidade

Projeto separado do Alvorada. Origem: `~/Downloads/Pokemon Fire Ash 3.7.zip`; o ZIP permanece intacto. A cópia de trabalho está em `originais/fire-ash-3.7/`, fora do controle de versão.

## O que já funciona

- Leitura de Marshal/RXDATA sem executar Ruby. Foram lidos 996 mapas, 14.898 eventos e 27.896 páginas de evento; nenhum mapa falhou na leitura.
- Inventário dos 402 blocos de scripts Ruby e das chamadas de batalha. São cerca de 144 mil linhas; não foram traduzidas para JavaScript.
- Prévia de Pallet Town, Route 1 e casa de Ash em Canvas, com blocos e sprites originais, prioridades de desenho, autotiles animados, colisão de terreno e controle por toque.
- Atlas em páginas de até 256 × 512, com pixels idênticos ao original. Só entram as páginas usadas pela área carregada. O mapa exterior original usa uma imagem de 256 × 20.032.
- Figurino de Kanto de Ash (`trchar000_1`) na prévia. O arquivo `trchar000` sem sufixo representa outro personagem; figurinos do jogo completo precisam acompanhar o estado original da história.

Não é o Fire Ash completo convertido. Os eventos visuais da prévia representam páginas sem condições, sem executar seus comandos. Não há diálogos, missões, gatilhos, saves, encontros ou combate funcionando nesta prévia. NPCs visuais ainda não oferecem interação ou colisão. A casa também contém personagens de eventos que precisam da execução da história para aparecer na ocasião correta.

## Rodar e conferir

```sh
python3 tools/importar_area.py
python3 tools/testar_importacao.py
python3 -m http.server 8710 --bind 127.0.0.1 --directory web
# Em outro terminal, com o servidor ativo:
node tools/testar_navegador.mjs
```

Endereço local: http://127.0.0.1:8710/. Capturas reais em `docs/shots/`. Chrome em 844 × 390, DPR 2, com áudio desligado; Safari e iPhone físico ainda não testados.

## Como preservar o jogo inteiro

O Fire Ash usa RPG Maker XP/Essentials, Ruby e arquivos RXDATA. O Alvorada usa JavaScript/Pixi. Preservar a experiência exige uma camada de compatibilidade dos eventos e sistemas, além da importação dos desenhos. Não basta trocar as imagens de uma batalha por turnos.

1. Executar o início original, portas, diálogos, condições, variáveis e switches; conferir contra o jogo original. O leitor mantém todos os comandos, mas o navegador ainda não os executa.
2. Criar um adaptador de batalha com estado de entrada explícito: equipe, níveis, golpes, habilidades, itens e contexto da batalha. Não substituir os dados do Fire Ash pelos do Alvorada.
3. Integrar o motor de combate em tempo real do Alvorada, sem carregar um segundo jogo completo num iframe. Controles, recarga compartilhada, esquiva e PP seguem o formato aprovado.
4. Devolver vitória, derrota, fuga ou captura ao evento que chamou a batalha, com atualização de PS, estados, experiência e itens. Só então avançar os switches da história. Testar um selvagem e um treinador que libera uma passagem.
5. Conferir batalhas duplas, desafios, derrotas obrigatórias, evoluções e mecânicas específicas antes de expandir. Há milhares de chamadas de batalha e de introdução/encerramento de treinadores.
6. Validar todos os caminhos de progressão e saves, carregar recursos por área e medir memória no Safari de um iPhone real. Um teste Chrome em resolução móvel não prova compatibilidade iOS.

A alternativa de executar Ruby/RGSS no navegador também requer avaliação: o projeto [mkxp-web-jspi](https://github.com/Dim145/mkxp-web-jspi) documenta incompatibilidade atual com navegadores móveis e trabalho adicional para jogos com scripts de Essentials. Não é uma solução já validada para este Fire Ash.

Créditos e arquivos de autoria do Fire Ash foram preservados na cópia original. Nenhum script do ZIP foi executado, e a publicação contém somente a prévia de exploração.

## Publicação da prévia

Endereço: https://medtechbr.com.br/fire-ash-web/

O GitHub Pages publica apenas `web/`. O ZIP, a cópia integral do Fire Ash e os arquivos executáveis ficam de fora. Os créditos originais acompanham o pacote em `web/creditos.txt`. O fluxo de publicação confere o JavaScript, a presença dos recursos e o tamanho das imagens antes do envio.

Para conferir o site após publicar:

```sh
URL_JOGO=https://medtechbr.com.br/fire-ash-web/ RESULTADOS=docs/publicacao/ node tools/testar_navegador.mjs
```
