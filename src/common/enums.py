from choicesenum import ChoicesEnum as BaseChoicesEnum


class ChoicesEnum(BaseChoicesEnum):
    @classmethod
    def choices(cls) -> list[dict[str, str]]:
        return [{"value": x.value, "label": x.display} for x in cls]  # type: ignore
