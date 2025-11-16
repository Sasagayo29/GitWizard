# GitWizard

![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/PySide6-Qt%206-teal?style=for-the-badge&logo=qt)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Um cliente Git de desktop moderno, leve e poderoso, construído com Python e PySide6, inspirado na elegância visual do GitKraken e na navegação limpa do VSCode.

---

## 🌟 Visão Geral

Este projeto começou como um simples script para automatizar tarefas do Git e evoluiu para um cliente Git gráfico completo. O objetivo principal é fornecer 95% das funcionalidades de clientes pesados (como GitKraken ou Sourcetree) numa aplicação Python leve, limpa e "despoluída", com foco num fluxo de trabalho visual e intuitivo.

A aplicação é multithreaded para garantir que a interface nunca congele durante operações de rede (como clone, pull, push) e possui um grafo de commits personalizado desenhado com curvas de Bézier.

### 🖼️ Screenshot (Placeholder)

> **Nota:** Adicione aqui um screenshot da sua aplicação em ação! Um bom screenshot é a parte mais importante de um README de UI.

![[INSIRA AQUI UM SCREENSHOT DO GITWIZARD]](https://i.imgur.com/gYf4g4j.png)

## ✨ Funcionalidades Principais

Este não é um cliente Git "simples". Ele implementa todo o fluxo de trabalho profissional, desde o "init" até ao "rebase".

### 🧭 Navegação e UI

* **Tema Moderno:** Um tema "dark mode" completo, inspirado no GitKraken/VSCode, construído de raiz com QSS.
* **Navegação em "Rail":** Interface limpa com uma barra de navegação lateral de ícones (semelhante ao VSCode) que economiza espaço.
* **Layouts Flexíveis:** Todos os painéis em todas as secções usam divisores (`QSplitter`) que permitem ao utilizador redimensionar e organizar o seu espaço de trabalho.
* **Visualizador de Diff:** Um painel de "diff" integrado nas secções "Commit" e "Histórico".

### 📊 Grafo de Commits Visual (A Alma do Projeto)

* **Grafo Personalizado:** Um widget de histórico de commits totalmente personalizado, desenhado com `QPainter`.
* **Visualização de Todas as Branches:** O algoritmo de layout analisa `git --all` para mostrar o histórico completo de todas as branches e merges.
* **Curvas de Bézier:** As linhas de merge são desenhadas com curvas de Bézier suaves para um visual limpo e profissional, em vez de linhas retas cruzadas.
* **Interatividade:**
    * Clique-esquerdo num commit para o selecionar e ver os seus detalhes e "diff" completo.
    * Clique-direito num commit para abrir um menu de contexto.

### 🧰 Conjunto Completo de Ferramentas Git

* **Fluxo Essencial:** **Clone**, **Stage** (Adicionar), **Commit**, **Pull** e **Push**.
* **Gestão de Branches:**
    * Listar branches locais e remotas.
    * Criar, Deletar (local e remoto) e Mudar de Branch (`checkout`).
    * **Checkout Remoto:** Clique duplo numa branch remota para criar automaticamente a branch local correspondente.
    * **Merge** com deteção de conflito.
* **Gestão de Stash (Completa):**
    * Uma página dedicada para o **Stash**.
    * **Guardar** alterações (incluindo ficheiros não rastreados).
    * **Listar** todos os stashes guardados.
    * **Ver o Diff** de qualquer stash selecionado.
    * **Aplicar** ou **Apagar (Drop)** stashes específicos.
* **Gestão de Tags:**
    * Página dedicada para **Tags**.
    * Listar todas as tags.
    * Ver detalhes de tags (anotadas ou leves).
    * Criar e apagar tags locais.
* **Gestão de Remotes:**
    * Página dedicada para **Remotes**.
    * Listar, adicionar e remover múltiplos repositórios remotos (ex: `origin`, `upstream`).
* **Ferramentas "Power-User":**
    * **Rebase Interativo (`rebase -i`):** Uma janela de diálogo que permite reordenar, "esmagar" (`squash`), renomear (`reword`) ou apagar (`drop`) commits.
    * **Deteção de Conflito:** Uma barra de aviso persistente (vermelha) aparece no topo da aplicação se um `merge`, `pull` ou `rebase` falhar.
    * **Abortar Operação:** Um botão "Abortar" aparece na barra de conflito, permitindo executar `git merge --abort` ou `git rebase --abort` com segurança.

## 🛠️ Stack de Tecnologia

* **Python 3.10+**
* **PySide6 (Qt 6):** Para toda a interface gráfica de utilizador (GUI).
* **GitPython:** A biblioteca Python usada para interagir com a lógica do Git.
* **Subprocess:** Usado para operações complexas (como Rebase) que exigem controlo de ambiente.
* **QSS (Qt Style Sheets):** Para a criação do tema "dark mode".

## 🚀 Começar (Getting Started)

Para executar este projeto localmente:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/GitWizard.git](https://github.com/seu-usuario/GitWizard.git)
    cd GitWizard
    ```

2.  **Crie um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    ```
    * No Windows: `.\venv\Scripts\activate`
    * No macOS/Linux: `source venv/bin/activate`

3.  **Instale as dependências:**
    ```bash
    pip install PySide6 GitPython
    ```

4.  **Execute a aplicação:**
    *(Altere `gitAss_v2.py` para o nome final do seu ficheiro, ex: `main.py` ou `git_wizard.py`)*
    ```bash
    python gitAss_v2.py
    ```

## 📄 Licença

Este projeto está licenciado sob a Licença MIT. Veja o ficheiro `LICENSE` para mais detalhes.

