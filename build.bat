pyinstaller --noconfirm --log-level=WARN ^
    --onefile --noconsole ^
    --hidden-import=jinja2 ^
    --hidden-import=sqlite3 ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtWidgets ^
    --icon=bookshelf.ico ^
    --name "Bookshelf Exporter" ^
    book_exporter.basespec