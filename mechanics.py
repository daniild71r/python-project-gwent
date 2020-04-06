import random as rand

deckSize = 20
handSize = 10
rows = 3
roundWinCondition = 2
messageLength = 4


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
    def __init__(self, player):
        self.player = player
        self.rowType = Unit.generateRow()
        self.strength = Unit.generateStrength()
        self.condition = ConditionType.inDeck

    @staticmethod
    def generateRow():
        return rand.randint(0, rows - 1)

    @staticmethod
    def generateStrength():
        strength = rand.randint(0, 2) * rand.randint(0, 2) + rand.randint(0, 6)
        if strength == 0:
            strength = 1
        return strength

    def play(self):
        row = self.player.rows[self.rowType]
        self.condition = ConditionType.inGame
        self.strength += row.activeCommanders
        row.units.append(self)
        row.updateSum()

    def getLabel(self):
        return str(self.strength)

    def getButtonLabel(self):
        return Row.rowNames[self.rowType] + " " + str(self.strength)

    unitRate = 5


class Commander(Unit):
    def __init__(self, player):
        self.player = player
        self.rowType = Commander.generateRow()
        self.strength = Commander.generateStrength()
        self.condition = ConditionType.inDeck

    @staticmethod
    def generateStrength():
        strength = rand.randint(0, 2) * rand.randint(0, 2) + rand.randint(0, 4)
        if strength == 0:
            strength = 1
        return strength

    def play(self):
        row = self.player.rows[self.rowType]
        self.condition = ConditionType.inGame
        self.strength += row.activeCommanders
        for unit in row.units:
            unit.strength += 1
        row.units.append(self)
        row.activeCommanders += 1
        row.updateSum()

    def getLabel(self):
        return "(" + str(self.strength) + ")"

    def getButtonLabel(self):
        return ("commander " + Row.rowNames[self.rowType] + " " +
                str(self.strength))


class Spy(Unit):
    def __init__(self, player):
        self.player = player
        self.rowType = Spy.generateRow()
        self.strength = Spy.generateStrength()
        self.condition = ConditionType.inDeck

    @staticmethod
    def generateStrength():
        strength = rand.randint(0, 2) * rand.randint(0, 3)
        if strength == 0:
            strength = 1
        return strength

    def play(self):
        row = self.player.rows[self.rowType]
        self.condition = ConditionType.inGame
        self.strength += row.activeCommanders
        row.units.append(self)
        for i in range(2):
            self.player.drawCard()
        row.updateSum()

    def getLabel(self):
        return "[" + str(self.strength) + "]"

    def getButtonLabel(self):
        return ("spy " + Row.rowNames[self.rowType] + " " +
                str(self.strength))


class Row:
    rowNames = ["melee", "ranged", "siege"]

    def __init__(self, rowType):
        self.rowType = rowType
        self.units = list()
        self.sum = 0
        self.activeCommanders = 0

    def updateSum(self):
        self.sum = 0
        for unit in self.units:
            self.sum += unit.strength

    def getLabel(self):
        if len(self.units) > 0:
            return " ".join(unit.getLabel() for unit in self.units)
        else:
            return "-"


class Player:
    def __init__(self, name):
        self.name = name
        self.roundsWon = 0
        self.units = list()
        self.deckTop = handSize
        self.generateDeck()
        self.rows = [Row(i) for i in range(rows)]

    def generateDeck(self):
        for i in range(deckSize):
            unitTry = rand.randint(0, Unit.unitRate)
            if unitTry == Unit.unitRate - 1:
                self.units.append(Commander(self))
            elif unitTry == Unit.unitRate:
                self.units.append(Spy(self))
            else:
                self.units.append(Unit(self))
        for i in range(handSize):
            self.units[i].condition = ConditionType.inHand
        self.deckTop = handSize

    def getLabel(self):
        count = self.countUnits()
        return (self.name + " won " + str(self.roundsWon) + " rounds. " +
                str(count[0]) + " units in hand and " + str(count[1]) +
                " more in deck.")

    def countUnits(self):
        inHand = 0
        inDeck = 0
        for unit in self.units:
            if unit.condition == ConditionType.inHand:
                inHand += 1
            elif unit.condition == ConditionType.inDeck:
                inDeck += 1
        return inHand, inDeck

    def getSum(self):
        result = 0
        for i in range(rows):
            result += self.rows[i].sum
        return result

    def drawCard(self):
        if self.deckTop < deckSize:
            self.units[self.deckTop].condition = ConditionType.inHand
            self.deckTop += 1

    def clearRows(self):
        for i in range(rows):
            for unit in self.rows[i].units:
                if unit.condition == ConditionType.inGame:
                    unit.condition = ConditionType.dead
            self.rows[i] = Row(i)

    def refresh(self):
        self.clearRows()
        self.units = list()
        self.generateDeck()
        self.roundsWon = 0


class AI(Player):
    def __init__(self, name, difficulty):
        self.name = name
        self.difficulty = difficulty
        self.roundsWon = 0
        self.deckTop = handSize
        self.units = list()
        self.generateDeck()
        self.rows = [Row(i) for i in range(rows)]

    def generateDeck(self):
        for i in range(deckSize):
            unitTry = rand.randint(0, Unit.unitRate)
            if unitTry == Unit.unitRate - 1:
                self.units.append(Commander(self))
            elif unitTry == Unit.unitRate:
                self.units.append(Spy(self))
            else:
                self.units.append(Unit(self))
        for i in range(handSize):
            self.units[i].condition = ConditionType.inHand
        self.deckTop = handSize
        for unit in self.units:
            unit.strength += self.difficulty

    def getUnitOptions(self):
        options = list()
        for i in range(deckSize):
            unit = self.units[i]
            if unit.condition == ConditionType.inHand:
                options.append(unit)
        return options

    def chooseUnit(self, opponent, opponentPassed=False):
        mySum = self.getSum()
        opponentSum = opponent.getSum()

        # if opponent passed, then try to finish him
        if opponentPassed:
            if mySum > opponentSum:
                return 0
            options = self.getUnitOptions()
            for unit in options:
                add = unit.strength + self.rows[unit.rowType].activeCommanders
                if mySum + add > opponentSum:
                    return unit
            return 0

        # if the situation is not critical, then possibly pass
        if mySum > opponentSum + AI.strengthThreshold:
            return 0
        if max(self.roundsWon, opponent.roundsWon) < roundWinCondition - 1:
            passTry = rand.randint(0, AI.passRate)
            if passTry == AI.passRate:
                return 0

        # case is not that simple, so make a random turn :)
        options = self.getUnitOptions()
        return rand.choice(options) if len(options) > 0 else 0

    strengthThreshold = 12
    passRate = 5
