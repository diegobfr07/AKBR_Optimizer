# ⚡ Aika Optimizer Pro v3.0 Master Class

**Interface Premium, Motor de Performance Extrema, Game Booster Furtivo e Extrator JIT nativo para Aika Online.**

O AKOptimizer Pro atingiu o nível **Master Class**. Deixamos de ser apenas um script para nos tornarmos um **Software de Otimização de Nível Enterprise**. Desenvolvido em Python com arquitetura transacional, ele agora conta com uma Interface Gráfica (GUI) responsiva em PySide6, isolamento de núcleo no Kernel, desativação de MPO e injeção de mods Hot-Swap.

---

## 🚀 O que mudou na v3.0 Master Class?

* **Interface Gráfica Premium (Neon UI)** Interface moderna, estilo macOS, com botões interativos, animações em tempo real e terminal integrado.
* **Game Booster Inteligente** Um novo motor agressivo que monitora processos em segundo plano, hiberna aplicações que consomem RAM (via `EmptyWorkingSet`) e encerra bloatwares e serviços inúteis assim que a otimização é iniciada.
* **Isolamento de CPU & Desativação de MPO** Otimizações profundas que isolam o processo do Aika do Core 0 (núcleo ocupado pelo Windows) e desligam o Multiplane Overlay (MPO), eliminando os famosos *stutters* (engasgos) e *flickers* do DirectX 9.
* **Extrator de Texturas (.JIT) Nativo** Ferramenta inédita capaz de quebrar a criptografia das texturas da Joy Impact Engine. Extrai texturas DDS embutidas (JT31/JT33/JT35) e converte instantaneamente o complexo formato JT20 (8-bits) para TGA (32-bits).
* **Tray Icon (Modo Furtivo)** O Optimizer agora pode ser minimizado para a bandeja do sistema (perto do relógio). Ele fica rodando de forma invisível, garantindo a performance sem poluir a sua tela.
* **Timer Resolution a 1ms** Injeção direta na API de multimídia do Windows (`winmm.dll`) para cravar o tempo de resposta do sistema em 1 milissegundo, garantindo input-lag zero.

---

## 🛠️ Performance Engine (v3.0)

| Otimização | O que faz | Nível |
| --- | --- | --- |
| **Turbo Booster Agressivo** | Mata bloatwares, limpa memória RAM e para serviços pesados invisivelmente | 🚀 Sistema |
| **Isolar CPU (Afinidade)** | Força o jogo a desocupar o núcleo 0, focando o processamento em núcleos livres | 🧠 CPU |
| **Desativar MPO** | Remove o Multiplane Overlay do Windows, curando problemas visuais crônicos no DX9 | 🖥️ GPU |
| **Timer Resolution 1ms** | Injetado no Kernel para zerar o delay de teclado e mouse em PvP | ⌨️ Input |
| **TCP NoDelay + Throttling** | Reduz a latência de pacotes (TCP) e remove os limites artificiais de banda | 🔧 Rede |
| **Modo Tela Cheia Exclusivo** | Desliga a Game Bar nativamente para forçar renderização máxima | ⚡ Energia |
| **Limpeza de Cache Profunda** | Apaga caches antigos da NVIDIA/AMD forçando a fluidez das *skills* | 🗑️ Disco |

---

## 📦 Injetor de Mods & Áudio (Hot-Swap)

* **Indexação JSON:** O sistema varre a pasta do jogo silenciosamente e cria um mapa inteligente dos arquivos (`aika_index.json`).
* **Hot-Swapping:** Pode injetar texturas e áudios com o jogo **ABERTO** instantaneamente.
* **Conversor de Áudio Nativo:** Suporte a arquivos MP3/WAV, convertendo e injetando no formato `.bin` que o jogo reconhece.
* **Backup Blindado:** Todo arquivo substituído recebe um backup e tem suas permissões (`chmod`) tratadas atomaticamente.

---

## 🛡️ Central de Restauração (Rollback Total)

Nenhuma alteração é permanente. O sistema trabalha com **Transações Atômicas** (`TransacaoSistema`). Na aba **🛡️ Segurança**, você encontra duas frentes de defesa:

1. **🖥️ DESFAZER TWEAKS DE SISTEMA E BOOSTER** - Restaura os serviços parados do Windows, reverte as prioridades de RAM/CPU, redefine o plano de energia e limpa o DNS usando um Snapshot gravado antes da otimização.
2. **🎮 DESFAZER MODIFICAÇÕES NO JOGO** - Processo inteligente em lotes (*batching*) que restaura os arquivos `.bin`, `.jit` e de interface originais do jogo sem congelar o uso do seu Disco Rígido.

---

## 🔒 Segurança e Transparência (VirusTotal)

O Aika Optimizer v3.0 realiza modificações avançadas no Registro do Windows, encerra processos nativos (Booster) e ajusta o Kernel do sistema operacional para alta performance.

Por ser compilado via **PyInstaller** e empacotado profissionalmente via **Inno Setup** sem uma Assinatura Digital Corporativa (que possui um alto custo em dólar), ferramentas heurísticas ultra-sensíveis geridas por IA (como o *DeepInstinct*) podem acusar Falsos Positivos de comportamento.

**✅ Resultados Oficiais do VirusTotal (1/69):**
O executável foi **APROVADO E CERTIFICADO COMO LIMPO** por 68 dos 69 maiores motores de antivírus do mundo, incluindo **Microsoft Defender, Kaspersky, BitDefender, Malwarebytes e Avast**. 

🛡️ **[CLIQUE AQUI PARA VER O RELATÓRIO OFICIAL DO VIRUSTOTAL DIRETAMENTE NO SITE](https://www.virustotal.com/gui/file/6ea82e5a15ea22f944dc8d29ed6386731ce54ee30588d3fb0983b5af53216852)**

**Como auditar por conta própria:**
1. **Código 100% Aberto:** Audite cada linha deste repositório. Não há backdoors, nem coleta de dados.
2. **Compile você mesmo:** Faça o download dos fontes e crie seu próprio `.exe` usando Python 3.14.

---

## 🚀 Como Baixar, Instalar e Usar (v3.0)

Para evitar que navegadores (como o Chrome) ou o Google Drive bloqueiem o download por falso-positivo, o instalador oficial foi compactado com uma senha de segurança. Siga o passo a passo:

1. Baixe o arquivo **`Instalador_Aika_Optimizer_V3.zip`** na aba **Releases** aqui no GitHub.
2. Extraia o arquivo utilizando a senha: **`123`**
3. Execute o instalador extraído e siga o assistente (O sistema já pedirá permissão de Administrador automaticamente para aplicar os ajustes no Registro).
4. Após instalar, abra o **Aika Optimizer V3.0** diretamente pelo atalho estilizado criado na sua Área de Trabalho.
5. Clique no botão gigante roxo **⚡ INICIAR OTIMIZAÇÃO GLOBAL** na aba Performance.
6. **A mágica:** O software fará um backup silencioso do seu PC, limpará a RAM, ativará o Timer de 1ms e abrirá o jogo sozinho!
7. **Minimize o Optimizer** (ele ficará escondido na bandeja do sistema, perto do relógio) e vá destruir no PvP com input-lag zero!

---

## 👨‍💻 Desenvolvedor

**@diegobfr07** *Arquitetura de Software | Especialista em Otimização de Sistemas e Engenharia Reversa.*

---

## 📜 Licença

MIT License — Estude, modifique e compartilhe o projeto livremente, sempre mantendo os devidos créditos aos desenvolvedores originais.

---

*Versão Oficial V3.0 Master Class — Testado em Windows 10 e Windows 11.*
