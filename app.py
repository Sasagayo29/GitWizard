import sys
import os
import shlex
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QFileDialog, QTextEdit, QMessageBox,
    QHBoxLayout, QStackedWidget, QListWidget, QListWidgetItem, QLabel,
    QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QHeaderView, QComboBox, 
    QToolBar, QStyle, QSplitter, QScrollArea,
    QMenu, QDialog, QDialogButtonBox  # --- CORREÇÃO: Readicionados ---
)
from PySide6.QtCore import Slot, Qt, QObject, Signal, QThread, QSize, QPoint, QRect
from PySide6.QtGui import (
    QFont, QAction, QIcon, QPainter, QColor, QPen, QBrush, QPainterPath
)
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
import datetime
import colorsys

# --- TEMA "GITKRAKEN-LITE" (sem alterações) ---
GITKRAKEN_LITE_QSS = """
QWidget {
    background-color: #282c34; color: #abb2bf;
    font-family: "Segoe UI", "Cantarell", "Helvetica Neue", sans-serif;
    font-size: 10pt; border: none;
}
QMainWindow { background-color: #282c34; }
QDialog { background-color: #282c34; }
QToolBar {
    background-color: #33373d; border-bottom: 1px solid #21252b;
    padding: 4px; spacing: 5px;
}
QToolBar::separator {
    background-color: #444851; width: 1px;
    margin-left: 5px; margin-right: 5px;
}
QToolBar QLabel { color: #abb2bf; padding-left: 3px; }
QPushButton {
    background-color: #3c4048; color: #f0f0f0;
    border: 1px solid #555555; border-radius: 4px; padding: 5px 10px;
}
QPushButton:hover { background-color: #4a4e57; border-color: #777777; }
QPushButton:pressed { background-color: #42464d; }
QPushButton:disabled { background-color: #33373d; color: #777777; }
QPushButton#CommitButton {
    background-color: #28a745; color: #ffffff;
    border-color: #2e8a42; font-weight: bold;
}
QPushButton#CommitButton:hover { background-color: #218838; }
QPushButton#MergeButton {
    background-color: #007acc; color: #ffffff; border-color: #005f9e;
}
QPushButton#MergeButton:hover { background-color: #006cbb; }
QPushButton#DeleteButton {
    background-color: #dc3545; color: #ffffff; border-color: #b02a37;
}
QPushButton#DeleteButton:hover { background-color: #c82333; }
QWidget#ConflictBar {
    background-color: #a63232;
    border-radius: 4px;
}
QWidget#ConflictBar QLabel {
    color: #ffffff;
    font-weight: bold;
    padding: 5px;
}
QWidget#ConflictBar QPushButton#AbortButton {
    background-color: #dc3545;
    color: #ffffff;
    border-color: #b02a37;
    font-weight: bold;
}
QWidget#ConflictBar QPushButton#AbortButton:hover {
    background-color: #c82333;
}
QListWidget#NavRail {
    background-color: #21252b; border-right: 1px solid #33373d;
    padding-top: 10px;
}
QListWidget#NavRail::item {
    padding: 10px; border: none; text-align: center; color: #abb2bf;
}
QListWidget#NavRail::item:hover { background-color: #33373d; }
QListWidget#NavRail::item:selected {
    background-color: #282c34; color: #ffffff;
    border-left: 3px solid #00aaff;
}
QLineEdit, QTextEdit, QListWidget, QTableWidget, QComboBox, QScrollArea {
    background-color: #21252b; color: #abb2bf;
    border: 1px solid #3c4048; border-radius: 4px; padding: 4px;
}
QListWidget#NavRail { border-radius: 0px; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border-color: #00aaff; }
QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #00aaff; color: #ffffff;
}
QListWidget#NavRail::item:selected {
    background-color: #282c34; color: #ffffff;
    border-left: 3px solid #00aaff;
}
QListWidget::item:hover, QTableWidget::item:hover {
    background-color: #33373d;
}
QListWidget#NavRail::item:hover { background-color: #33373d; }
QHeaderView::section {
    background-color: #33373d; color: #f0f0f0;
    padding: 4px; border: 1px solid #444851; font-weight: bold;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #33373d; border: 1px solid #555555;
    selection-background-color: #00aaff;
}
QTextEdit[readOnly="true"] {
    background-color: #1d1f21;
    font-family: "Consolas", "Monaco", "Menlo", monospace; font-size: 9.5pt;
}
QScrollBar:vertical {
    background: #282c34; width: 12px; margin: 0px;
}
QScrollBar::handle:vertical { background: #4a4e57; min-height: 20px; border-radius: 6px; }
QScrollBar::handle:vertical:hover { background: #5a5e67; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { background: #282c34; height: 12px; margin: 0px; }
QScrollBar::handle:horizontal { background: #4a4e57; min-width: 20px; border-radius: 6px; }
QScrollBar::handle:horizontal:hover { background: #5a5e67; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
QMessageBox { background-color: #3c3f41; }
QMessageBox QPushButton { min-width: 80px; }
QSplitter::handle { background-color: #33373d; }
QSplitter::handle:horizontal { width: 3px; }
QSplitter::handle:vertical { height: 3px; }
QSplitter::handle:hover { background-color: #00aaff; }
"""
# --- FIM DO TEMA ---


# --- Diálogo de Rebase (sem alterações) ---
class RebaseDialog(QDialog):
    def __init__(self, commits, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor de Rebase Interativo")
        self.setMinimumSize(700, 400)
        self.commits = commits
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Edite a sequência do rebase (do mais antigo para o mais novo):"))
        self.table = QTableWidget()
        self.setup_table()
        self.populate_table()
        layout.addWidget(self.table)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def setup_table(self):
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Ação", "Hash", "Mensagem"])
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.verticalHeader().setVisible(True)
        self.table.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.table.setDragDropOverwriteMode(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def populate_table(self):
        self.table.setRowCount(len(self.commits))
        for row, commit in enumerate(self.commits):
            combo = QComboBox()
            combo.addItems(["pick", "reword", "squash", "drop"])
            self.table.setCellWidget(row, 0, combo)
            hash_item = QTableWidgetItem(commit.hexsha[:7])
            hash_item.setFlags(hash_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, hash_item)
            msg_item = QTableWidgetItem(commit.summary)
            msg_item.setFlags(msg_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, msg_item)

    def get_rebase_sequence(self):
        sequence = []
        for row in range(self.table.rowCount()):
            action = self.table.cellWidget(row, 0).currentText()
            original_hash = self.table.item(row, 1).text()
            message = self.table.item(row, 2).text()
            original_commit = next((c for c in self.commits if c.hexsha.startswith(original_hash)), None)
            if not original_commit: continue
            sequence.append({
                "action": action,
                "hash": original_commit.hexsha,
                "summary": original_commit.summary,
                "new_message": message
            })
        return sequence
# --- FIM DO DIÁLOGO ---


# --- Classe CommitGraphWidget (sem alterações) ---
class CommitGraphWidget(QWidget):
    commit_selected = Signal(str)
    commit_context_menu_requested = Signal(str, QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph_data = []
        self.commit_rects = {}
        self.commit_lanes = {}
        self.selected_hash = None
        self.LANE_WIDTH = 20
        self.ROW_HEIGHT = 25
        self.DOT_SIZE = 10
        self.TEXT_X_OFFSET = 150
        self.lane_colors = self.generate_lane_colors(16)
        self.setMouseTracking(True)
        self.setMinimumHeight(self.ROW_HEIGHT * len(self.graph_data))

    def generate_lane_colors(self, count):
        colors = []
        for i in range(count):
            hue = i / count
            r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(hue, 0.8, 1.0)]
            colors.append(QColor(r, g, b))
        return colors

    def set_data(self, graph_data):
        self.graph_data = graph_data
        self.commit_rects.clear()
        self.commit_lanes.clear()
        self.selected_hash = None
        for item in graph_data:
            self.commit_lanes[item['commit'].hexsha] = item['lane']
        self.setMinimumHeight(self.ROW_HEIGHT * len(self.graph_data))
        self.update()

    def select_commit(self, commit_hash):
        self.selected_hash = commit_hash
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        commit_positions = {}
        
        for y_row, item in enumerate(self.graph_data):
            commit = item['commit']
            lane = item['lane']
            x = (lane * self.LANE_WIDTH) + (self.LANE_WIDTH / 2)
            y = (y_row * self.ROW_HEIGHT) + (self.ROW_HEIGHT / 2)
            commit_positions[commit.hexsha] = QPoint(int(x), int(y))

        lane_paths = {}
        
        for y_row, item in enumerate(self.graph_data):
            commit = item['commit']
            lane = item['lane']
            if commit.hexsha not in commit_positions: continue
            pos_child = commit_positions[commit.hexsha]
            
            if lane not in lane_paths: lane_paths[lane] = QPainterPath()
            path = lane_paths[lane]

            for i, parent in enumerate(commit.parents):
                if parent.hexsha in commit_positions:
                    pos_parent = commit_positions[parent.hexsha]
                    parent_lane = self.get_lane_for_hash(parent.hexsha)
                    if parent_lane == -1: continue

                    draw_path = path
                    if lane != parent_lane:
                        if parent_lane not in lane_paths:
                             lane_paths[parent_lane] = QPainterPath()
                        draw_path = lane_paths[parent_lane]

                    draw_path.moveTo(pos_child)
                    
                    if lane == parent_lane:
                        draw_path.lineTo(pos_parent)
                    else:
                        c1_x = pos_child.x()
                        c1_y = (pos_child.y() + pos_parent.y()) / 2
                        c2_x = pos_parent.x()
                        c2_y = (pos_child.y() + pos_parent.y()) / 2
                        draw_path.cubicTo(QPoint(c1_x, c1_y), QPoint(c2_x, c2_y), pos_parent)

        pen = QPen(); pen.setWidth(2)
        for lane, path in lane_paths.items():
            pen.setColor(self.lane_colors[lane % len(self.lane_colors)])
            painter.setPen(pen)
            painter.drawPath(path)
                
        for y_row, item in enumerate(self.graph_data):
            commit = item['commit']
            lane = item['lane']
            pos = commit_positions[commit.hexsha]
            color = self.lane_colors[lane % len(self.lane_colors)]
            pen = QPen(color); pen.setWidth(2)
            brush = QBrush(color)

            if commit.hexsha == self.selected_hash:
                pen.setColor(QColor("#00aaff")); pen.setWidth(3)
                brush.setColor(QColor("#00aaff"))
            
            painter.setPen(pen); painter.setBrush(brush)
            dot_rect = QRect(int(pos.x() - self.DOT_SIZE / 2), int(pos.y() - self.DOT_SIZE / 2), self.DOT_SIZE, self.DOT_SIZE)
            self.commit_rects[commit.hexsha] = dot_rect
            painter.drawEllipse(dot_rect)
            
            text_x = self.TEXT_X_OFFSET
            text_y = pos.y() + (self.fontMetrics().height() / 4)
            
            if commit.hexsha == self.selected_hash:
                pen.setColor(QColor("#FFFFFF"))
            else:
                pen.setColor(QColor("#abb2bf"))
            painter.setPen(pen)
            
            summary = commit.summary[:80]
            painter.drawText(QPoint(text_x + 10, text_y), summary)
            
            author_text = f"{commit.author.name} - {commit.hexsha[:7]}"
            author_rect = QRect(self.width() - 250, text_y - (self.ROW_HEIGHT/2), 240, self.ROW_HEIGHT)
            painter.drawText(author_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, author_text)

    def mousePressEvent(self, event):
        click_pos = event.position()
        clicked_hash = None
        for commit_hash, rect in self.commit_rects.items():
            if rect.contains(click_pos.toPoint()):
                clicked_hash = commit_hash
                break
        
        if clicked_hash:
            if event.button() == Qt.MouseButton.LeftButton:
                self.selected_hash = clicked_hash
                self.commit_selected.emit(clicked_hash)
                self.update()
                return
            
        super().mousePressEvent(event)
        
    def contextMenuEvent(self, event):
        click_pos = event.position()
        clicked_hash = None
        for commit_hash, rect in self.commit_rects.items():
            if rect.contains(click_pos.toPoint()):
                clicked_hash = commit_hash
                break
        
        if clicked_hash:
            self.commit_context_menu_requested.emit(clicked_hash, event.globalPos())
        else:
            super().contextMenuEvent(event)
        
    def get_lane_for_hash(self, commit_hash):
        return self.commit_lanes.get(commit_hash, -1)
# --- FIM DO WIDGET DO GRAFO ---


# --- Classe GitWorker (sem alterações) ---
class GitWorker(QObject):
    log_message = Signal(str)
    error_message = Signal(str, str)
    operation_finished = Signal()
    clone_finished = Signal(str)

    def __init__(self):
        super().__init__()
        self.repo_path = None

    @Slot(str)
    def set_repo_path(self, path): self.repo_path = path

    @Slot(str, str)
    def do_clone(self, url, path):
        try:
            self.log_message.emit(f"Clonando {url} para {path}...")
            Repo.clone_from(url, path)
            self.log_message.emit(">>> Clone concluído com sucesso!")
            self.clone_finished.emit(path)
        except GitCommandError as e: self.error_message.emit("Erro no Clone", str(e.stderr))
        except Exception as e: self.error_message.emit("Erro Inesperado", str(e))

    @Slot(str)
    def do_pull(self, remote_name):
        if not self.repo_path: return self.error_message.emit("Erro de Pull", "Caminho do repositório não definido.")
        try:
            repo = Repo(self.repo_path)
            if remote_name not in [r.name for r in repo.remotes]:
                 return self.error_message.emit("Erro de Pull", f"Remote '{remote_name}' não encontrado.")
            remote = repo.remotes[remote_name]
            self.log_message.emit(f"Executando 'git pull' de '{remote_name}' ({remote.url})...")
            remote.pull()
            self.log_message.emit(">>> Repositório atualizado com sucesso!")
            self.operation_finished.emit()
        except GitCommandError as e:
            if "conflict" in str(e.stderr).lower():
                self.error_message.emit("Conflito no Pull",
                                     "Ocorreu um conflito de merge durante o 'pull'.\n\nResolva os conflitos manualmente e faça 'commit' das alterações.")
            else: self.error_message.emit("Erro no Pull", str(e.stderr))
        except Exception as e: self.error_message.emit("Erro no Pull", str(e))
            
    @Slot(str, str)
    def do_push(self, remote_name, branch_name):
        if not self.repo_path: return self.error_message.emit("Erro de Push", "Caminho do repositório não definido.")
        try:
            repo = Repo(self.repo_path)
            if remote_name not in [r.name for r in repo.remotes]:
                 return self.error_message.emit("Erro de Push", f"Remote '{remote_name}' não encontrado.")
            self.log_message.emit(f"Executando 'git push --set-upstream {remote_name} {branch_name}'...")
            repo.git.push('--set-upstream', remote_name, branch_name)
            self.log_message.emit(">>> PUSH realizado com sucesso!")
            self.operation_finished.emit()
        except Exception as e:
            self.error_message.emit("Erro no Push", str(e))

    @Slot(str)
    def do_merge(self, branch_name):
        if not self.repo_path: return self.error_message.emit("Erro de Merge", "Caminho do repositório não definido.")
        try:
            repo = Repo(self.repo_path)
            self.log_message.emit(f"Tentando merge de '{branch_name}' em '{repo.active_branch.name}'...")
            repo.git.merge(branch_name)
            self.log_message.emit(">>> Merge concluído com sucesso!")
            self.operation_finished.emit()
        except GitCommandError as e:
            error_msg = str(e.stderr).lower()
            if "conflict" in error_msg or "conflicts" in error_msg:
                 self.error_message.emit("Conflito de Merge",
                                     "Ocorreu um conflito de merge.\n\n"
                                     "Por favor, resolva os conflitos no seu editor de código "
                                     "e faça 'commit' dos arquivos resolvidos.")
            else: self.error_message.emit("Erro de Merge", str(e.stderr))
        except Exception as e: self.error_message.emit("Erro de Merge", str(e))

    @Slot(str, list)
    def do_interactive_rebase(self, parent_hash, sequence):
        if not self.repo_path:
            return self.error_message.emit("Erro de Rebase", "Caminho do repositório não definido.")
        
        repo = Repo(self.repo_path)
        editor_script_path = os.path.join(self.repo_path, ".git", "REBASE_SCRIPT.py")
        
        try:
            self.log_message.emit("Preparando o rebase interativo...")
            
            todo_content = ""
            for item in sequence:
                action = item['action']
                hash_curto = item['hash'][:7]
                summary = item['summary']
                
                if action == "reword":
                    todo_content += f"pick {hash_curto} {summary}\n"
                    new_msg_safe = shlex.quote(item['new_message'])
                    todo_content += f"exec git commit --amend -m {new_msg_safe}\n"
                else:
                    todo_content += f"{action} {hash_curto} {summary}\n"
            
            editor_script_content = f"""
import sys
try:
    todo_file_path = sys.argv[1]
    new_content = \"\"\"{todo_content}\"\"\"
    with open(todo_file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    sys.exit(0)
except Exception as e:
    print(f"Erro no editor de rebase: {{e}}")
    sys.exit(1)
"""
            with open(editor_script_path, "w", encoding='utf-8') as f:
                f.write(editor_script_content)
                
            editor_command = f"\"{sys.executable}\" \"{editor_script_path}\""
            
            env = os.environ.copy()
            env["GIT_SEQUENCE_EDITOR"] = editor_command
            
            self.log_message.emit(f"Executando rebase -i a partir de {parent_hash[:7]}...")
            
            process = subprocess.run(
                ['git', 'rebase', '-i', parent_hash],
                cwd=self.repo_path,
                env=env,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            if process.returncode != 0:
                stderr = process.stderr
                if "conflict" in stderr.lower():
                    self.error_message.emit("Conflito de Rebase",
                                         "Ocorreu um conflito durante o rebase.\n\n"
                                         "Resolva os conflitos, 'stageie' os ficheiros, e depois execute 'git rebase --continue' manualmente no terminal.\n\n"
                                         "(A UI ainda não suporta 'rebase --continue')")
                else:
                    raise GitCommandError(process.args, process.returncode, process.stdout, process.stderr)
            else:
                self.log_message.emit(">>> Rebase concluído com sucesso!")
                self.operation_finished.emit()

        except GitCommandError as e:
            self.error_message.emit("Erro no Rebase", str(e.stderr))
        except Exception as e:
            self.error_message.emit("Erro Inesperado no Rebase", str(e))
        finally:
            if os.path.exists(editor_script_path):
                os.remove(editor_script_path)
# --- FIM DO WORKER ---


class GitApp(QMainWindow):
    request_clone = Signal(str, str)
    request_pull = Signal(str)
    request_push = Signal(str, str)
    request_merge = Signal(str)
    request_set_repo_path = Signal(str)
    request_interactive_rebase = Signal(str, list)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meu Assistente Git (v5.6 - Correção de Import)")
        self.setGeometry(100, 100, 1000, 750)
        self.repo = None 
        self.commits_na_tabela = []
        self.is_empty_repo = False 

        # Estilo para ícones
        self.icon_style = self.style()

        # Configuração da Thread
        self.thread = QThread()
        self.worker = GitWorker()
        self.worker.moveToThread(self.thread)
        self.worker.log_message.connect(self.log)
        self.worker.error_message.connect(self.show_error_message)
        self.worker.clone_finished.connect(self.on_clone_finished)
        self.worker.operation_finished.connect(self.on_operation_finished)
        self.request_clone.connect(self.worker.do_clone)
        self.request_pull.connect(self.worker.do_pull)
        self.request_push.connect(self.worker.do_push)
        self.request_merge.connect(self.worker.do_merge)
        self.request_set_repo_path.connect(self.worker.set_repo_path)
        self.request_interactive_rebase.connect(self.worker.do_interactive_rebase)
        self.thread.start()
        
        # Configurar a Barra de Ferramentas
        self.setup_toolbar()
        
        # Widget Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 1. Seção Superior (Controle do Repositório) ---
        repo_control_layout = QHBoxLayout()
        icon_clone = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        self.txt_url_clone = QLineEdit()
        self.txt_url_clone.setPlaceholderText("URL para Clonar...")
        self.btn_clone = QPushButton(icon_clone, " Clonar")
        self.btn_clone.clicked.connect(self.clonar_repositorio)
        repo_control_layout.addWidget(QLabel("Novo Repositório:"))
        repo_control_layout.addWidget(self.txt_url_clone)
        repo_control_layout.addWidget(self.btn_clone)
        repo_control_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        icon_browse = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        self.txt_local_path = QLineEdit()
        self.txt_local_path.setPlaceholderText("Caminho do repositório local...")
        self.btn_browse = QPushButton(icon_browse, " Abrir...")
        self.btn_browse.clicked.connect(self.abrir_repositorio)
        repo_control_layout.addWidget(QLabel("Repositório Local:"))
        repo_control_layout.addWidget(self.txt_local_path)
        repo_control_layout.addWidget(self.btn_browse)
        main_layout.addLayout(repo_control_layout)
        
        # --- Barra de Conflito ---
        self.conflict_bar = QWidget()
        self.conflict_bar.setObjectName("ConflictBar")
        conflict_layout = QHBoxLayout(self.conflict_bar)
        conflict_layout.setContentsMargins(10, 5, 5, 5)
        
        icon_warn = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        label_icon = QLabel()
        label_icon.setPixmap(icon_warn.pixmap(QSize(16, 16)))
        label_text = QLabel("CONFLITO DETETADO! Resolva os conflitos e faça 'Commit'.")
        
        conflict_layout.addWidget(label_icon)
        conflict_layout.addWidget(label_text)
        
        conflict_layout.addStretch()
        icon_abort = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        self.btn_abort_merge = QPushButton(icon_abort, " Abortar Merge")
        self.btn_abort_merge.setObjectName("AbortButton")
        self.btn_abort_merge.clicked.connect(self.abortar_merge)
        conflict_layout.addWidget(self.btn_abort_merge)
        main_layout.addWidget(self.conflict_bar)
        self.conflict_bar.setVisible(False)

        # --- 2. Layout "Rail" e "Stack" ---
        main_content_layout = QHBoxLayout()
        main_layout.addLayout(main_content_layout)
        
        self.nav_rail = QListWidget()
        self.nav_rail.setObjectName("NavRail")
        self.nav_rail.setFixedWidth(70)
        self.nav_rail.setViewMode(QListWidget.ViewMode.IconMode)
        self.nav_rail.setFlow(QListWidget.Flow.TopToBottom)
        self.nav_rail.setMovement(QListWidget.Movement.Static)
        self.nav_rail.setIconSize(QSize(32, 32))
        self.nav_rail.currentRowChanged.connect(self.change_page)
        main_content_layout.addWidget(self.nav_rail)
        
        self.stacked_content = QStackedWidget()
        main_content_layout.addWidget(self.stacked_content)
        
        # --- 4. Log de Saída ---
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setPlaceholderText("Logs das operações Git aparecerão aqui...")
        self.txt_output.setFixedHeight(150)
        main_layout.addWidget(self.txt_output)
        
        # --- CORREÇÃO: Listas de widgets movidas para ANTES de setup_pages_and_navigation ---
        self.repo_only_widgets = [
            self.stacked_content, self.nav_rail,
            self.btn_pull, self.btn_push, self.act_refresh,
        ]
        self.non_repo_widgets = [
            self.btn_clone, self.txt_url_clone, 
            self.btn_browse, self.txt_local_path
        ]
        self.all_interactive_widgets = self.repo_only_widgets + self.non_repo_widgets
        
        self.setup_pages_and_navigation()
        
        self.set_repo_open_state(False)

    def setup_pages_and_navigation(self):
        pages = [
            ("SP_FileIcon", "Commit", self.create_page_commit),
            ("SP_DirLinkIcon", "Branches", self.create_page_branches),
            ("SP_FileDialogDetailedView", "Histórico", self.create_page_history),
            ("SP_FileLinkIcon", "Tags", self.create_page_tags), # Ícone corrigido
            ("SP_DriveFDIcon", "Stash", self.create_page_stash),
            ("SP_ComputerIcon", "Remotes", self.create_page_remotes)
        ]
        
        for icon_name, tooltip, create_func in pages:
            page_widget = create_func()
            self.stacked_content.addWidget(page_widget)
            
            icon = self.icon_style.standardIcon(getattr(QStyle.StandardPixmap, icon_name))
            item = QListWidgetItem(icon, "")
            item.setToolTip(tooltip)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.nav_rail.addItem(item)
            
        self.nav_rail.setCurrentRow(0)
        
        self.repo_only_widgets.extend([
            self.list_tags, self.btn_create_tag, self.btn_delete_tag,
            self.txt_tag_name, self.txt_tag_message, self.log_tag_details,
            self.list_stashes, self.log_stash_details, self.btn_create_stash,
            self.btn_apply_stash, self.btn_drop_stash
        ])
        self.all_interactive_widgets = self.repo_only_widgets + self.non_repo_widgets

    @Slot(int)
    def change_page(self, row):
        self.stacked_content.setCurrentIndex(row)
        # 2=Histórico, 3=Tags, 4=Stash
        if (row == 2 or row == 3 or row == 4) and self.repo:
            if row == 2: self.atualizar_historico()
            if row == 3: self.atualizar_lista_tags()
            if row == 4: self.atualizar_lista_stashes()

    def setup_toolbar(self):
        toolbar = QToolBar("Ações Principais")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        icon_refresh = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        self.act_refresh = QAction(icon_refresh, "Atualizar Status (Refresh)", self)
        self.act_refresh.triggered.connect(self.atualizar_status_ui)
        toolbar.addAction(self.act_refresh)
        toolbar.addSeparator()
        
        pull_widget = QWidget()
        pull_layout = QHBoxLayout(pull_widget)
        pull_layout.setContentsMargins(5, 0, 5, 0)
        pull_layout.addWidget(QLabel("Puxar de:"))
        self.combo_pull_remote = QComboBox()
        pull_layout.addWidget(self.combo_pull_remote)
        icon_pull = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown)
        self.btn_pull = QPushButton(icon_pull, " PULL")
        self.btn_pull.clicked.connect(self.pull_repositorio)
        pull_layout.addWidget(self.btn_pull)
        toolbar.addWidget(pull_widget)

        push_widget = QWidget()
        push_layout = QHBoxLayout(push_widget)
        push_layout.setContentsMargins(5, 0, 5, 0)
        push_layout.addWidget(QLabel("Enviar para:"))
        self.combo_push_remote = QComboBox()
        self.combo_push_branch = QComboBox()
        push_layout.addWidget(self.combo_push_remote)
        push_layout.addWidget(self.combo_push_branch)
        icon_push = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_ArrowUp)
        self.btn_push = QPushButton(icon_push, " PUSH")
        self.btn_push.clicked.connect(self.push_repositorio)
        push_layout.addWidget(self.btn_push)
        toolbar.addWidget(push_widget)

    @Slot(bool)
    def set_ui_loading(self, loading):
        for widget in self.all_interactive_widgets:
            widget.setEnabled(not loading)
        
        if loading:
            self.log("... Operação em andamento ...")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            self.log(">>> Operação concluída.")
            QApplication.restoreOverrideCursor()
            for widget in self.non_repo_widgets:
                widget.setEnabled(True)
            if self.repo:
                self.set_repo_open_state(True)
            else:
                self.set_repo_open_state(False)
        
        if not loading and self.repo:
            self._check_conflict_state()

    @Slot(str)
    def on_clone_finished(self, path):
        self.carregar_repo(path)
        self.set_ui_loading(False)

    @Slot()
    def on_operation_finished(self):
        self.atualizar_status_ui()
        self.atualizar_lista_branches()
        self.atualizar_historico()
        self.atualizar_lista_remotes()
        self.atualizar_lista_tags()
        self.atualizar_lista_stashes()
        self.set_ui_loading(False)

    @Slot(str, str)
    def show_error_message(self, title, message):
        self.log(f"!!! ERRO: {title} !!!")
        self.log(message)
        QMessageBox.critical(self, title, message)
        self.set_ui_loading(False)
        if self.repo:
            self.atualizar_status_ui()

    def set_repo_open_state(self, enabled):
        for widget in self.repo_only_widgets:
            widget.setEnabled(enabled)
        
        if not enabled:
            self.setWindowTitle("Meu Assistente Git (v5.6) - Nenhum repositório carregado")
            
        if not enabled:
             self.conflict_bar.setVisible(False)

    def create_page_commit(self):
        page = QWidget()
        left_panel = QWidget()
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        staging_layout = QHBoxLayout()
        v_layout_unstaged = QVBoxLayout()
        v_layout_unstaged.addWidget(QLabel("Modificados (Unstaged):"))
        self.list_unstaged = QListWidget()
        self.list_unstaged.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_unstaged.itemSelectionChanged.connect(self.show_unstaged_diff)
        v_layout_unstaged.addWidget(self.list_unstaged)
        staging_layout.addLayout(v_layout_unstaged)
        v_layout_buttons = QVBoxLayout()
        v_layout_buttons.addStretch()
        icon_stage = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
        self.btn_stage = QPushButton(icon_stage, "")
        self.btn_stage.setToolTip("Adicionar ao Stage (git add)")
        self.btn_stage.clicked.connect(self.stage_arquivos)
        v_layout_buttons.addWidget(self.btn_stage)
        icon_unstage = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_ArrowLeft)
        self.btn_unstage = QPushButton(icon_unstage, "")
        self.btn_unstage.setToolTip("Remover do Stage (git reset)")
        self.btn_unstage.clicked.connect(self.unstage_arquivos)
        v_layout_buttons.addWidget(self.btn_unstage)
        v_layout_buttons.addStretch()
        staging_layout.addLayout(v_layout_buttons)
        v_layout_staged = QVBoxLayout()
        v_layout_staged.addWidget(QLabel("Prontos para Commit (Staged):"))
        self.list_staged = QListWidget()
        self.list_staged.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_staged.itemSelectionChanged.connect(self.show_staged_diff)
        v_layout_staged.addWidget(self.list_staged)
        staging_layout.addLayout(v_layout_staged)
        left_panel_layout.addLayout(staging_layout)
        commit_layout = QFormLayout()
        commit_layout.setContentsMargins(0, 5, 0, 0)
        self.txt_commit_msg = QLineEdit("Commit...")
        icon_commit_btn = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self.btn_commit = QPushButton(icon_commit_btn, " Commitar")
        self.btn_commit.setObjectName("CommitButton")
        self.btn_commit.clicked.connect(self.commitar_mudancas)
        commit_layout.addRow("Mensagem:", self.txt_commit_msg)
        commit_layout.addRow(self.btn_commit)
        left_panel_layout.addLayout(commit_layout)
        right_panel = QWidget()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.addWidget(QLabel("Visualizador de Diff:"))
        self.diff_viewer = QTextEdit()
        self.diff_viewer.setReadOnly(True)
        self.diff_viewer.setFont(QFont("Monospace", 9))
        self.diff_viewer.setPlaceholderText("Selecione um ficheiro à esquerda para ver as alterações...")
        right_panel_layout.addWidget(self.diff_viewer)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([450, 550])
        main_layout = QHBoxLayout(page)
        main_layout.addWidget(main_splitter)
        return page

    def create_page_branches(self):
        page = QWidget()
        left_panel = QWidget()
        col_esquerda = QVBoxLayout(left_panel)
        col_esquerda.setContentsMargins(0, 0, 0, 0)
        col_esquerda.addWidget(QLabel("Branches Locais e Remotas:"))
        self.list_branches = QListWidget()
        self.list_branches.setToolTip("Clique duplo para fazer 'Checkout'")
        self.list_branches.itemDoubleClicked.connect(self.trocar_branch)
        col_esquerda.addWidget(self.list_branches)
        right_panel = QWidget()
        col_direita = QVBoxLayout(right_panel)
        col_direita.setContentsMargins(0, 0, 0, 0)
        form_layout = QFormLayout()
        self.txt_new_branch = QLineEdit()
        icon_new_branch = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
        self.btn_create_branch = QPushButton(icon_new_branch, " Criar Nova Branch")
        self.btn_create_branch.clicked.connect(self.criar_nova_branch)
        form_layout.addRow("Nome da Nova Branch:", self.txt_new_branch)
        form_layout.addRow(self.btn_create_branch)
        col_direita.addLayout(form_layout)
        col_direita.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        icon_checkout = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DialogOkButton)
        self.btn_checkout_branch = QPushButton(icon_checkout, " Trocar para Branch (Checkout)")
        self.btn_checkout_branch.clicked.connect(self.trocar_branch)
        col_direita.addWidget(self.btn_checkout_branch)
        icon_merge = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DirLinkIcon)
        self.btn_merge_branch = QPushButton(icon_merge, " Juntar Branch Selecionada (Merge)")
        self.btn_merge_branch.setObjectName("MergeButton")
        self.btn_merge_branch.setStyleSheet("")
        self.btn_merge_branch.clicked.connect(self.merge_branch)
        col_direita.addWidget(self.btn_merge_branch)
        icon_delete = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.btn_delete_branch = QPushButton(icon_delete, " Deletar Branch Selecionada")
        self.btn_delete_branch.setObjectName("DeleteButton")
        self.btn_delete_branch.setStyleSheet("")
        self.btn_delete_branch.clicked.connect(self.deletar_branch)
        col_direita.addWidget(self.btn_delete_branch)
        col_direita.addStretch()
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([600, 300])
        main_layout = QHBoxLayout(page)
        main_layout.addWidget(main_splitter)
        return page

    def create_page_history(self):
        page = QWidget()
        self.graph_widget = CommitGraphWidget()
        self.graph_widget.commit_context_menu_requested.connect(self.show_commit_context_menu)
        self.graph_widget.commit_selected.connect(self.mostrar_detalhes_commit)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.graph_widget)
        details_panel = QWidget()
        details_layout = QVBoxLayout(details_panel)
        details_layout.setContentsMargins(0, 5, 0, 0)
        details_layout.addWidget(QLabel("Detalhes e Diff do Commit Selecionado:"))
        self.log_commit_details = QTextEdit()
        self.log_commit_details.setReadOnly(True)
        self.log_commit_details.setFont(QFont("Monospace", 9))
        details_layout.addWidget(self.log_commit_details)
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(scroll_area)
        main_splitter.addWidget(details_panel)
        main_splitter.setSizes([400, 200])
        main_layout = QHBoxLayout(page)
        main_layout.addWidget(main_splitter)
        return page

    def create_page_remotes(self):
        page = QWidget()
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Remotes Configurados:"))
        self.list_remotes = QListWidget()
        self.list_remotes.itemSelectionChanged.connect(self.mostrar_detalhes_remote)
        left_layout.addWidget(self.list_remotes)
        icon_delete_remote = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.btn_remove_remote = QPushButton(icon_delete_remote, " Remover Remote Selecionado")
        self.btn_remove_remote.setObjectName("DeleteButton")
        self.btn_remove_remote.setStyleSheet("")
        self.btn_remove_remote.clicked.connect(self.remover_remote)
        left_layout.addWidget(self.btn_remove_remote)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        form_layout = QFormLayout()
        self.txt_remote_name = QLineEdit()
        self.txt_remote_url = QLineEdit()
        form_layout.addRow("Nome (ex: 'upstream'):", self.txt_remote_name)
        form_layout.addRow("URL (ex: 'https://...'):", self.txt_remote_url)
        icon_add_remote = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self.btn_add_remote = QPushButton(icon_add_remote, " Adicionar Novo Remote")
        self.btn_add_remote.clicked.connect(self.adicionar_remote)
        form_layout.addRow(self.btn_add_remote)
        right_layout.addLayout(form_layout)
        right_layout.addWidget(QLabel("Detalhes do Remote:"))
        self.log_remote_details = QTextEdit()
        self.log_remote_details.setReadOnly(True)
        right_layout.addWidget(self.log_remote_details)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 600])
        main_layout = QHBoxLayout(page)
        main_layout.addWidget(main_splitter)
        return page

    def create_page_tags(self):
        page = QWidget()
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Tags do Repositório:"))
        self.list_tags = QListWidget()
        self.list_tags.itemSelectionChanged.connect(self.mostrar_detalhes_tag)
        left_layout.addWidget(self.list_tags)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        action_panel = QWidget()
        action_layout = QVBoxLayout(action_panel)
        action_layout.setContentsMargins(0, 0, 0, 0)
        form_layout = QFormLayout()
        self.txt_tag_name = QLineEdit()
        self.txt_tag_name.setPlaceholderText("ex: v1.0.0")
        self.txt_tag_message = QLineEdit()
        self.txt_tag_message.setPlaceholderText("ex: Lançamento da versão 1.0 (opcional)")
        icon_add = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self.btn_create_tag = QPushButton(icon_add, " Criar Nova Tag")
        self.btn_create_tag.setToolTip("Cria uma tag no commit atual (HEAD)")
        self.btn_create_tag.clicked.connect(self.criar_nova_tag)
        form_layout.addRow("Nome da Tag:", self.txt_tag_name)
        form_layout.addRow("Mensagem (p/ tag anotada):", self.txt_tag_message)
        form_layout.addRow(self.btn_create_tag)
        action_layout.addLayout(form_layout)
        action_layout.addStretch()
        right_splitter.addWidget(action_panel)

        details_panel = QWidget()
        details_layout = QVBoxLayout(details_panel)
        details_layout.setContentsMargins(0, 5, 0, 0)
        details_layout.addWidget(QLabel("Detalhes da Tag Selecionada:"))
        self.log_tag_details = QTextEdit()
        self.log_tag_details.setReadOnly(True)
        details_layout.addWidget(self.log_tag_details)
        icon_del = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.btn_delete_tag = QPushButton(icon_del, " Deletar Tag Selecionada (Local)")
        self.btn_delete_tag.setObjectName("DeleteButton")
        self.btn_delete_tag.clicked.connect(self.remover_tag)
        details_layout.addWidget(self.btn_delete_tag)
        right_splitter.addWidget(details_panel)
        right_splitter.setSizes([150, 450])
        right_layout.addWidget(right_splitter)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 600])
        
        main_layout = QHBoxLayout(page)
        main_layout.addWidget(main_splitter)
        return page

    def create_page_stash(self):
        page = QWidget()
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_save_stash = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        self.btn_create_stash = QPushButton(icon_save_stash, " Guardar Alterações (Stash)")
        self.btn_create_stash.setToolTip("Guarda as alterações atuais (staged e unstaged) num novo stash")
        self.btn_create_stash.clicked.connect(self.stash_mudancas)
        left_layout.addWidget(self.btn_create_stash)
        
        left_layout.addWidget(QLabel("Stashes Guardados:"))
        self.list_stashes = QListWidget()
        self.list_stashes.itemSelectionChanged.connect(self.mostrar_detalhes_stash)
        left_layout.addWidget(self.list_stashes)
        
        action_layout = QHBoxLayout()
        icon_apply = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        self.btn_apply_stash = QPushButton(icon_apply, " Aplicar")
        self.btn_apply_stash.setToolTip("Aplica o stash selecionado (git stash apply)")
        self.btn_apply_stash.clicked.connect(self.aplicar_stash)
        action_layout.addWidget(self.btn_apply_stash)
        
        icon_del = self.icon_style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.btn_drop_stash = QPushButton(icon_del, " Apagar (Drop)")
        self.btn_drop_stash.setToolTip("Apaga permanentemente o stash selecionado (git stash drop)")
        self.btn_drop_stash.setObjectName("DeleteButton")
        self.btn_drop_stash.clicked.connect(self.remover_stash)
        action_layout.addWidget(self.btn_drop_stash)
        left_layout.addLayout(action_layout)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(QLabel("Detalhes e Diff do Stash:"))
        self.log_stash_details = QTextEdit()
        self.log_stash_details.setReadOnly(True)
        self.log_stash_details.setFont(QFont("Monospace", 9))
        right_layout.addWidget(self.log_stash_details)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 600])
        
        main_layout = QHBoxLayout(page)
        main_layout.addWidget(main_splitter)
        return page

    def log(self, message):
        self.txt_output.append(message)
        QApplication.processEvents()
        
    def carregar_repo(self, path):
        try:
            self.repo = Repo(path)
            self.txt_local_path.setText(path)
            
            try:
                _ = self.repo.head.commit
                self.is_empty_repo = False
            except Exception:
                self.is_empty_repo = True
                self.log("Aviso: Repositório vazio (sem commits) detetado.")
                
            self.log(f"Repositório '{path}' carregado com sucesso.")
            self.request_set_repo_path.emit(path)
            
            self.atualizar_status_ui() # Isto chama _check_conflict_state
            self.atualizar_lista_branches()
            self.atualizar_historico()
            self.atualizar_titulo_janela() 
            self.atualizar_lista_remotes()
            self.atualizar_lista_tags()
            self.atualizar_lista_stashes()
            if hasattr(self, 'diff_viewer'): self.diff_viewer.clear()
            self.set_repo_open_state(True)
        except InvalidGitRepositoryError:
            self.repo = None
            self.log(f"ERRO: A pasta '{path}' não é um repositório Git válido.")
            self.set_repo_open_state(False)
        except Exception as e:
            self.repo = None
            self.log(f"ERRO inesperado ao carregar repo: {e}")
            self.set_repo_open_state(False)
            
    def atualizar_titulo_janela(self):
        if not self.repo: return
        
        if self.is_empty_repo:
            try:
                branch_name = self.repo.head.ref.name
            except Exception:
                branch_name = "Vazio"
            self.setWindowTitle(f"Assistente Git - [{branch_name} (vazio)] - {self.repo.working_tree_dir}")
            return
            
        try:
            branch_name = self.repo.active_branch.name
            self.setWindowTitle(f"Assistente Git - [{branch_name}] - {self.repo.working_tree_dir}")
        except TypeError:
            self.setWindowTitle(f"Assistente Git - [Detached HEAD] - {self.repo.working_tree_dir}")
            
    def atualizar_lista_branches(self):
        if not self.repo: return
        self.list_branches.clear()
        self.combo_push_branch.clear()
        bold_font = QFont(); bold_font.setBold(True)
        
        if self.is_empty_repo:
            try:
                branch_name = self.repo.head.ref.name
                item = QListWidgetItem(f"➡️ {branch_name} (vazio)")
                item.setFont(bold_font)
                self.list_branches.addItem(item)
                self.combo_push_branch.addItem(branch_name)
                self.combo_push_branch.setCurrentText(branch_name)
            except Exception:
                self.log("Não foi possível ler a branch 'unborn' do HEAD.")
        else:
            for branch in self.repo.heads:
                item = QListWidgetItem(f"📍 {branch.name}")
                self.combo_push_branch.addItem(branch.name)
                if branch == self.repo.active_branch:
                    item.setFont(bold_font)
                    item.setText(f"➡️ {branch.name} (Ativa)")
                    self.combo_push_branch.setCurrentText(branch.name)
                self.list_branches.addItem(item)
            
        try:
            for remote in self.repo.remotes:
                for ref in remote.refs:
                    if "HEAD" not in ref.name:
                        item = QListWidgetItem(f"☁️ {ref.name}")
                        item.setForeground(Qt.GlobalColor.gray)
                        self.list_branches.addItem(item)
        except Exception as e:
            self.log(f"Aviso: Não foi possível listar branches remotas. {e}")

    def build_commit_graph_data(self):
        if not self.repo or self.is_empty_repo:
            return []
            
        try:
            commits = list(self.repo.iter_commits('--all', max_count=200))
            commits.sort(key=lambda c: c.committed_datetime, reverse=True)
        except Exception as e:
            self.log(f"ERRO ao ler commits: {e}")
            return []
        
        commit_to_row = {commit.hexsha: i for i, commit in enumerate(commits)}
        graph_data = []
        lanes = {}
        commit_to_lane = {}
        
        for y_row, commit in enumerate(commits):
            lane = -1
            
            for lane_index, head_hash in lanes.items():
                if commit.hexsha == head_hash:
                    lane = lane_index
                    break
            
            if lane == -1:
                lane_index = 0
                while lane_index in lanes:
                    lane_index += 1
                lane = lane_index
            
            lanes[lane] = commit.hexsha
            commit_to_lane[commit.hexsha] = lane
            
            if len(commit.parents) > 1:
                for parent in commit.parents[1:]:
                    for l_idx, l_hash in list(lanes.items()):
                        if l_hash == parent.hexsha:
                            is_head = False
                            for head in self.repo.heads:
                                if head.commit.hexsha == l_hash:
                                    is_head = True
                                    break
                            if not is_head:
                                del lanes[l_idx]
                            
            graph_data.append({'commit': commit, 'lane': lane, 'y_row': y_row})
            
            for i, parent in enumerate(commit.parents):
                parent_lane = commit_to_lane.get(parent.hexsha, -1)
                
                if i == 0:
                    lanes[lane] = parent.hexsha
                    if parent_lane != -1 and parent_lane != lane:
                        if parent_lane in lanes:
                            del lanes[parent_lane]
                    commit_to_lane[parent.hexsha] = lane
                else:
                    if parent_lane == -1:
                        new_lane_index = 0
                        while new_lane_index in lanes:
                            new_lane_index += 1
                        lanes[new_lane_index] = parent.hexsha
                        commit_to_lane[parent.hexsha] = new_lane_index

        self.commits_na_tabela = commits
        return graph_data

    @Slot()
    def atualizar_historico(self):
        if not self.repo: return
        
        if self.is_empty_repo:
            self.log("Repositório vazio. O grafo de commits será preenchido após o primeiro commit.")
            if hasattr(self, 'graph_widget'): self.graph_widget.set_data([])
            if hasattr(self, 'log_commit_details'): self.log_commit_details.clear()
            self.commits_na_tabela = []
            return

        self.log("Construindo grafo de commits...")
        graph_data = self.build_commit_graph_data()
        self.graph_widget.set_data(graph_data)
        self.log(f"Histórico de {len(graph_data)} commits carregado.")
        self.log_commit_details.clear()

    def atualizar_lista_remotes(self):
        if not self.repo: return
        self.list_remotes.clear()
        self.combo_pull_remote.clear()
        self.combo_push_remote.clear()
        self.log_remote_details.clear()
        try:
            for remote in self.repo.remotes:
                self.list_remotes.addItem(remote.name)
                self.combo_pull_remote.addItem(remote.name)
                self.combo_push_remote.addItem(remote.name)
            if 'origin' in [r.name for r in self.repo.remotes]:
                self.combo_pull_remote.setCurrentText("origin")
                self.combo_push_remote.setCurrentText("origin")
            self.log("Lista de remotes atualizada.")
        except Exception as e:
            self.log(f"ERRO ao atualizar lista de remotes: {e}")

    @Slot()
    def atualizar_lista_tags(self):
        if not self.repo: return
        
        self.list_tags.clear()
        self.log_tag_details.clear()
        
        try:
            tags = sorted(self.repo.tags, key=lambda t: t.name, reverse=True)
            for tag in tags:
                self.list_tags.addItem(tag.name)
            self.log("Lista de tags atualizada.")
        except Exception as e:
            self.log(f"ERRO ao atualizar lista de tags: {e}")

    @Slot()
    def atualizar_lista_stashes(self):
        if not self.repo: return
        
        self.list_stashes.clear()
        self.log_stash_details.clear()
        
        try:
            stash_list_raw = self.repo.git.stash('list')
            if not stash_list_raw:
                self.log("Nenhum item no stash.")
                return
                
            stashes = stash_list_raw.splitlines()
            self.list_stashes.addItems(stashes)
            self.log(f"Lista de {len(stashes)} stashes carregada.")
        except Exception as e:
            self.log(f"ERRO ao ler lista de stashes: {e}")

    @Slot()
    def abrir_repositorio(self):
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Pasta do Repositório")
        if directory:
            self.carregar_repo(directory)

    @Slot()
    def clonar_repositorio(self):
        url = self.txt_url_clone.text()
        if not url: return self.log("ERRO: URL para clone não pode estar vazia.")
        directory = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Destino para Clonar")
        if not directory: return self.log("Clone cancelado.")
        repo_name = url.split('/')[-1].replace('.git', '')
        local_path = os.path.join(directory, repo_name)
        self.set_ui_loading(True)
        self.request_clone.emit(url, local_path)

    @Slot()
    def atualizar_status_ui(self):
        if not self.repo:
            self.log("Nenhum repositório carregado para atualizar.")
            return
            
        self._check_conflict_state()
        
        self.list_unstaged.clear()
        self.list_staged.clear()
        if hasattr(self, 'diff_viewer'): self.diff_viewer.clear()
        self.log(f"Verificando status em '{self.repo.working_tree_dir}'...")
        
        modified_files = [item.a_path for item in self.repo.index.diff(None)]
        untracked_files = self.repo.untracked_files
        
        if self.is_empty_repo:
            staged_files = [entry[0] for entry, stage in self.repo.index.entries.items()]
        else:
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            
        self.list_unstaged.addItems(modified_files)
        self.list_unstaged.addItems(untracked_files)
        self.list_staged.addItems(staged_files)
        
        self.log("Status atualizado.")
        for i in range(len(modified_files), self.list_unstaged.count()):
             self.list_unstaged.item(i).setForeground(Qt.GlobalColor.gray)
             self.list_unstaged.item(i).setText(f"[Novo] {self.list_unstaged.item(i).text()}")

    @Slot()
    def stage_arquivos(self):
        if not self.repo: return
        itens_selecionados = self.list_unstaged.selectedItems()
        if not itens_selecionados:
            return self.log("Nenhum arquivo selecionado para 'stage'.")
        try:
            arquivos_para_add = [item.text().replace("[Novo] ", "") for item in itens_selecionados]
            self.log(f"Adicionando ao stage: {', '.join(arquivos_para_add)}")
            self.repo.index.add(arquivos_para_add)
            self.atualizar_status_ui()
        except GitCommandError as e:
            self.log(f"ERRO ao adicionar (stage): {e.stderr}")
            
    @Slot()
    def unstage_arquivos(self):
        if not self.repo: return
        itens_selecionados = self.list_staged.selectedItems()
        if not itens_selecionados:
            return self.log("Nenhum arquivo selecionado para 'unstage'.")
        try:
            arquivos_para_reset = [item.text() for item in itens_selecionados]
            self.log(f"Removendo do stage: {', '.join(arquivos_para_reset)}")
            self.repo.index.reset(paths=arquivos_para_reset)
            self.atualizar_status_ui()
        except GitCommandError as e:
            self.log(f"ERRO ao remover (unstage): {e.stderr}")
            
    @Slot()
    def commitar_mudancas(self):
        if not self.repo: return
        msg = self.txt_commit_msg.text()
        if not msg:
            return self.log("ERRO: Mensagem de commit não pode estar vazia.")
        if self.list_staged.count() == 0:
            return self.log("ERRO: Não há nada em 'stage' para commitar.")
        try:
            self.log(f"Commitando: '{msg}'")
            self.repo.index.commit(msg)
            self.log(">>> Commit realizado com sucesso!")
            
            if self.is_empty_repo:
                self.is_empty_repo = False
                self.carregar_repo(self.repo.working_tree_dir) 
            else:
                self.atualizar_status_ui()
                self.atualizar_historico()
            
            self.txt_commit_msg.setText("Commit...")
        except GitCommandError as e:
            self.log(f"ERRO no commit: {e.stderr}")
            
    @Slot()
    def pull_repositorio(self):
        if not self.repo: return
        remote_name = self.combo_pull_remote.currentText()
        if not remote_name:
            return self.log("ERRO: Nenhum remote selecionado para 'Pull'.")
        self.set_ui_loading(True)
        self.request_pull.emit(remote_name)

    @Slot()
    def push_repositorio(self):
        if not self.repo: return
        remote_name = self.combo_push_remote.currentText()
        branch_name = self.combo_push_branch.currentText()
        if not remote_name: return self.log("ERRO: Nenhum remote selecionado para 'Push'.")
        if not branch_name: return self.log("ERRO: Nenhuma branch selecionada para 'Push'.")
        self.set_ui_loading(True)
        self.request_push.emit(remote_name, branch_name)

    @Slot()
    def criar_nova_branch(self):
        if not self.repo: return
        if self.is_empty_repo:
            self.log("ERRO: Faça o primeiro commit antes de criar uma nova branch.")
            return
            
        novo_nome = self.txt_new_branch.text().strip()
        if not novo_nome:
            return self.log("ERRO: Nome da nova branch não pode ser vazio.")
        try:
            self.log(f"Criando nova branch: '{novo_nome}'...")
            nova_branch = self.repo.create_head(novo_nome)
            self.log("Branch criada com sucesso.")
            reply = QMessageBox.question(self, "Trocar de Branch",
                                         f"Branch '{novo_nome}' criada. Deseja fazer checkout agora?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                nova_branch.checkout()
                self.log(f"Trocado para a nova branch: '{novo_nome}'.")
                self.atualizar_status_ui(); self.atualizar_historico()
            self.atualizar_lista_branches(); self.atualizar_titulo_janela()
            self.txt_new_branch.clear()
        except Exception as e:
            self.log(f"ERRO ao criar branch (ela já existe?): {e}")

    @Slot()
    def trocar_branch(self):
        if not self.repo: return
        item_selecionado = self.list_branches.currentItem()
        if not item_selecionado:
            item_duplo_clique = self.sender()
            if isinstance(item_duplo_clique, QListWidgetItem): item_selecionado = item_duplo_clique
            else: return self.log("Nenhuma branch selecionada para trocar.")
        
        if self.is_empty_repo:
            self.log("ERRO: Faça o primeiro commit antes de trocar de branch.")
            return
            
        nome_completo = self._limpar_nome_branch(item_selecionado.text())
        if self.repo.is_dirty(untracked_files=True):
             self.log("ERRO: Você possui alterações não commitadas.")
             QMessageBox.warning(self, "Troca de Branch Falhou", "Você possui alterações não commitadas.\n\nUse 'Stash' ou 'Commit'.")
             return
        try:
            if item_selecionado.text().startswith("☁️ "):
                partes = nome_completo.split('/', 1)
                if len(partes) < 2:
                    return self.log(f"ERRO: Nome de branch remota inválido: '{nome_completo}'")
                remote_name, branch_name_remota = partes
                reply = QMessageBox.question(self, "Checkout de Branch Remota",
                                     f"Deseja criar uma nova branch local chamada '{branch_name_remota}' para rastrear '{nome_completo}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.No: return self.log("Checkout cancelado.")
                if branch_name_remota in self.repo.heads:
                    self.log(f"Branch local '{branch_name_remota}' já existe. Fazendo checkout simples...")
                    self.repo.heads[branch_name_remota].checkout()
                else:
                    self.log(f"Criando e fazendo checkout da nova branch local '{branch_name_remota}'...")
                    remote_branch = self.repo.remotes[remote_name].refs[branch_name_remota]
                    nova_branch = self.repo.create_head(branch_name_remota, remote_branch, track=True)
                    nova_branch.checkout()
            else:
                self.log(f"Trocando (checkout) para a branch local '{nome_completo}'...")
                self.repo.heads[nome_completo].checkout()
            self.log(">>> Troca concluída com sucesso!")
            self.atualizar_lista_branches(); self.atualizar_titulo_janela()
            self.atualizar_status_ui(); self.atualizar_historico()
        except Exception as e:
            self.log(f"ERRO ao trocar de branch: {e}")

    @Slot()
    def deletar_branch(self):
        if not self.repo or self.is_empty_repo: return
        item_selecionado = self.list_branches.currentItem()
        if not item_selecionado:
            return self.log("Nenhuma branch selecionada para deletar.")
        nome_branch = self._limpar_nome_branch(item_selecionado.text())
        if item_selecionado.text().startswith("☁️ "):
            reply = QMessageBox.warning(self, "Confirmar Deleção Remota",
                                     f"Tem certeza que deseja deletar a branch REMOTA '{nome_branch}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No: return self.log("Deleção remota cancelada.")
            try:
                remote_name, branch_name_remota = nome_branch.split('/', 1)
                self.log(f"Deletando branch remota: 'git push {remote_name} --delete {branch_name_remota}'...")
                self.repo.git.push(remote_name, '--delete', branch_name_remota)
                self.log(">>> Branch remota deletada com sucesso.")
                self.atualizar_lista_branches()
            except Exception as e:
                self.log(f"ERRO ao deletar branch remota: {e}")
            return
        if self.repo.active_branch.name == nome_branch:
            return self.log(f"ERRO: Não é possível deletar a branch '{nome_branch}' pois ela é a branch ativa.")
        reply = QMessageBox.warning(self, "Confirmar Deleção",
                                     f"Tem certeza que deseja deletar a branch local '{nome_branch}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return self.log("Deleção cancelada.")
        try:
            self.log(f"Deletando branch local '{nome_branch}'...")
            self.repo.delete_head(nome_branch)
            self.log(">>> Branch deletada com sucesso.")
            self.atualizar_lista_branches()
        except Exception as e:
            self.log(f"ERRO ao deletar branch: {e}")

    @Slot()
    def merge_branch(self):
        if not self.repo or self.is_empty_repo: return
        item_selecionado = self.list_branches.currentItem()
        if not item_selecionado: return self.log("Nenhuma branch selecionada para fazer merge.")
        nome_branch_para_merge = self._limpar_nome_branch(item_selecionado.text())
        branch_ativa = self.repo.active_branch.name
        if branch_ativa == nome_branch_para_merge:
            return self.log("ERRO: Não é possível fazer merge de uma branch nela mesma.")
        if self.repo.is_dirty(untracked_files=True):
             self.log("ERRO: Você possui alterações não commitadas.")
             QMessageBox.warning(self, "Merge Falhou", "Você possui alterações não commitadas.\n\nUse 'Stash' ou 'Commit'.")
             return
        reply = QMessageBox.question(self, "Confirmar Merge",
                                     f"Tem certeza que deseja fazer merge de:\n\n'{nome_branch_para_merge}'\n\nDENTRO DE:\n\n'{branch_ativa}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return self.log("Merge cancelado.")
        self.set_ui_loading(True)
        self.request_merge.emit(nome_branch_para_merge)
            
    @Slot(str)
    def mostrar_detalhes_commit(self, commit_hash):
        if not self.repo or self.is_empty_repo: return
        
        try:
            commit = self.repo.commit(commit_hash)
            self.graph_widget.select_commit(commit_hash)
        except Exception as e:
            self.log(f"Erro ao encontrar o commit {commit_hash}: {e}")
            return
            
        self.log_commit_details.clear()
        
        self.log_commit_details.append(f"Autor:   {commit.author.name} <{commit.author.email}>")
        data_str = commit.committed_datetime.strftime("%d/%m/%Y %H:%M:%S %z")
        self.log_commit_details.append(f"Data:    {data_str}")
        self.log_commit_details.append(f"Hash:    {commit.hexsha}")
        self.log_commit_details.append("\n--- Mensagem ---\n"); self.log_commit_details.append(commit.message)
        self.log_commit_details.append("\n--- Alterações (Diff) ---\n")
        
        try:
            if not commit.parents:
                self.log("Carregando diff do commit inicial...")
                diff_text = self.repo.git.show(commit.hexsha)
            else:
                parent_hash = commit.parents[0].hexsha
                diff_text = self.repo.git.diff(parent_hash, commit.hexsha)
            
            if not diff_text: diff_text = "(Sem alterações visíveis de código - ex: merge)"
        except Exception as e:
            diff_text = f"(Não foi possível carregar o diff: {e})"

        self.log_commit_details.append(diff_text)
    
    @Slot()
    def show_unstaged_diff(self):
        if not self.repo: return
        self.list_staged.clearSelection()
        item = self.list_unstaged.currentItem()
        if not item: self.diff_viewer.clear(); return
        file_path = item.text()
        try:
            if "[Novo]" in file_path:
                file_path = file_path.replace("[Novo] ", "")
                full_path = os.path.join(self.repo.working_tree_dir, file_path)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f: content = f.read()
                    self.diff_viewer.setText(f"--- NOVO FICHEIRO: {file_path} ---\n\n{content}")
                except Exception as e:
                    self.diff_viewer.setText(f"--- NOVO FICHEIRO: {file_path} ---\n\n(Não foi possível ler o conteúdo. Ficheiro binário? {e})")
            else:
                diff_text = self.repo.git.diff(None, file_path)
                if not diff_text: diff_text = "(Sem alterações 'unstaged' para este ficheiro)"
                self.diff_viewer.setText(diff_text)
        except Exception as e:
            self.diff_viewer.setText(f"Erro ao gerar diff: {e}")

    @Slot()
    def show_staged_diff(self):
        if not self.repo: return
        self.list_unstaged.clearSelection()
        item = self.list_staged.currentItem()
        if not item: self.diff_viewer.clear(); return
        file_path = item.text()
        try:
            if self.is_empty_repo:
                diff_text = self.repo.git.diff('--cached', file_path)
            else:
                diff_text = self.repo.git.diff('--cached', file_path)
                
            if not diff_text: diff_text = "(Sem alterações 'staged' para este ficheiro)"
            self.diff_viewer.setText(diff_text)
        except Exception as e:
            self.diff_viewer.setText(f"Erro ao gerar diff: {e}")
            
    @Slot()
    def mostrar_detalhes_remote(self):
        if not self.repo: return
        item = self.list_remotes.currentItem()
        if not item: self.log_remote_details.clear(); return
        try:
            remote = self.repo.remotes[item.text()]
            self.log_remote_details.clear()
            self.log_remote_details.append(f"Nome: {remote.name}\n")
            self.log_remote_details.append("URLs:")
            for url in remote.urls:
                self.log_remote_details.append(f"- {url}")
        except Exception as e:
            self.log_remote_details.setText(f"Erro ao ler remote: {e}")
            
    @Slot()
    def adicionar_remote(self):
        if not self.repo: return
        name = self.txt_remote_name.text().strip()
        url = self.txt_remote_url.text().strip()
        if not name or not url:
            return self.log("ERRO: Nome e URL são obrigatórios para adicionar um remote.")
        try:
            self.log(f"Adicionando remote '{name}' com URL '{url}'...")
            self.repo.create_remote(name, url)
            self.log(">>> Remote adicionado com sucesso!")
            self.atualizar_lista_remotes()
            self.txt_remote_name.clear(); self.txt_remote_url.clear()
        except Exception as e:
            self.log(f"ERRO ao adicionar remote (já existe?): {e}")

    @Slot()
    def remover_remote(self):
        if not self.repo: return
        item = self.list_remotes.currentItem()
        if not item: return self.log("Nenhum remote selecionado para remover.")
        remote_name = item.text()
        reply = QMessageBox.warning(self, "Confirmar Remoção",
                                     f"Tem certeza que deseja remover o remote '{remote_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No: return self.log("Remoção cancelada.")
        try:
            self.log(f"Removendo remote '{remote_name}'...")
            self.repo.delete_remote(remote_name)
            self.log(">>> Remote removido com sucesso!")
            self.atualizar_lista_remotes()
        except Exception as e:
            self.log(f"ERRO ao remover remote: {e}")
            
    @Slot()
    def mostrar_detalhes_tag(self):
        if not self.repo: return
        item = self.list_tags.currentItem()
        if not item:
            self.log_tag_details.clear()
            return
            
        try:
            tag_name = item.text()
            tag = self.repo.tags[tag_name]
            commit = tag.commit
            
            self.log_tag_details.clear()
            self.log_tag_details.append(f"Tag:    {tag.name}")
            self.log_tag_details.append(f"Commit: {commit.hexsha[:7]}")
            self.log_tag_details.append(f"Autor:  {commit.author.name}")
            self.log_tag_details.append(f"Data:   {commit.committed_datetime.strftime('%d/%m/%Y %H:%M')}")
            
            try:
                self.log_tag_details.append(f"\nMensagem:\n{tag.tag.message}")
            except Exception:
                self.log_tag_details.append("\n(Tag leve - sem mensagem)")
                
        except Exception as e:
            self.log_tag_details.setText(f"Erro ao ler detalhes da tag: {e}")

    @Slot()
    def criar_nova_tag(self):
        if not self.repo or self.is_empty_repo:
            self.log("ERRO: Faça o primeiro commit antes de criar uma tag.")
            return
            
        name = self.txt_tag_name.text().strip()
        msg = self.txt_tag_message.text().strip()
        
        if not name:
            self.log("ERRO: O nome da tag é obrigatório.")
            return
            
        try:
            if msg:
                self.repo.create_tag(name, message=msg)
                self.log(f"Tag anotada '{name}' criada com sucesso.")
            else:
                self.repo.create_tag(name)
                self.log(f"Tag leve '{name}' criada com sucesso.")
                
            self.atualizar_lista_tags()
            self.txt_tag_name.clear()
            self.txt_tag_message.clear()
            
        except Exception as e:
            self.log(f"ERRO ao criar tag (já existe?): {e}")
            
    @Slot()
    def remover_tag(self):
        if not self.repo: return
        item = self.list_tags.currentItem()
        if not item:
            return self.log("Nenhuma tag selecionada para remover.")
            
        tag_name = item.text()
        
        reply = QMessageBox.warning(self, "Confirmar Remoção de Tag (Local)",
                                     f"Tem certeza que deseja deletar a tag local '{tag_name}'?\n(Isto não remove a tag do servidor remoto.)",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return self.log("Remoção cancelada.")
            
        try:
            self.log(f"Removendo tag local '{tag_name}'...")
            self.repo.delete_tag(tag_name)
            self.log(">>> Tag local removida com sucesso.")
            self.atualizar_lista_tags()
        except Exception as e:
            self.log(f"ERRO ao remover tag: {e}")

    @Slot()
    def mostrar_detalhes_stash(self):
        if not self.repo: return
        item = self.list_stashes.currentItem()
        if not item:
            self.log_stash_details.clear()
            return
            
        try:
            stash_ref = item.text().split(':')[0]
            diff_text = self.repo.git.stash('show', '-p', stash_ref)
            if not diff_text:
                diff_text = "(Este stash está vazio ou contém apenas ficheiros 'untracked')"
            self.log_stash_details.setText(diff_text)
        except Exception as e:
            self.log_stash_details.setText(f"Erro ao ler diff do stash: {e}")

    @Slot()
    def aplicar_stash(self):
        if not self.repo: return
        item = self.list_stashes.currentItem()
        if not item:
            return self.log("Nenhum stash selecionado para aplicar.")
            
        stash_ref = item.text().split(':')[0]
        
        reply = QMessageBox.question(self, "Confirmar Aplicação de Stash",
                                     f"Tem certeza que deseja aplicar o stash '{stash_ref}'?\n(Isto não o removerá da lista.)",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.Yes)
        if reply == QMessageBox.StandardButton.No:
            return self.log("Aplicação cancelada.")
            
        try:
            self.log(f"Aplicando stash '{stash_ref}' (git stash apply)...")
            self.repo.git.stash('apply', stash_ref)
            self.log(">>> Stash aplicado com sucesso!")
            self.atualizar_status_ui()
        except GitCommandError as e:
            if "conflict" in str(e.stderr).lower():
                self.log("!!! CONFLITO DETECTADO AO APLICAR O STASH !!!")
                self.log(f"ERRO: {e.stderr}")
                QMessageBox.critical(self, "Conflito no Stash", "Ocorreu um conflito ao aplicar o stash.\n\nResolva os conflitos manualmente e faça 'commit'.")
                self.atualizar_status_ui()
            else:
                self.log(f"ERRO ao aplicar stash: {e.stderr}")
        except Exception as e:
            self.log(f"ERRO: {e}")

    @Slot()
    def remover_stash(self):
        if not self.repo: return
        item = self.list_stashes.currentItem()
        if not item:
            return self.log("Nenhum stash selecionado para apagar.")
            
        stash_ref = item.text().split(':')[0]
        
        reply = QMessageBox.warning(self, "Confirmar Remoção de Stash",
                                     f"Tem certeza que deseja apagar permanentemente o stash '{stash_ref}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return self.log("Remoção cancelada.")
            
        try:
            self.log(f"Apagando stash '{stash_ref}' (git stash drop)...")
            self.repo.git.stash('drop', stash_ref)
            self.log(">>> Stash apagado com sucesso.")
            self.atualizar_lista_stashes()
        except Exception as e:
            self.log(f"ERRO ao apagar stash: {e}")
    
    @Slot()
    def stash_mudancas(self):
        if not self.repo: return
        
        if self._check_conflict_state(silent=True):
            self.log("ERRO: Não é possível guardar o stash durante um conflito de merge.")
            QMessageBox.warning(self, "Stash Falhou", "Você não pode guardar um stash enquanto estiver a resolver um conflito de merge.")
            return

        if not self.repo.is_dirty(untracked_files=True):
            self.log("Aviso: Não há alterações para guardar no Stash.")
            return

        try:
            self.log("Guardando alterações no Stash (git stash)...")
            self.repo.git.stash('save', '-u', 'Stash automático via GitApp')
            self.log(">>> Alterações guardadas com sucesso!")
            
            self.atualizar_status_ui()
            self.atualizar_lista_stashes()
            
        except GitCommandError as e:
            self.log(f"ERRO ao guardar no Stash: {e.stderr}")
        except Exception as e:
            self.log(f"ERRO: {e}")
    
    def _check_conflict_state(self, silent=False):
        if not self.repo:
            self.conflict_bar.setVisible(False)
            return False

        try:
            in_merge_state = os.path.exists(os.path.join(self.repo.git_dir, "MERGE_HEAD"))
            in_rebase_state = os.path.exists(os.path.join(self.repo.git_dir, "rebase-merge"))
            
            is_in_conflict = in_merge_state or in_rebase_state
            
            if not silent:
                self.conflict_bar.setVisible(is_in_conflict)
                
            return is_in_conflict
        except Exception as e:
            if not silent:
                self.log(f"Erro ao verificar estado de merge: {e}")
                self.conflict_bar.setVisible(False)
            return False
            
    @Slot()
    def abortar_merge(self):
        if not self.repo: return
        
        reply = QMessageBox.warning(self, "Confirmar Abortar",
                                     "Tem certeza que deseja abortar a operação atual (merge/rebase)?\nTodas as resoluções de conflito serão perdidas.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return self.log("Operação cancelada.")
            
        try:
            self.log("Abortando operação...")
            try:
                self.repo.git.merge('--abort')
                self.log(">>> Merge abortado com sucesso.")
            except GitCommandError:
                self.repo.git.rebase('--abort')
                self.log(">>> Rebase abortado com sucesso.")
                
            self.log("O seu repositório foi restaurado.")
            self.atualizar_status_ui()
            self.atualizar_historico()
        except Exception as e:
            self.log(f"ERRO ao abortar operação: {e}")
            
    @Slot(str, QPoint)
    def show_commit_context_menu(self, commit_hash, global_pos):
        if not self.repo or self.is_empty_repo:
            return
            
        menu = QMenu(self)
        
        rebase_action = QAction("Rebase Interativo a partir daqui...", self)
        rebase_action.triggered.connect(lambda: self.open_rebase_dialog(commit_hash))
        menu.addAction(rebase_action)
        
        menu.exec(global_pos)

    @Slot(str)
    def open_rebase_dialog(self, clicked_commit_hash):
        if not self.repo: return
        
        try:
            clicked_commit = self.repo.commit(clicked_commit_hash)
            
            if not clicked_commit.parents:
                self.log("ERRO: Não é possível fazer rebase do commit inicial.")
                QMessageBox.warning(self, "Rebase Inválido", "Não é possível fazer rebase a partir do commit inicial (root commit).")
                return
                
            if self._check_conflict_state(silent=True):
                self.log("ERRO: Não é possível iniciar um rebase enquanto estiver num estado de conflito.")
                QMessageBox.warning(self, "Rebase Inválido", "Você não pode iniciar um rebase enquanto resolve um conflito de merge ou rebase.")
                return

            parent_hash = clicked_commit.parents[0].hexsha
            commits = list(self.repo.iter_commits(f'{parent_hash}..HEAD'))
            commits.reverse()
            
            if not commits:
                self.log("Não há commits entre o selecionado e o HEAD para rebasear.")
                return

            dialog = RebaseDialog(commits, self)
            
            if dialog.exec():
                sequence = dialog.get_rebase_sequence()
                self.log("Iniciando rebase interativo...")
                self.set_ui_loading(True)
                self.request_interactive_rebase.emit(parent_hash, sequence)
            else:
                self.log("Rebase cancelado pelo utilizador.")
                
        except Exception as e:
            self.log(f"ERRO ao preparar o rebase: {e}")
            QMessageBox.critical(self, "Erro de Rebase", f"Não foi possível iniciar o rebase:\n{e}")
            
    def closeEvent(self, event):
        """Garante que a thread do worker é encerrada."""
        self.thread.quit()
        self.thread.wait()
        event.accept()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setStyleSheet(GITKRAKEN_LITE_QSS)
    
    window = GitApp()
    window.show()
    sys.exit(app.exec())