from core.Dice import Dice
from typing import Optional

class TreasureHoardCoins:
    copper_coins_dice: Optional[Dice]
    copper_coins_value: int
    silver_coins_dice: Optional[Dice]
    silver_coins_value: int
    gold_coins_dice: Optional[Dice]
    gold_coins_value: int

class TreasureHoard:
    d100: int
    gemsOrArtObjects_dice: Optional[Dice] = None
    gemsOrArtObjects_value: str
    gemsOrArtObjects_type: str
    magicItems_dice: Optional[Dice] = None
    magicItems_table: str

    def __init__(self, **kwargs):
        self.d100 = kwargs.pop("d100", None)


        gemsOrArtObjects_dice_amount = kwargs.pop("gemsOrArtObjects_dice_amount", None)
        gemsOrArtObjects_dice_type = kwargs.pop("gemsOrArtObjects_dice_type", None)
        if gemsOrArtObjects_dice_amount:
            self.gemsOrArtObjects_dice = Dice(amount=gemsOrArtObjects_dice_amount, type=gemsOrArtObjects_dice_type)
        self.gemsOrArtObjects_value = kwargs.pop("gemsOrArtObjects_value", None)
        self.gemsOrArtObjects_type = kwargs.pop("gemsOrArtObjects_type", None)

        magicItems_dice_amount = kwargs.pop("magicItems_dice_amount", None)
        magicItems_dice_type = kwargs.pop("magicItems_dice_type", None)
        if magicItems_dice_amount:
            self.magicItems_dice = Dice(amount=magicItems_dice_amount, type=magicItems_dice_type)
        self.magicItems_table = kwargs.pop("magicItems_table", None)
        