# Load environment variables from .env
ifneq ("$(wildcard .env)","")
    include .env
    export
endif

# --- Installation & Setup ---
install:
	pip install pipenv
	pipenv install -r requirements.txt
	npm install --prefix frontend

# --- Database & Docker ---
db-up:
	docker compose --env-file .env up -d

db-down:
	docker compose down

db-clean:
	docker compose down -v --rmi all

# --- Data & Utilities ---
# No need to manually export $(grep...) because of the 'include .env' at the top
seed:
	pipenv run python seed_data.py

verify:
	pipenv run python verify_setup.py

# --- Execution ---
# Start FastAPI Backend
api:
	pipenv run python main.py

# Start Streamlit Frontend
streamlit:
	pipenv run streamlit run streamlit_app.py

# Start React Frontend (Vite)
react:
	npm run dev --prefix frontend

# --- Development Shortcuts ---
# Runs Backend and Streamlit simultaneously using 'make -j' (jobs)
dev:
	make -j 2 api streamlit

# Full reset: Clean everything and restart
reset:
	pipenv --rm
	docker compose down -v --rmi all
	make install

# --- Browser Helpers ---
# Detects OS to use correct 'open' command
ifeq ($(OS),Windows_NT)
    OPEN_CMD := start
else
    OPEN_CMD := xdg-open
endif

# --- The "Big Green Button" ---
# 1. Starts DB, 2. Starts API, 3. Starts React, 4. Opens Browser
all:
	@echo "🚀 Starting the full stack..."
	@make db-up
	@echo "⏳ Waiting for DB to be healthy..."
	@sleep 5
	@echo "🌐 Opening browser..."
	@$(OPEN_CMD) http://localhost:5173
	@make -j 2 api react

# Alternative: FastAPI + Streamlit
all-streamlit:
	@make db-up
	@sleep 5
	@$(OPEN_CMD) http://localhost:8501
	@make -j 2 api streamlit