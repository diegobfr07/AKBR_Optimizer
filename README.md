# ⚡ AKOPTIMIZER PRO | v1.0.0
**Otimizador de Alta Performance, Conversor Nativo e Injetor de Mods para Aika Online.**

O AKOptimizer Pro não é um simples limpador de lixeira. Ele é uma **Performance Engine** desenvolvida em Python que atua diretamente nas chaves de registro do Windows e nos protocolos de rede (TCP/IP) para extrair o máximo de FPS e a menor latência possível no Aika Online, focando na estabilidade.

## 🛠️ Recursos de Performance Engine
* **Otimização de Stack TCP/IP:** Desativa funções nativas do Windows (Autotuning e RSC) que causam oscilação de pacotes, estabilizando a latência.
* **Prioridade de Processo (IFEO):** Injeta prioridade máxima de CPU direto no registro do sistema, forçando o Windows a focar 100% no motor gráfico do jogo.
* **Input Zero Delay:** Zera o tempo de resposta do teclado no registro (`KeyboardDelay`), garantindo a execução instantânea de combos.
* **Injeção de CFG de Elite:** Aplica um perfil de configuração nativo otimizado para a guerra, reduzindo a renderização de elementos que causam gargalo.
* **Fix Visual Integrado:** Varredura e exclusão automática do arquivo `WeaponEff3.bin` para reduzir a poluição visual na tela.

## 🎵 Conversor de Áudio Nativo
Esqueça problemas de compatibilidade! O conversor embutido transforma seus arquivos `.mp3` ou `.wav` diretamente para a extensão `.bin` exigida pelo motor do jogo, permitindo que você altere os sons das skills e do ambiente com dois cliques sem corromper o cliente.

## 🎮 Auto Mods Inteligente
Um sistema de injeção atômica. Basta selecionar os seus arquivos modificados (texturas, cursores, skills) e o algoritmo varrerá todo o diretório do jogo substituindo os originais de forma segura e rápida.

## 🔒 Segurança e Transparência
Este projeto é **100% Open Source** (Código Aberto). Diferente de muitos otimizadores no mercado que são "caixas pretas", aqui todo o código fonte está disponível para auditoria. Você pode baixar os arquivos `.py`, analisar linha por linha e compilar o seu próprio executável. 

*(Devido às alterações necessárias no Registro do Windows para a otimização de CPU e Rede, alguns antivírus heurísticos podem apontar um "Falso Positivo". O link do escaneamento do executável oficial no VirusTotal encontra-se junto ao arquivo de download nas Releases).*

## 🚀 Como Usar
1. Faça o download do arquivo `AKBR_OPTIMIZER_PRO.zip` na aba lateral **Releases** (Senha para extrair: 123).
2. Extraia o arquivo e **Execute como Administrador** (Obrigatório para as funções de Registro e Rede funcionarem).
3. Selecione as otimizações desejadas e clique em "Executar Otimização".
4. Abra o jogo diretamente pelo painel do aplicativo!

---
*Desenvolvido por [@diegobfr07]*
