class CSVError(Exception):
    pass

class RequiredLibraryError(Exception):
    pass

class SearchError(Exception):
    pass

class PisteError(Exception):
    pass

class OccupiedPisteError(PisteError):
    pass

class StageError(Exception):
    pass

class TournamentError(Exception):
    pass