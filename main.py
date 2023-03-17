import os
import sys
import tempfile
import webbrowser
from pathlib import Path

from PySide2.QtCore import Qt, QMimeData, QUrl
from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

class PyOutlineExplorer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyOutlineExplorer")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.info_label = QLabel("Drag and drop a directory here")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.setLayout(layout)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.process_directory(path)
                break

    def process_directory(self, path):
        hierarchy = self.build_hierarchy(path)
        self.trim_hierarchy(hierarchy)
        html = self.generate_html(hierarchy)
        html_path = self.save_html(html)
        webbrowser.open(html_path)

    def build_hierarchy(self, path):
        hierarchy = {}
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    hierarchy[filepath] = self.extract_outline(filepath)
        return hierarchy

    def extract_outline(self, filepath):
        outline = []

        with open(filepath, "r") as file:
            inside_docstring = False
            for line in file:
                stripped_line = line.strip()

                if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
                    inside_docstring = not inside_docstring

                if not stripped_line.startswith("#") and stripped_line and not inside_docstring:
                    outline.append(line)

        return outline

    def generate_html(self, hierarchy):
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>PyOutlineExplorer</title>",
            "<style>",
            "pre {",
            "  white-space: pre-wrap;",
            "  font-family: monospace;",
            "}",
            "</style>",
            "</head>",
            "<body>"
        ]

        for filepath, outline in hierarchy.items():
            html.append(f"<h3>{filepath}</h3>")
            html.append("<pre>")
            html.extend(outline)
            html.append("</pre>")

        html.extend(["</body>", "</html>"])

        return "\n".join(html)

    def save_html(self, html):
        temp_dir = Path(tempfile.gettempdir()) / "PyOutlineExplorer"
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / "outline.html"

        with open(temp_file, "w") as file:
            file.write(html)

        return temp_file

    def trim_hierarchy(self, hierarchy):
        MAX_WORDS = 3500
        total_words = sum(len(''.join(outline).split()) for outline in hierarchy.values())

        while total_words > MAX_WORDS:
            min_len = float("inf")
            min_file = None

            for filepath, outline in hierarchy.items():
                for line in outline:
                    line_words = line.split()
                    line_word_count = len(line_words)
                    if line_word_count < min_len and "def " in line:
                        min_len = line_word_count
                        min_file = filepath

            if min_file:
                stripped_outline = []
                for line in hierarchy[min_file]:
                    if "def " in line:
                        func_name = line.split()[1].split("(")[0]
                        stripped_outline.append(f"{func_name}\n")
                        total_words -= min_len - 1
                    else:
                        stripped_outline.append(line)
                hierarchy[min_file] = stripped_outline
            else:
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyOutlineExplorer()
    window.show()
    sys.exit(app.exec_())