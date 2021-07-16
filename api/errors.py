class NoCache(Exception):
    def __str__(self) -> str:
        return "No cache was found!"