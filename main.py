import tkinter as tk
import tkinter.messagebox as messagebox
import mechanics
import random as rand


# everything with index 1 refers to player, with index 2 refers to opponent
class GameWidgets:
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

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gwent")
        self.root.iconphoto(True, tk.PhotoImage(file="img/geralt_32.png"))

        self.state1 = tk.StringVar()
        self.state1.set(player1.getLabel())
        self.playerLabel1 = tk.Label(self.root, width=60,
                                     textvariable=self.state1)

        self.state2 = tk.StringVar()
        self.state2.set(player2.getLabel())
        self.playerLabel2 = tk.Label(self.root, width=60,
                                     textvariable=self.state2)

        self.board = [[] for i in range(6)]
        for x in range(3):
            self.board[x].append(
                tk.Label(self.root, anchor=tk.E, width=20, relief=tk.RIDGE,
                         text=self.captions2[2 - x])
            )
        for x in range(3):
            self.board[3 + x].append(
                tk.Label(self.root, anchor=tk.E, width=20, relief=tk.RIDGE,
                         text=self.captions1[x])
            )

        self.rows1 = list()
        self.rowSums1 = list()
        for i in range(3):
            self.rows1.append(tk.StringVar())
            self.rows1[i].set("-")
            self.rowSums1.append(tk.StringVar())
            self.rowSums1[i].set("0")
        for i in range(3):
            self.board[3 + i].append(
                tk.Label(self.root, width=3, relief=tk.RIDGE,
                         textvariable=self.rowSums1[i])
            )
            self.board[3 + i].append(
                tk.Label(self.root, width=35, anchor=tk.W, relief=tk.RIDGE,
                         textvariable=self.rows1[i])
            )

        self.rows2 = list()
        self.rowSums2 = list()
        for i in range(3):
            self.rows2.append(tk.StringVar())
            self.rows2[i].set("-")
            self.rowSums2.append(tk.StringVar())
            self.rowSums2[i].set("0")
        for i in range(3):
            self.board[i].append(
                tk.Label(self.root, width=3, relief=tk.RIDGE,
                         textvariable=self.rowSums2[2 - i])
            )
            self.board[i].append(
                tk.Label(self.root, width=35, anchor=tk.W, relief=tk.RIDGE,
                         textvariable=self.rows2[2 - i])
            )

        self.playerLabel2.grid(row=1, column=1, columnspan=3)
        for i in range(6):
            self.board[i][0].grid(row=i + 2, column=1)
            self.board[i][1].grid(row=i + 2, column=2)
            self.board[i][2].grid(row=i + 2, column=3)
        self.playerLabel1.grid(row=8, column=1, columnspan=3)

        self.handFrame = tk.Frame(self.root)
        self.handFrame.grid(row=9, column=1, columnspan=3)
        self.handButtons = list()
        self.generateUnitButtons()

        self.opponentPassed = False
        method = self.passRound
        passButton = tk.Button(self.handFrame, text="Pass", command=method)
        passButton.pack(side=tk.BOTTOM)

    def generateUnitButtons(self):
        for i in range(mechanics.handSize):
            unit = player1.units[i]
            row = player1.rows[unit.rowType]
            label = unit.getButtonLabel()
            method = self.createMethod(i, unit, row)
            button = tk.Button(self.handFrame, text=label, command=method)
            self.handButtons.append(button)
            button.pack(side=tk.TOP)

    def createMethod(self, i, unit, row):
        def buttonMethod():
            self.handButtons[i].destroy()
            unit.play(row)
            self.updateState()
            self.updateRow(row)
            if self.opponentPassed:
                self.endRound()
            else:
                self.opponentTurn()
        return buttonMethod

    def updateState(self, opponent=False):
        if opponent:
            self.state2.set(player2.getLabel())
        else:
            self.state1.set(player1.getLabel())

    def updateRow(self, row, opponent=False):
        if opponent:
            self.rows2[row.rowType].set(row.getLabel())
            self.rowSums2[row.rowType].set(str(row.sum))
        else:
            self.rows1[row.rowType].set(row.getLabel())
            self.rowSums1[row.rowType].set(str(row.sum))

    def opponentTurn(self):
        passCode = mechanics.handSize * 3 // 4
        passChance = rand.randint(0, passCode)
        if passChance == passCode:
            self.opponentPassed = True
            text = "{} passed, the next turn will be your last!"
            text = text.format(player2.name)
            messagebox.showinfo(title="Opponent passed", message=text)
        else:
            unit = player2.chooseUnit()
            if unit != 0:
                row = player2.rows[unit.rowType]
                unit.play(row)
                self.updateState(opponent=True)
                self.updateRow(row, opponent=True)

    def passRound(self):
        if not self.opponentPassed:
            self.opponentTurn()
        self.endRound()

    def endRound(self):
        sum1 = 0
        sum2 = 0
        for i in range(3):
            sum1 += player1.rows[i].sum
            sum2 += player2.rows[i].sum

        textSource = open("txt/message.txt", "r")
        line1 = textSource.readline()
        line2 = textSource.readline()
        textSource.close()

        if self.opponentPassed:
            line1 = line1.format(player2.name, player1.name)
        else:
            line1 = line1.format(player1.name, player2.name)
        self.opponentPassed = False

        if sum1 > sum2:
            action = "won"
            player1.roundsWon += 1
        elif sum1 == sum2:
            action = "tied"
        else:
            action = "lost"
            player2.roundsWon += 1
        line2 = line2.format(sum1, sum2, action)

        if messagebox.askyesno(title="Round ended", message=line1 + line2):
            self.refreshBoard()
        else:
            quit()

    def refreshBoard(self):
        player1.refresh()
        player2.refresh()
        self.updateState()
        self.updateState(opponent=True)
        for i in range(mechanics.rows):
            self.updateRow(player1.rows[i])
            self.updateRow(player2.rows[i], opponent=True)
        for button in self.handButtons:
            button.destroy()
        self.handButtons = list()
        self.generateUnitButtons()


player1 = mechanics.Player("You")
player2 = mechanics.Player("Geralt of Rivia")
gameWidgets = GameWidgets()
gameWidgets.root.mainloop()
