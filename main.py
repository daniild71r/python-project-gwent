import abc
import tkinter as tk
import tkinter.messagebox as messagebox
import mechanics


class Texts:
    def __init__(self):
        textSource = open("txt/texts.txt", "r")
        lines = textSource.read().splitlines()
        iterator = iter(lines)
        self.gameName = next(iterator)
        self.playerNames = list()
        for i in range(2):
            self.playerNames.append(next(iterator))

        self.difficultyQuestion = list()
        for i in range(2):
            self.difficultyQuestion.append(next(iterator))
        self.difficultyOptions = list()
        for i in range(4):
            self.difficultyOptions.append(next(iterator))

        self.fractionQuestion = list()
        for i in range(2):
            self.fractionQuestion.append(next(iterator))
        self.fractionOptions = list()
        for i in range(2):
            self.fractionOptions.append(next(iterator))

        self.rowTypes = list()
        for i in range(3):
            self.rowTypes.append(next(iterator))
        self.rowCaptions1 = list()
        for i in range(3):
            self.rowCaptions1.append(next(iterator))
        self.rowCaptions2 = list()
        for i in range(3):
            self.rowCaptions2.append(next(iterator))

        self.passTurn = next(iterator)
        self.opponentPassed = next(iterator)
        self.opponentPassedMessage = next(iterator)
        self.roundEnded = next(iterator)
        self.gameEnded = next(iterator)
        self.endingMessage = list()
        for i in range(4):
            self.endingMessage.append(next(iterator))
        self.endingActions = list()
        for i in range(3):
            self.endingActions.append(next(iterator))
        textSource.close()


class Labeler:
    def __init__(self):
        pass

    def getUnitLabel(self, unit):
        return str(unit.strength)

    def getCommanderLabel(self, commander):
        return "(" + str(commander.strength) + ")"

    def getSpyLabel(self, spy):
        return "[" + str(spy.strength) + "]"

    def getRowLabel(self, row):
        if len(row.units) > 0:
            return " ".join(unit.acceptLabeler(self) for unit in row.units)
        else:
            return "-"

    def getPlayerLabel(self, player):
        count = player.countUnits()
        label = "{} ({}) won {} rounds.\n{} units in hand and {} more in deck."
        return label.format(
            player.name, texts.fractionOptions[player.fraction],
            player.roundsWon, count[0], count[1]
        )


class ButtonLabeler(Labeler):
    def getUnitLabel(self, unit):
        return texts.rowTypes[unit.rowType] + " " + str(unit.strength)

    def getCommanderLabel(self, commander):
        return ("commander " + texts.rowTypes[commander.rowType] + " " +
                str(commander.strength))

    def getSpyLabel(self, spy):
        return "spy " + texts.rowTypes[spy.rowType] + " " + str(spy.strength)


class Configurator:
    def __init__(self, manager):
        self.manager = manager
        self.questionText = tk.StringVar()
        self.questionLabel = tk.Label(self.manager.root, width=60,
                                      textvariable=self.questionText)
        self.questionLabel.pack()
        self.optionsFrame = tk.Frame(self.manager.root)
        self.optionsFrame.pack(side=tk.BOTTOM)
        self.buttons = list()
        self.answers = [0, 0]

    def askQuestion(self, questionNumber, questionText, options):
        self.questionText.set(questionText)
        for i in range(len(options)):
            method = self.createButtonMethod(questionNumber, i)
            button = tk.Button(self.optionsFrame, text=options[i],
                               command=method)
            self.buttons.append(button)
            button.pack()

    def selectDifficulty(self):
        question = "\n".join(texts.difficultyQuestion)
        self.askQuestion(0, question, texts.difficultyOptions)

    def selectFraction(self):
        question = "\n".join(texts.fractionQuestion)
        self.askQuestion(1, question, texts.fractionOptions)

    def createButtonMethod(self, questionNumber, value):
        def unitMethod():
            for button in self.buttons:
                button.destroy()
                self.buttons = list()
            self.answers[questionNumber] = value
            if questionNumber == 0:
                self.selectFraction()
            else:
                self.endConfiguration()
        return unitMethod

    def endConfiguration(self):
        self.questionLabel.destroy()
        self.optionsFrame.destroy()
        self.manager.startGame(self.answers[0], self.answers[1])


class InterfaceElement:
    @abc.abstractmethod
    def place(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class PlayerElement(InterfaceElement):
    def __init__(self, root, player):
        self.player = player
        self.state = tk.StringVar()
        labeler = Labeler()
        self.state.set(self.player.acceptLabeler(labeler))
        self.label = tk.Label(root, width=60, textvariable=self.state)

    def place(self, startingRow, startingColumn):
        self.label.grid(row=startingRow, column=startingColumn, columnspan=3)

    def update(self):
        labeler = Labeler()
        self.state.set(self.player.acceptLabeler(labeler))


class RowsElement(InterfaceElement):
    def __init__(self, root, player, captions):
        self.player = player
        self.rows = list()
        self.rowSums = list()
        for i in range(mechanics.rows):
            self.rows.append(tk.StringVar())
            self.rows[i].set("-")
            self.rowSums.append(tk.StringVar())
            self.rowSums[i].set("0")

        self.rowCaptionLabels = list()
        self.rowLabels = list()
        self.rowSumLabels = list()
        for i in range(mechanics.rows):
            self.rowCaptionLabels.append(tk.Label(
                root, anchor=tk.E, width=20, relief=tk.RIDGE, text=captions[i])
            )
            self.rowSumLabels.append(tk.Label(
                root, width=3, relief=tk.RIDGE, textvariable=self.rowSums[i])
            )
            self.rowLabels.append(tk.Label(
                root, width=35, anchor=tk.W, relief=tk.RIDGE,
                textvariable=self.rows[i])
            )

    def place(self, startingRow, startingColumn, inverse=False):
        for i in range(mechanics.rows):
            rowIndex = startingRow + i if not inverse else startingRow + 2 - i
            self.rowCaptionLabels[i].grid(row=rowIndex, column=startingColumn)
            self.rowSumLabels[i].grid(row=rowIndex, column=startingColumn + 1)
            self.rowLabels[i].grid(row=rowIndex, column=startingColumn + 2)

    def update(self, rowType):
        row = self.player.rows[rowType]
        labeler = Labeler()
        self.rows[rowType].set(row.acceptLabeler(labeler))
        self.rowSums[rowType].set(str(row.sum))


class UnitsElement(InterfaceElement):
    def __init__(self, game, player, playerElement, rowsElement):
        self.game = game
        self.player = player
        self.playerElement = playerElement
        self.rowsElement = rowsElement

        self.handFrame = tk.Frame(game.root)
        self.handButtons = list()
        self.update()

        method = self.passMethod
        passButton = tk.Button(self.handFrame, text=texts.passTurn,
                               command=method)
        passButton.pack(side=tk.BOTTOM)

    def place(self, startingRow, startingColumn):
        self.handFrame.grid(row=startingRow, column=startingColumn,
                            columnspan=3)

    def update(self):
        unitCounter = 0
        for unit in self.player.units:
            if unit.condition == mechanics.ConditionType.inHand and \
                    unitCounter >= len(self.handButtons):
                self.createUnitButton(unitCounter)
            unitCounter += 1

    def createUnitButton(self, i):
        unit = self.player.units[i]
        buttonLabeler = ButtonLabeler()
        label = unit.acceptLabeler(buttonLabeler)
        method = self.createUnitMethod(i, unit)
        button = tk.Button(self.handFrame, text=label, command=method)
        self.handButtons.append(button)
        button.pack(side=tk.TOP)

    def createUnitMethod(self, i, unit):
        def unitMethod():
            self.handButtons[i].destroy()
            unit.play()
            self.playerElement.update()
            self.rowsElement.update(unit.rowType)
            self.update()
            self.game.switchTurns()
        return unitMethod

    def passMethod(self):
        self.game.passRound()


# everything with index 1 refers to player, with index 2 refers to opponent
class gameInterface:
    def __init__(self, game, player1, player2):
        self.root = game.root
        self.player1 = player1
        self.player2 = player2

        self.playerInterface1 = PlayerElement(self.root, self.player1)
        self.playerInterface2 = PlayerElement(self.root, self.player2)
        self.playerInterface2.place(1, 1)
        self.playerInterface1.place(8, 1)

        self.rowsInterface1 = RowsElement(self.root, self.player1,
                                          texts.rowCaptions1)
        self.rowsInterface2 = RowsElement(self.root, self.player2,
                                          texts.rowCaptions2)
        self.rowsInterface2.place(2, 1, inverse=True)
        self.rowsInterface1.place(5, 1)

        self.unitsInterface = UnitsElement(
            game, self.player1, self.playerInterface1, self.rowsInterface1
        )
        self.unitsInterface.place(9, 1)


class Game:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(texts.gameName)
        self.root.iconphoto(True, tk.PhotoImage(file="img/geralt_32.png"))
        configurator = Configurator(self)
        configurator.selectDifficulty()
        self.interface = None
        self.player1 = None
        self.player2 = None
        self.opponentPassed = False

    def startGame(self, difficulty, fraction):
        self.player1 = mechanics.Player(texts.playerNames[0], fraction)
        self.player2 = mechanics.AI(texts.playerNames[1], difficulty)
        self.player1.generateDeck(deckGenerator)
        self.player2.generateDeck(deckGenerator)
        self.interface = gameInterface(self, self.player1, self.player2)

    def switchTurns(self):
        if self.opponentPassed:
            self.endRound()
        else:
            self.opponentTurn()

    def opponentTurn(self, lastTurn=False):
        unit = self.player2.chooseUnit(self.player1, lastTurn)
        if unit != 0:
            unit.play()
            self.interface.playerInterface2.update()
            self.interface.rowsInterface2.update(unit.rowType)
        elif not lastTurn:
            self.opponentPassed = True
            text = texts.opponentPassedMessage.format(self.player2.name)
            messagebox.showinfo(title=texts.opponentPassed, message=text)

    def passRound(self):
        if not self.opponentPassed:
            self.opponentTurn(lastTurn=True)
        self.endRound()

    def endRound(self):
        sum1 = self.player1.getSum()
        sum2 = self.player2.getSum()
        lines = [line + "\n" for line in texts.endingMessage]

        if self.opponentPassed:
            lines[0] = lines[0].format(self.player2.name, self.player1.name)
        else:
            lines[0] = lines[0].format(self.player1.name, self.player2.name)
        self.opponentPassed = False

        gameEnded = False
        if sum1 > sum2:
            action = texts.endingActions[0]
            self.player1.roundsWon += 1
            if self.player1.roundsWon == mechanics.roundWinCondition:
                gameEnded = True
        elif sum1 == sum2:
            action = texts.endingActions[1]
        else:
            action = texts.endingActions[2]
            self.player2.roundsWon += 1
            if self.player2.roundsWon == mechanics.roundWinCondition:
                gameEnded = True
        lines[1] = lines[1].format(sum1, sum2, action)

        if gameEnded:
            lines[2] = lines[2].format(action)
            message = lines[0] + lines[1] + lines[2] + lines[3]
            if messagebox.askyesno(title=texts.gameEnded, message=message):
                self.newGame()
            else:
                quit()
        else:
            message = lines[0] + lines[1] + lines[3]
            if messagebox.askyesno(title=texts.roundEnded, message=message):
                self.newRound()
            else:
                quit()

    def clearBoard(self):
        self.interface.playerInterface1.update()
        self.interface.playerInterface2.update()
        self.player1.clearRows()
        self.player2.clearRows()
        for i in range(mechanics.rows):
            self.interface.rowsInterface1.update(i)
            self.interface.rowsInterface2.update(i)

    def newRound(self):
        self.player1.drawCard()
        self.player2.drawCard()
        self.clearBoard()
        self.interface.unitsInterface.update()

    def newGame(self):
        self.player1.refresh(deckGenerator)
        self.player2.refresh(deckGenerator)
        self.clearBoard()
        for button in self.interface.unitsInterface.handButtons:
            button.destroy()
        self.interface.unitsInterface.handButtons = list()
        self.interface.unitsInterface.update()


deckGenerator = mechanics.DeckGenerator()
texts = Texts()
gwentGame = Game()
gwentGame.root.mainloop()
