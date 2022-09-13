import json

from controller.UIDataModels import EA_Parameters


class UIParser:

    @classmethod
    def parse_ea_params(cls, raw):
        raw = {k.upper() : v for k,v in raw.items()}
        return EA_Parameters(
            generations=int(raw.get('GENERATIONS')),
            population=int(raw.get('POPULATION')),
            selection=float(raw.get('SELECTION')) / 100,
            mutation=float(raw.get('MUTATION')) / 100,
            crossover=float(raw.get('CROSSOVER')) / 100
        )