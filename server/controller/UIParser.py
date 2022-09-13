import json

from server.controller.UIDataModels import EA_Parameters


class UIParser:

    @classmethod
    def parse_ea_params(cls, raw_json):
        raw = json.loads(raw_json)
        return EA_Parameters(
            generations=raw.get('generations'),
            population=raw.get('population'),
            selection=raw.get('selection') / 100,
            mutation=raw.get('mutation') / 100,
            crossover=raw.get('crossover') / 100
        )