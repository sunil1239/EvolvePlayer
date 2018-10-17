from PySide import QtGui, QtUiTools, QtCore
from ui.controls import *
from ui.dailogs.ErrorDialog import ErrorDialog as _ErrorDialog
from images import *
from core.CommandParams import CommandParams
from core.SongThread import SongThread
from ui.controls.ProgressBar import Widget
from ui.controls.SongList import SongList
from ui import *
from pygame import mixer_music as _mixer
from pygame import mixer
from lib.data import *
from core.GetSongList import GetSongList as _GetSongList
from core.songData.SongDetails import SongDetails

class NoSongsException():
    def __init__(self, err):
        print err

class MainController(QtGui.QWidget):
    def __init__(self, imgPath, parent=None):
        super(MainController, self).__init__(parent)
        self.setParent(parent)

        self.playFlag = True
        self.currentSong = ""#"crazyFeeling.mp3"

        loader = QtUiTools.QUiLoader()
        _file = QtCore.QFile(os.path.join(getControlsPath(),"controlUi.ui"))
        _file.open(QtCore.QFile.ReadOnly)
        self.musicCtrl = loader.load(_file, self)
        _file.close()
        ctrlWidth = self.musicCtrl.frameGeometry().width()+50
        ctrlHeight = self.musicCtrl.frameGeometry().height()+700
        maxCtrlSize = QtCore.QSize(ctrlWidth, ctrlHeight)
        self.setMaximumSize(maxCtrlSize)
        # self.setMinimumSize(minCtrlSize)

        self.playImg = QtGui.QPixmap(os.path.join(imgPath, "play.png"))
        self.pauseImg = QtGui.QPixmap(os.path.join(imgPath, "pause.png"))
        stopImg = QtGui.QPixmap(os.path.join(imgPath, "stop.png"))
        prevImg = QtGui.QPixmap(os.path.join(imgPath, "previous.png"))
        nextImg = QtGui.QPixmap(os.path.join(imgPath, "next.png"))
        repImg = QtGui.QPixmap(os.path.join(imgPath, "repeat.png"))

        self.musicCtrl.playBtn.setIcon(self.playImg)
        self.musicCtrl.stopBtn.setIcon(stopImg)
        self.musicCtrl.nextBtn.setIcon(repImg)
        self.musicCtrl.prevBtn.setIcon(prevImg)
        self.musicCtrl.repeatBtn.setIcon(nextImg)

        self.createPauseBtn()

        self.progressBar = Widget()
        self.setSongImage(path=imgPath)

        self.listSongsTable = SongList()

        outerLayout = QtGui.QGridLayout()
        outerLayout.addWidget(self.progressBar, 0, 1, 1, 1)
        outerLayout.addWidget(self.musicCtrl, 1, 0, 1, 3)
        outerLayout.addWidget(self.listSongsTable, 2, 0, 1, 3)
        self.setLayout(outerLayout)
        self.musicCtrl.playBtn.setShortcut("Space")
        self.musicCtrl.nextBtn.setShortcut("N")
        self.musicCtrl.prevBtn.setShortcut("B")
        self.listSongsTable.songTable.doubleClicked.connect(self.getCurrentSong)

        self.musicCtrl.playBtn.clicked.connect(self.playTheSong)
        self.pauseBtn.clicked.connect(self.togglePlayPause)
        self.contBtn.clicked.connect(self.togglePlayPause)
        self.playSong = None
        self.musicCtrl.stopBtn.clicked.connect(self.stopSong)
        self.setSongToPlay()

    def setSongImage(self, path=None, imageName="logoIcon.png"):
        if path:
            self.progressBar.roundProgress.setSongImg(path, imageName)
        else:
            self.progressBar.roundProgress.setSongImg(getImgPath(), imageName)

    def getCurrentSong(self, id):
        file = self.listSongsTable.songModal.index(id.row(), 0).data()+".mp3"
        self.currentSong = file
        getSongData = SongDetails(file)
        imagePath = getSongData.imageDisplay()
        if imagePath:
            self.setSongImage(os.path.dirname(imagePath), os.path.basename(imagePath))
        else:
            self.setSongImage()
        self.stopSong(NextSong=file)

    def setSongToPlay(self, songName=None):
        if songName:
            testSong = _GetSongList().getSelectedSong(songName)
        else:
            if not self.currentSong:
                print "Working"
                try:
                    self.currentSong = _GetSongList().updateSongs()[0]
                except Exception as e:
                    noSongError = _ErrorDialog(message="Unable to load the songs/nPlease add songs to the library", title="Unable to load the song")
            testSong = _GetSongList().getSelectedSong(self.currentSong)

        mixer.init()
        _mixer.load(testSong)
        from core.songData.SongDetails import SongDetails
        self.playBackSong = SongDetails(testSong).getSongLength()

    def createPauseBtn(self):
        self.pauseBtn = QtGui.QPushButton(self.musicCtrl)
        self.pauseBtn.setObjectName("pauseBtn")
        self.pauseBtn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.pauseBtn.setMaximumSize(100, 100)
        self.pauseBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pauseBtn.setStyleSheet("max-height:100px;max-width:100px;border-radius:49px;")
        self.pauseBtn.setIcon(self.pauseImg)
        self.pauseBtn.setIconSize(QtCore.QSize(100, 100))

        self.createContinueBtn()

        self.musicCtrl.gridLayout.addWidget(self.pauseBtn, 0, 2, 2, 1)
        self.musicCtrl.gridLayout.addWidget(self.contBtn, 0, 2, 2, 1)
        self.pauseBtn.setVisible(False)
        self.pauseBtn.setEnabled(False)
        self.contBtn.setVisible(False)
        self.contBtn.setEnabled(False)
        self.pauseBtn.setShortcut("Space")

    def createContinueBtn(self):
        self.contBtn = QtGui.QPushButton(self.musicCtrl)
        self.contBtn.setObjectName("contBtn")
        self.contBtn.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.contBtn.setMaximumSize(100, 100)
        self.contBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.contBtn.setStyleSheet("max-height:100px;max-width:100px;border-radius:49px;")
        self.contBtn.setIcon(self.playImg)
        self.contBtn.setIconSize(QtCore.QSize(100, 100))
        self.contBtn.setShortcut("Space")

    def playTheSong(self, *args):
        self.musicCtrl.playBtn.setVisible(False)
        self.musicCtrl.playBtn.setEnabled(False)
        self.pauseBtn.setVisible(True)
        self.pauseBtn.setEnabled(True)
        self.playSong = SongThread(self.progressBar.roundProgress.value(), self.playBackSong)
        self.playSong.start()
        self.playSong.dePauseTimeline()
        self.playSong.runTime.connect(self.updateTimeline)
        print "Entered play"
        _mixer.play()


    def togglePlayPause(self, *args):

        if self.pauseBtn.isVisible():
            self.pauseBtn.setVisible(False)
            self.pauseBtn.setEnabled(False)
            self.contBtn.setVisible(True)
            self.contBtn.setEnabled(True)
            self.playSong.pauseTimeline()
            # self.playSong.runTime.connect(self.updateTimeline)
            print "Entered Pause"
            _mixer.pause()

        elif self.contBtn.isVisible():
            self.contBtn.setVisible(False)
            self.contBtn.setEnabled(False)
            self.pauseBtn.setVisible(True)
            self.pauseBtn.setEnabled(True)
            self.playSong.dePauseTimeline()
            # self.playSong.runTime.connect(self.updateTimeline)
            print "Entered Playing"
            _mixer.unpause()

    def stopSong(self, NextSong=None, *args):
        if self.playSong != None:
            self.playSong.interPretSong()
            self.playSong.exit()
            self.playSong.wait()
            self.progressBar.roundProgress.setValue(0)

        self.musicCtrl.playBtn.setEnabled(True)
        self.musicCtrl.playBtn.setVisible(True)
        self.pauseBtn.setEnabled(False)
        self.pauseBtn.setVisible(False)
        self.contBtn.setEnabled(False)
        self.contBtn.setVisible(False)
        self.progressBar.roundProgress.setValue(0)
        mixer.quit()
        if NextSong:
            self.setSongToPlay(NextSong)
        else:
            self.setSongToPlay()

    def updateTimeline(self, value):
        self.progressBar.roundProgress.setValue(value)
        if value == 100:
            self.playSong.exit()
            self.playSong = None
            self.stopSong()


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    gui = MainController(getImgPath())
    gui.show()
    sys.exit(app.exec_())
