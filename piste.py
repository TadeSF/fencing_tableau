class PisteError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Piste:
    def __init__(self, number_assigend) -> None:
        self.number = number_assigend
        self.staged = False
        self.occupied = False

    @property
    def index(self):
        return self.number - 1

    @property
    def free_now(self):
        return True if not self.staged and not self.occupied else False

    def match_finished(self):
        self.occupied = False

    def match_started(self):
        if self.occupied:
            raise PisteError("This Piste is already/still occupied")
        self.occupied = True
        self.staged = False
        print(f"Piste {self.number} started")