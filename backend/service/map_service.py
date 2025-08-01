from backend.models.chat import MapState


class MapService:
    def __init__(self):
        self.map_state: MapStateData = MapStateData(
            active_layers=[],
            foot_increment="0",
            current_map_position=Boundaries(
                north=22.5, south=18.5, east=-154.0, west=-161.0
            ),
        )

    def get_state(self) -> MapStateData:
        return self.map_state

    def set_state(self, map_state: MapStateData):
        self.map_state = map_state
