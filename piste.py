import logging

# ------- Logging -------
try: # Error Catch for Sphinx Documentation
    # create logger
    logger = logging.getLogger('piste')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create file handler and set level to debug
    fh = logging.FileHandler('logs/tournament.log')
    fh.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    
except FileNotFoundError:
    pass


class Piste:
    def __init__(self, number_assigend) -> None:
        self.number = number_assigend
        self.staged = False
        self.occupied = False
        self.disabled = False

    @property
    def index(self):
        return self.number - 1

    @property
    def free_now(self) -> bool:
        return True if not self.staged and not self.occupied else False
    
    @property
    def status(self) -> str:
        if self.disabled:
            return 'disabled'
        elif self.occupied:
            return 'occupied'
        elif self.staged:
            return 'staged'
        else:
            return 'free'

    def match_finished(self):
        self.occupied = False

    def match_started(self, staged: bool = False):
        self.staged = staged
        self.occupied = True

    def reset(self):
        self.staged = False
        self.occupied = False

    def disable(self):
        self.disabled = True
        self.staged = False
        self.occupied = False