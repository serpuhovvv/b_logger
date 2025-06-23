
class DotDict(dict):
    """
    Gives access to dict through dots: obj.key instead of obj['key']
    """

    def __init__(self, data):
        super().__init__()
        for key, value in data.items():
            self[key] = self._wrap(value)

    def _wrap(self, value):
        if isinstance(value, dict):
            return DotDict(value)
        elif isinstance(value, list):
            return [self._wrap(item) for item in value]
        return value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            print(f"No such attribute: {key}")
            return None

    def __setattr__(self, key, value):
        self[key] = value
