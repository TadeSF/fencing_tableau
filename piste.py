import logging

# Logging
try: # Error catch for Sphinx Documentation
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler('logs/tournament.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
except FileNotFoundError:
    pass


class Piste:
    def __init__(self, number_assigend) -> None:
        self.number = number_assigend
        self.staged = False
        self.occupied = False

    @property
    def index(self):
        return self.number - 1

    @property
    def free_now(self) -> bool:
        return True if not self.staged and not self.occupied else False

    def match_finished(self):
        self.occupied = False

    def match_started(self, staged: bool = False):
        self.staged = staged
        self.occupied = True

    def reset(self):
        self.staged = False
        self.occupied = False