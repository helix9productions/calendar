import sys, os, datetime
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.topLevelFilePath = os.path.dirname(__file__)
        with open(self.topLevelFilePath + '/UI/stylesheet.qss', 'r', encoding='utf-8') as file:
            style = file.read()
        self.setStyleSheet(style)
        self.setWindowTitle("Calendar")
        self.resize(960,720)
        self.page = 0

        with open(self.topLevelFilePath + '/data/master.txt', 'r', encoding='utf-8') as file:
            data = file.read()
        self.contents = data.split('\n')
        self.contents.remove('')
        
        # base
        self.mainWidget = QWidget()
        self.primaryWidget = QWidget(self.mainWidget)
        self.secondaryWidget = QWidget(self.mainWidget)
        self.middleWidget = QWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.primaryWidget)
        self.mainLayout.addWidget(self.middleWidget)
        self.mainLayout.addWidget(self.secondaryWidget)

        # top middle and bottom layouts
        self.layoutNorth = QHBoxLayout(self.primaryWidget)
        self.layoutMiddle = QHBoxLayout(self.middleWidget)
        self.layoutSouth = QGridLayout(self.secondaryWidget)
        self.createHeader()
        self.createWeekdays()
        self.createDates()          

        self.setCentralWidget(self.mainWidget)
        self.saveContent()
        self._createActions()
        #self._connectActions()

    def _createActions(self):
        self.leftArrow.clicked.connect(self.forwardPage)
        self.rightArrow.clicked.connect(self.backPage)

        self.saveTimer = QTimer(self)
        self.saveTimer.setInterval(2000)
        self.saveTimer.timeout.connect(self.saveContent)
        self.saveTimer.start()

    def createHeader(self):
        self.layoutNorth.setContentsMargins(10, 10, 10, 10)
        self.now = datetime.datetime.now()
        self.monthLabel = QLabel(self.now.strftime("%Y") + " - Week " + self.now.strftime("%W"), self.primaryWidget)
        self.monthLabel.setObjectName("Title")
        self.leftArrow = QPushButton("<", self.primaryWidget)
        self.rightArrow = QPushButton(">", self.primaryWidget)
        self.layoutNorth.addWidget(self.monthLabel)
        self.layoutNorth.addWidget(self.leftArrow)
        self.layoutNorth.addWidget(self.rightArrow)

    def createWeekdays(self):
        self.layoutMiddle.setContentsMargins(0, 0, 0, 0)
        self.layoutMiddle.setSpacing(0)
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for x in weekdays:
            weekLabel = QLabel(x, self.middleWidget)
            weekLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layoutMiddle.addWidget(weekLabel)

    def createDates(self):
        self.layoutSouth.setContentsMargins(1,1,1,1)
        self.layoutSouth.setSpacing(1)
        startingDate = self.now - datetime.timedelta(days=self.now.weekday())
        for i in range(7):
            for j in range(4):
                body = QWidget()
                date = startingDate + datetime.timedelta(days=(i+7*j))
                dateLabel = QLabel(date.strftime("%b-%d"), body)
                dateLabel.setProperty("dateLabel", True)
                content = QTextEdit("", body)
                content.setPlaceholderText("Type...")
                content.textChanged.connect(self.placeHolderCheck)
                memIndex = -1
                for x in range(len(self.contents)):
                    if(self.contents[x].split(':')[0] == date.strftime("%d-%m-%Y")):
                        memIndex = x
                    if(memIndex != -1):
                        content.setText(':'.join(self.contents[memIndex].split(':')[1:]))
                    else:
                        content.setText("")
                if date == self.now:
                    dateLabel.setProperty("today", True)
                    content.setProperty("today", True)
                elif date < self.now:
                    dateLabel.setProperty("past", True)
                    content.setProperty("past", True)
                bodylayout = QVBoxLayout(body)
                bodylayout.setContentsMargins(0, 0, 0, 0)
                bodylayout.setSpacing(0)
                bodylayout.addWidget(dateLabel)
                bodylayout.addWidget(content)
                self.layoutSouth.addWidget(body, j, i)

    def changeDates(self):
        startingDate = self.now - datetime.timedelta(days=self.now.weekday()+self.page*7)
        if isinstance(self.layoutNorth.itemAt(0).widget(), QLabel):
            self.layoutNorth.itemAt(0).widget().setText(startingDate.strftime("%Y") + " - Week " + startingDate.strftime("%W"))
        for i in range(7):
            for j in range(4):
                widget = self.layoutSouth.itemAtPosition(j, i).widget()

                date = startingDate + datetime.timedelta(days=(i+7*j))

                dateLabel = widget.layout().itemAt(0).widget()
                content = widget.layout().itemAt(1).widget()

                if isinstance(dateLabel, QLabel):
                    dateLabel.setText(date.strftime("%b-%d"))
                if isinstance(content, QTextEdit):
                    content.clearFocus()
                    memIndex = -1
                    for x in range(len(self.contents)):
                        if(self.contents[x].split(':')[0] == date.strftime("%d-%m-%Y")):
                            memIndex = x
                    if(memIndex != -1):
                        content.setText(':'.join(self.contents[memIndex].split(':')[1:]))
                    else:
                        content.setText("")

                dateLabel.setProperty("today", False)
                content.setProperty("today", False)
                dateLabel.setProperty("past", False)
                content.setProperty("past", False)

                if date == self.now:
                    dateLabel.setProperty("today", True)
                    content.setProperty("today", True)
                elif date < self.now:
                    dateLabel.setProperty("past", True)
                    content.setProperty("past", True)
                if content.toPlainText() == "":
                    content.setProperty("empty", True)
                else:
                    content.setProperty("empty", False)

                dateLabel.setStyleSheet(dateLabel.styleSheet())
                content.setStyleSheet(content.styleSheet())
            
    def saveContent(self):
        print("Saving...")
        file = open(self.topLevelFilePath + '/data/master.txt', 'w', encoding='utf-8')
        startingDate = self.now - datetime.timedelta(days=self.now.weekday()+self.page*7)
        for i in range(7):
            for j in range(4):
                widget = self.layoutSouth.itemAtPosition(j, i).widget()
                date = startingDate + datetime.timedelta(days=(i+7*j))
                content = widget.layout().itemAt(1).widget().toPlainText()
                memory = date.strftime("%d-%m-%Y:") + content
                memContains = True
                if(len(self.contents) > 0):
                    toRemove = []
                    for x in range(len(self.contents)):
                        if(self.contents[x].split(':')[0] == date.strftime("%d-%m-%Y") and ':'.join(self.contents[x].split(':')[1:]) != content):
                            toRemove.append(self.contents[x])
                        elif(self.contents[x].split(':')[0] != date.strftime("%d-%m-%Y")):
                            memContains = False
                        else:
                            toRemove.append(self.contents[x])
                            memContains = False
                            continue
                    for x in toRemove:
                        self.contents.remove(x)
                    if memContains == False and content != "":
                        self.contents.append(memory)
                elif content != "":
                    self.contents.append(memory)

        self.contents = [*set(self.contents)]
        a = ""
        for x in self.contents:
                a += x+'\n'
        file.write(a)
        file.close()
        print("Done saving.")
    
    def placeHolderCheck(self):
        content = QApplication.focusWidget()
        if isinstance(content, QTextEdit):
            if content.toPlainText() == "":
                content.setProperty("empty", True)
            else:
                content.setProperty("empty", False)
            content.setStyleSheet(content.styleSheet())

    def forwardPage(self):
        self.saveContent()
        self.page += 4
        self.changeDates()

    def backPage(self):
        self.saveContent()
        self.page -= 4
        self.changeDates()

    def wheelEvent(self, event: QWheelEvent):
        self.saveContent()
        self.page += event.angleDelta().y()//120
        self.changeDates()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
