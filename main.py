import tkinter as tk
import tkinter.messagebox as messagebox
import mechanics


class PlayerInterface:
    def __init__(self, root, player):
        self.player = player
        self.state = tk.StringVar()
        self.state.set(player.getLabel())
        self.label = tk.Label(root, width=60, textvariable=self.state)

    def place(self, startingRow, startingColumn):
        self.label.grid(row=startingRow, column=startingColumn,
                        columnspan=3)

    def update(self):
        self.state.set(self.player.getLabel())


class RowsInterface:
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
            self.rowCaptionLabels.append(
                tk.Label(root, anchor=tk.E, width=20, relief=tk.RIDGE,
                         text=captions[i])
            )
            self.rowSumLabels.append(
                tk.Label(root, width=3, relief=tk.RIDGE,
                         textvariable=self.rowSums[i])
            )
            self.rowLabels.append(
                tk.Label(root, width=35, anchor=tk.W, relief=tk.RIDGE,
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
        self.rows[rowType].set(row.getLabel())
        self.rowSums[rowType].set(str(row.sum))


class ButtonsInterface:
    def __init__(self, root, player, playerInterface, rowsInterface):
        self.player = player
        self.playerInterface = playerInterface
        self.rowsInterface = rowsInterface

        self.handFrame = tk.Frame(root)
        self.handButtons = list()
        self.update()

        method = self.passMethod
        passButton = tk.Button(self.handFrame, text="Pass", command=method)
        passButton.pack(side=tk.BOTTOM)

    def place(self, startingRow, startingColumn):
        self.handFrame.grid(row=startingRow, column=startingColumn,
                            columnspan=3)

    def update(self):
        for i in range(mechanics.deckSize):
            unit = self.player.units[i]
            if (unit.condition == mechanics.ConditionType.inHand and
                    i >= len(self.handButtons)):
                self.createUnitButton(i)

    def createUnitButton(self, i):
        unit = self.player.units[i]
        label = unit.getButtonLabel()
        method = self.createUnitMethod(i, unit)
        button = tk.Button(self.handFrame, text=label, command=method)
        self.handButtons.append(button)
        button.pack(side=tk.TOP)

    def createUnitMethod(self, i, unit):
        def unitMethod():
            self.handButtons[i].destroy()
            unit.play()
            self.playerInterface.update()
            self.rowsInterface.update(unit.rowType)
            self.update()
            gameManager.switchTurns()
        return unitMethod

    @staticmethod
    def passMethod():
        gameManager.passRound()


# everything with index 1 refers to player, with index 2 refers to opponent
class GameManager:
    captions1 = [
        "Your melee row",
        "Your ranged row",
        "Your siege row"
    ]
    captions2 = [
        "Opponent's melee row",
        "Opponent's ranged row",
        "Opponent's siege row"
    ]

    def __init__(self, gameName, gameIcon):
        self.root = tk.Tk()
        self.root.title(gameName)
        self.root.iconphoto(True, tk.PhotoImage(file=gameIcon))

        self.playerInterface1 = PlayerInterface(self.root, player1)
        self.playerInterface2 = PlayerInterface(self.root, player2)
        self.playerInterface2.place(1, 1)
        self.playerInterface1.place(8, 1)

        self.rowsInterface1 = RowsInterface(self.root, player1, self.captions1)
        self.rowsInterface2 = RowsInterface(self.root, player2, self.captions2)
        self.rowsInterface2.place(2, 1, inverse=True)
        self.rowsInterface1.place(5, 1)

        self.unitsInterface = ButtonsInterface(self.root, player1,
                                               self.playerInterface1,
                                               self.rowsInterface1)
        self.unitsInterface.place(9, 1)
        self.opponentPassed = False

    def switchTurns(self):
        if self.opponentPassed:
            self.endRound()
        else:
            self.opponentTurn()

    def opponentTurn(self, lastTurn=False):
        unit = player2.chooseUnit(player1, lastTurn)
        if unit != 0:
            unit.play()
            self.playerInterface2.update()
            self.rowsInterface2.update(unit.rowType)
        elif not lastTurn:
            self.opponentPassed = True
            text = "{} passed, the next turn will be your last!"
            text = text.format(player2.name)
            messagebox.showinfo(title="Opponent passed", message=text)

    def passRound(self):
        if not self.opponentPassed:
            self.opponentTurn(lastTurn=True)
        self.endRound()

    def endRound(self):
        sum1 = player1.getSum()
        sum2 = player2.getSum()

        textSource = open("txt/message.txt", "r")
        lines = list()
        for i in range(mechanics.messageLength):
            line = textSource.readline()
            lines.append(line)
        textSource.close()

        if self.opponentPassed:
            lines[0] = lines[0].format(player2.name, player1.name)
        else:
            lines[0] = lines[0].format(player1.name, player2.name)
        self.opponentPassed = False

        gameEnded = False
        if sum1 > sum2:
            action = "won"
            player1.roundsWon += 1
            if player1.roundsWon == mechanics.roundWinCondition:
                gameEnded = True
        elif sum1 == sum2:
            action = "tied"
        else:
            action = "lost"
            player2.roundsWon += 1
            if player2.roundsWon == mechanics.roundWinCondition:
                gameEnded = True
        lines[1] = lines[1].format(sum1, sum2, action)

        if gameEnded:
            lines[2] = lines[2].format(action)
            message = lines[0] + lines[1] + lines[2] + lines[3]
            if messagebox.askyesno(title="Game ended", message=message):
                self.newGame()
            else:
                quit()
        else:
            message = lines[0] + lines[1] + lines[3]
            if messagebox.askyesno(title="Round ended", message=message):
                self.newRound()
            else:
                quit()

    def clearBoard(self):
        self.playerInterface1.update()
        self.playerInterface2.update()
        player1.clearRows()
        player2.clearRows()
        for i in range(mechanics.rows):
            self.rowsInterface1.update(i)
            self.rowsInterface2.update(i)

    def newRound(self):
        player1.drawCard()
        player2.drawCard()
        self.clearBoard()
        self.unitsInterface.update()

    def newGame(self):
        player1.refresh()
        player2.refresh()
        self.clearBoard()
        for button in self.unitsInterface.handButtons:
            button.destroy()
        self.unitsInterface.handButtons = list()
        self.unitsInterface.update()


player1 = mechanics.Player("You")
player2 = mechanics.AI("Geralt of Rivia", 1)
gameManager = GameManager("Gwent", "img/geralt_32.png")
gameManager.root.mainloop()
