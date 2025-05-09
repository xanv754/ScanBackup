DATE = $(shell date +%Y-%m-%d)

updater: .venv/bin/activate
	.venv/bin/python3 -m updater data

updater-date: .venv/bin/activate
	.venv/bin/python3 -m updater data --date $(DATE)

setup: requirements.txt
	if [ ! -d ".venv" ]; then \
	   python3.13 -m venv .venv; \
	fi
	.venv/bin/pip install -r requirements.txt
	sudo python3.13 utils/log.py

migration: .venv/bin/activate
	.venv/bin/python3 -m storage migration

rollback: .venv/bin/activate
	.venv/bin/python3 -m storage rollback

clean:
	rm -rf __pycache__
	rm -rf .venv

test: .venv/bin/activate
	.venv/bin/python3 -m unittest discover -s $(PWD)/test/database -p "*_test.py"
	.venv/bin/python3 -m unittest discover -s $(PWD)/test/updater -p "*_test.py"
