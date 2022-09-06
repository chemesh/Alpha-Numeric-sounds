from spleeter.separator import Separator

class SingleSeperator(Separator):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingleSeperator, cls).__new__(cls, "spleeter:5stems")
        return cls.instance
