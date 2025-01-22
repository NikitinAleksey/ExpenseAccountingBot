import logging

__all__ = ["logged"]


class AppLogger:
    def __init__(self, name: str, log_file_name: str = None, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if log_file_name:
            self.logger.addHandler(console_handler)
            file_handler = logging.FileHandler(log_file_name)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str):
        """Логирование отладочных сообщений."""
        self.logger.debug(message)

    def info(self, message: str):
        """Логирование информационных сообщений."""
        self.logger.info(message)

    def warning(self, message: str):
        """Логирование предупреждений."""
        self.logger.warning(message)

    def error(self, message: str):
        """Логирование ошибок."""
        self.logger.error(message)

    def critical(self, message: str):
        """Логирование критических ошибок."""
        self.logger.critical(message)

    def set_level(self, level: int):
        """Изменить уровень логирования для этого логгера."""
        self.logger.setLevel(level)


def logged(name: str = None, log_file_name: str = None, level=logging.DEBUG):
    """
    Внешний декоратор для передачи аргументов в класс логгера.

    Применяется к классу для добавления атрибута `cls.log`, который является
    экземпляром логгера `AppLogger`. Логгер используется для записи логов
    с заданным именем, уровнем и (опционально) записью в файл.

    ВАЖНО: Декоратор всегда вызывается со скобками, даже если аргументы не передаются.
    Пример:
        @logged()
        class MyClass:
            pass

    Аргументы:
        name (str, optional): Имя логгера. Если не указано, используется имя класса.
        log_file_name (str, optional): Имя файла для записи логов. Если не указано, логи
                                       пишутся только в консоль (по настройке AppLogger).
        level (int, optional): Уровень логирования (по умолчанию DEBUG).

    Возвращает:
        cls: Класс с добавленным атрибутом `log`.
    """

    def wrapper(cls, **kwargs):
        """Декоратор для классов, добавляющий атрибут логирования cls.log."""
        logger_name = name if name else cls.__name__
        setattr(
            cls,
            "log",
            AppLogger(name=logger_name, log_file_name=log_file_name, level=level),
        )

        return cls

    return wrapper
