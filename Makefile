all: app

init:
	pip install -r requirements.txt

dev:
	python -B src/main.py

app:
	pyinstaller --clean -F src/main.py --noconsole -n "Discord Botspam Removal Tool"
