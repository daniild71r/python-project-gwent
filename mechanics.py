import copy
import random as rand

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


class Fraction:
    north = 0
    nilfgaard = 1


class Unit:
    def __init__(self):
        self.player = None
        self.rowType = Unit.generateRow()
        self.strength = Unit.generateStrength()
        self.condition = ConditionType.inDeck

    def setPlayer(self, player):
        self.player = player

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

    def acceptLabeler(self, labeler):
        return labeler.getUnitLabel(self)

    unitRate = 5


class Commander(Unit):
    def __init__(self):
        self.player = None
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

    def acceptLabeler(self, labeler):
        return labeler.getCommanderLabel(self)


class Spy(Unit):
    def __init__(self):
        self.player = None
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

    def acceptLabeler(self, labeler):
        return labeler.getSpyLabel(self)


class Row:
    def __init__(self, rowType):
        self.rowType = rowType
        self.units = list()
        self.sum = 0
        self.activeCommanders = 0

    def updateSum(self):
        self.sum = 0
        for unit in self.units:
            self.sum += unit.strength

    def acceptLabeler(self, labeler):
        return labeler.getRowLabel(self)


class DeckGenerator:
    def __init__(self):
        self.preset = list()
        for i in range(DeckGenerator.basicUnits):
            self.preset.append(Unit())

    def getDeck(self, player):
        newDeck = list()
        for unit in self.preset:
            newDeck.append(copy.copy(unit))

        if player.fraction == Fraction.north:
            for i in range(DeckGenerator.firstUnique):
                newDeck.append(Commander())
                newDeck[-1].strength += 2
            for i in range(DeckGenerator.secondUnique):
                newDeck.append(Spy())
        elif player.fraction == Fraction.nilfgaard:
            for i in range(DeckGenerator.firstUnique):
                newDeck.append(Spy())
                newDeck[-1].strength += 2
            for i in range(DeckGenerator.secondUnique):
                newDeck.append(Commander())

        for i in range(Player.deckSize):
            newDeck[i].setPlayer(player)
        rand.shuffle(newDeck)
        for i in range(Player.handSize):
            newDeck[i].condition = ConditionType.inHand
        return newDeck

    basicUnits = 13
    firstUnique = 5
    secondUnique = 2


class Player:
    def __init__(self, name, fraction=Fraction.north):
        self.name = name
        self.fraction = fraction
        self.roundsWon = 0
        self.units = list()
        self.deckTop = 0
        self.rows = [Row(i) for i in range(rows)]

    def generateDeck(self, deckGenerator):
        self.innerGenerateDeck(deckGenerator)

    def innerGenerateDeck(self, deckGenerator):
        self.units = deckGenerator.getDeck(self)
        self.deckTop = Player.handSize

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
        if self.deckTop < Player.deckSize:
            self.units[self.deckTop].condition = ConditionType.inHand
            self.deckTop += 1

    def clearRows(self):
        for i in range(rows):
            for unit in self.rows[i].units:
                if unit.condition == ConditionType.inGame:
                    unit.condition = ConditionType.dead
            self.rows[i] = Row(i)

    def refresh(self, deckGenerator):
        self.clearRows()
        self.units = list()
        self.generateDeck(deckGenerator)
        self.roundsWon = 0

    def acceptLabeler(self, labeler):
        return labeler.getPlayerLabel(self)

    deckSize = 20
    handSize = 10


class AI(Player):
    def __init__(self, name, difficulty):
        super().__init__(name)
        self.difficulty = difficulty

    def generateDeck(self, deckGenerator):
        self.innerGenerateDeck(deckGenerator)
        for unit in self.units:
            unit.strength += self.difficulty

    def getUnitOptions(self):
        options = list()
        for unit in self.units:
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
