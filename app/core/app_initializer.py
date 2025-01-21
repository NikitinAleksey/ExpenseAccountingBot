from app.db.connector import PostgresConnector

# TODO создать класс, который будет создавать все превичные настройки, обязательно СОЗДАТЬ КЛАСС КОННЕКТОР И ЗАКРЫТЬ ПУЛ В КОНЦЕ РАБОТЫ ПРИЛОЖЕНИЯ


class AppInitializer:
    def __init__(self):
        self.db_connector = PostgresConnector()

    def close_system(self):
        if self.db_connector:
            self.db_connector.close()
