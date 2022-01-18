import sqlite3
from jinja2 import Environment, PackageLoader, select_autoescape
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLabel, QFileDialog)

TEMPLATE_STR = """
<HTML>
    <HEAD>
        <TITLE>Book Report</TITLE>
    </HEAD>
    <BODY BGCOLOR="#FFFFFF" TEXT="#000000" LINK="#0000FF">
    {% for entry in entries %}
    <p>
        <b>[{{ entry.inventory_id }}] {{ entry.author }} "{{ entry.title }}"; </b>
        {% if entry.isbn %}
        ISBN: {{ entry.isbn }}
        {% endif %}
        {% if entry.mfg_place %}
        {{ entry.mfg_place }}: {{ entry.publisher }}, {{ entry.year_published }}.
        {% else %}
        {{ entry.publisher }}, {{ entry.year_published -}}.
        {% endif %}
        {{ entry.description }}
    </p>
    {% endfor %}
    </BODY>
</HTML>
"""

class DBSelectWidget(QWidget):
    def __init__(self, parent=None):
        super(DBSelectWidget, self).__init__(parent)

        self.fname = None
        layout = QHBoxLayout()

        self.label = QLabel("No database selected")
        self.select_button = QPushButton("Select DB")

        self.select_button.clicked.connect(self.select_db)

        layout.addWidget(self.label)
        layout.addWidget(self.select_button)

        self.setLayout(layout)

    def get_filename(self):
        if self.fname is None:
            return None
        else:
            return self.fname[0]

    def select_db(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Open file', '~/', "BKP files (*.bkp *.db)")
        self.label.setText(self.fname[0])


class OutputSelectWidget(QWidget):
    def __init__(self, parent=None):
        super(OutputSelectWidget, self).__init__(parent)

        self.fname = None
        self.label = QLabel("No file selected")
        self.select_button = QPushButton("Select Output File")
        self.select_button.clicked.connect(self.select_file)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.select_button)

        self.setLayout(layout)

    def get_filename(self):
        if self.fname is None:
            return None
        else:
            return self.fname[0]

    def select_file(self):
        self.fname = QFileDialog.getSaveFileName(
            self, "Save F:xile",
            "output.html",
           "HTML files (*.html *.htm)")

        self.label.setText(self.fname[0])


class BookshelfExporter(QWidget):
    def __init__(self, parent=None):
        super(BookshelfExporter, self).__init__(parent)

        # Layout elements
        layout = QVBoxLayout()
        action_buttons_layout = QHBoxLayout()

        # Widget define-o!
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        self.db_select_widget = DBSelectWidget()
        self.output_select_widget = OutputSelectWidget()

        # Set up the action buttons layout
        action_buttons_layout.addWidget(cancel_button)
        action_buttons_layout.addWidget(ok_button)

        # Button up our layout
        layout.addWidget(self.db_select_widget)
        layout.addWidget(self.output_select_widget)
        layout.addLayout(action_buttons_layout)
        self.setLayout(layout)

        # Set behaviors
        ok_button.clicked.connect(self.export_file)
        cancel_button.clicked.connect(self.exit_application)

    def export_file(self):
        db_filename = self.db_select_widget.get_filename()
        out_filename = self.output_select_widget.get_filename()

        if not all([db_filename, out_filename]):
            return None

        env = Environment()
        template = env.from_string(source=TEMPLATE_STR)
        conn = sqlite3.connect(self.db_select_widget.get_filename())
        conn.row_factory = sqlite3.Row

        entries = conn.execute("""
            SELECT
                inventoryId as inventory_id,
                primaryName as title,
                primaryCreator as author,
                mfgPlace as mfg_place,
                mfgYear as year_published,
                mfgName as publisher,
                primaryIdent as isbn,
                description
            FROM
                Listing
            WHERE
                privateNotes like '%LIST%'
            ORDER BY
                inventoryId ASC""")

        with open(self.output_select_widget.get_filename(), 'w', encoding="utf-8") as f:
            f.write(template.render(entries=entries))

        self.exit_application()

    def exit_application(self):
        QApplication.quit()


app = QApplication([])
app.setApplicationName("Bookshelf Exporter")
window = BookshelfExporter()
window.show()
app.exec()

