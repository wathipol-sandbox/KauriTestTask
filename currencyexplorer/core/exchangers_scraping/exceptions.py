

class ExplorerPairInvalidFormatException(Exception):
    def __init__(
                self,
                description: str | None = "invalid pair string format."
            ) -> None:
        self.description = description
        super().__init__(self.description)

    @classmethod
    def explorer_pair_format_validator(CLS, pair: str) -> str:
        """ Return valid string pair if passed pair in valid format
                if format invalid raise ExplorerPairInvalidFormatException Exception
        """
        if pair is None:
            raise CLS(description="pair string can't NoneType")
        pair_items = str(pair).split("_")
        if len(pair_items) != 2:
            raise CLS(description="pair string should be in format COIN1_COIN2")
        return str(pair).upper()
