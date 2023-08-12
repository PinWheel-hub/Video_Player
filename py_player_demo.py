from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from pynput import keyboard

from GUI import Ui_MainWindow
import sys, cv2


class myMainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('myVideoPlayer')

        self.sld_video_pressed = False  #判断当前进度条识别否被鼠标点击
        self.videoFullScreen = False   # 判断当前widget是否全屏
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.wgt_video)  # 视频播放输出的widget，就是上面定义的
        self.btn_open.clicked.connect(self.openVideoFile)   # 打开视频文件按钮
        self.btn_stop.clicked.connect(self.pauseVideo)       # pause
        self.btn_go.clicked.connect(self.goVideo)
        self.btn_back.clicked.connect(self.backVideo)

        self.player.positionChanged.connect(self.changeSlide)      # change Slide
        self.sld_video.setTracking(False)
        self.sld_video.sliderReleased.connect(self.releaseSlider)
        self.sld_video.sliderPressed.connect(self.pressSlider)
        self.sld_video.sliderMoved.connect(self.moveSlider)   # 进度条拖拽跳转
        self.sld_video.ClickedValue.connect(self.clickedSlider)  # 进度条点击跳转
        self.sld_audio.valueChanged.connect(self.volumeChange)  # 控制声音播放
        self.player.setVolume(100)
        self.videopath = ""
        self.listener = keyboard.Listener(on_release=self.on_release)
        self.listener.start()

    def volumeChange(self, position):
        volume = round(position/self.sld_audio.maximum()*100)
        self.player.setVolume(volume)
        self.lab_audio.setText("音量:"+str(volume)+"%")

    def clickedSlider(self, position):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            seconds = int((1 - position / self.vidoeLength) * self.player.duration() / 1000)
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            self.lab_video.setText(str(h).rjust(2, '0') + ":" + str(m).rjust(2, '0') + ":" + str(s).rjust(2, '0'))
        else:
            self.sld_video.setValue(0)

    def moveSlider(self, position):
        self.sld_video_pressed = True
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            seconds = int((1 - position / self.vidoeLength) * self.player.duration() / 1000)
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            self.lab_video.setText(str(h).rjust(2, '0') + ":" + str(m).rjust(2, '0') + ":" + str(s).rjust(2, '0'))

    def pressSlider(self):
        self.sld_video_pressed = True

    def releaseSlider(self):
        self.sld_video_pressed = False

    def changeSlide(self, position):
        if not self.sld_video_pressed:  # 进度条被鼠标点击时不更新
            self.vidoeLength = self.player.duration()+0.1
            self.sld_video.setValue(round((position/self.vidoeLength)*100))
            seconds = int((1-position/self.vidoeLength) * self.player.duration() / 1000)
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            self.lab_video.setText(str(h).rjust(2, '0') + ":" + str(m).rjust(2, '0') + ":" + str(s).rjust(2, '0'))

    def openVideoFile(self):
        videofile = QFileDialog.getOpenFileUrl()[0]
        if videofile.path() == '':
            pass
        else:
            capture = cv2.VideoCapture(videofile.path()[1:])
            ref, frame = capture.read()
            if not ref:
                QMessageBox.critical(self, "错误", "视频格式错误")
            else:
                self.player.setMedia(QMediaContent(videofile))  # 选取视频文件
                self.player.play()  # 播放视频
                self.player.pause()

    def pauseVideo(self):
        if self.player.state() != 2:
            self.player.pause()
        else:
            self.player.play()

    def goVideo(self):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            player_position = self.player.position()
            self.player.setPosition(min(player_position + 10000, self.player.duration()))



    def backVideo(self):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            player_position = self.player.position()
            self.player.setPosition(max(player_position - 10000, 0))
            if(player_position == self.player.duration()):
                self.player.play()

    def on_release(self, key):
        try:
            if key == keyboard.Key.f1:
                self.backVideo()
            if key == keyboard.Key.f2:
                self.goVideo()
            if key == keyboard.Key.f3:
                self.pauseVideo()

        except NameError:
            pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    vieo_gui = myMainWindow()
    vieo_gui.show()
    sys.exit(app.exec_())