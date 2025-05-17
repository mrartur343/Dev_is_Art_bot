import os

DB_FOLDER = "db"
os.makedirs(DB_FOLDER, exist_ok=True)
DB_NAME = os.path.join(DB_FOLDER, "chat_history.db")
SCHEDULED_DB = os.path.join(DB_FOLDER, "scheduled_commands.db")
VARIABLES_DB = os.path.join(DB_FOLDER, "variables.db")
CARDS_DB = os.path.join(DB_FOLDER, "user_cards.db")  # Додаємо нову БД для карток