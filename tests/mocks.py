class MockLogger:
    errors = []
    logs = []

    def __log(self, category, message):
        self.logs.append(f"{category}: {message}")

    def error(self, message: str):
        self.__log("ERROR", message)
        self.errors.append(message)

    def warn(self, message: str):
        self.__log("WARN", message)

    def info(self, message: str):
        self.__log("INFO", message)

    def debug(self, message: str):
        self.__log("DEBUG", message)
