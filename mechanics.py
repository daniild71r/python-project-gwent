import random as rand
handSize = 12
rows = 3


class RowType:
    melee = 0
    ranged = 1
    siege = 2


class ConditionType:
    inDeck = 0
    inHand = 1
    inGame = 2
    dead = 3


class Unit:
    def __init__(self):
        self.rowType = Unit.generateRow()
        self.strength = Unit.generateStrength()
        self.condition = ConditionType.inHand

    @staticmethod
    def generateRow():
        return rand.choice([RowType.melee, RowType.ranged, RowType.siege])

    @staticmethod
    def generateStrength():
        strength = rand.randint(0, 2) * rand.randint(0, 3) + rand.randint(0, 4)
        if strength == 0:
            strength = 1
        return strength

    def play(self, row):
        self.condition = ConditionType.inGame
        row.units.append(self)
        row.updateRow()

    def getButtonLabel(self):
        if self.rowType == 0:
            return "melee " + str(self.strength)
        elif self.rowType == 1:
            return "ranged " + str(self.strength)
        else:
            return "siege " + str(self.strength)


class Commander(Unit):
    def __init__(self):
        self.rowType = Commander.generateRow()
        self.strength = Commander.generateStrength()
        self.condition = ConditionType.inHand

    @staticmethod
    def generateStrength():
        strength = rand.randint(0, 2) * rand.randint(0, 3)
        if strength == 0:
            strength = 1
        return strength

    def play(self, row):
        self.condition = ConditionType.inGame
        for unit in row.units:
            unit.strength += 1
        row.units.append(self)
        row.updateRow()

    def getButtonLabel(self):
        if self.rowType == 0:
            return "commander melee " + str(self.strength)
        elif self.rowType == 1:
            return "commander ranged " + str(self.strength)
        else:
            return "commander siege " + str(self.strength)


class Row:
    def __init__(self, rowType):
        self.rowType = rowType
        self.units = list()
        self.sum = 0

    def updateRow(self):
        self.sum = 0
        for unit in self.units:
            self.sum += unit.strength

    def getLabel(self):
        if len(self.units) > 0:
            return " ".join(str(unit.strength) for unit in self.units)
        else:
            return "-"


class Player:
    def __init__(self, name):
        self.name = name
        self.roundsWon = 0
        self.units = list()
        self.generateHand()
        self.rows = [Row(i) for i in range(rows)]

    # generating hand is oversimplified, might be improved
    def generateHand(self):
        for i in range(handSize - 1):
            self.units.append(Unit())
        self.units.append(Commander())

    def getLabel(self):
        unitsInHand = 0
        for unit in self.units:
            if unit.condition == ConditionType.inHand:
                unitsInHand += 1
        return (self.name + " won " + str(self.roundsWon) + " rounds. " +
                str(unitsInHand) + " units in hand")

    def chooseUnit(self):
        possibleCards = []
        for i in range(handSize):
            unit = self.units[i]
            if unit.condition == ConditionType.inHand:
                possibleCards.append(unit)
        if len(possibleCards) == 0:
            return 0
        else:
            return rand.choice(possibleCards)

    def refresh(self):
        self.units = list()
        self.generateHand()
        self.rows = [Row(i) for i in range(rows)]
