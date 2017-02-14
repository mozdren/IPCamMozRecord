import cv
import threading
import datetime
import Configuration
import Downloader
import Decorator
import Comunicator

class RecorderThread(threading.Thread):
    def __init__(self, writer, camera):
        threading.Thread.__init__(self)
        self.writer = writer
        self.camera = camera
    def run(self):
        image = cv.LoadImage(self.camera.name+".jpg")
        cv.WriteFrame(self.writer, image)

class Recorder(object):
    def __init__(self, configuration):
        self.configuration = configuration
        self.writers = [] # [[writer, camera],....]
        self.fourcc = cv.CV_FOURCC('M',"P","4","2")
        self.fps = 25
        self.is_color = True
        self.start_time = datetime.datetime.now()
        self.is_recording = False
        self.video_len = self.configuration.data["video_len"]
        self.frame_size = (self.configuration.data["width"], self.configuration.data["height"])
        self.storage_path = self.configuration.data["storage_path"]
    def next_frame(self):
        if not self.is_recording: # Recording (first frame, or end of the video)
            self.writers = []
            self.start_time = datetime.datetime.now()
            for cam in self.configuration.data["cameras"]:
                filename = self.storage_path+"{0:04}{1:02}{2:02}T{3:02}{4:02}_{5}.avi".format(self.start_time.year, self.start_time.month, self.start_time.day, self.start_time.hour, self.start_time.minute, cam.name)
                self.writers.append([cv.CreateVideoWriter(filename, self.fourcc, self.fps, self.frame_size, self.is_color), cam])
            self.is_recording = True
        else:
            threads = []
            for wr_cam in self.writers:
                threads.append(RecorderThread(*wr_cam)) # * unpack data to constructor
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            # check if time threshold for one record was not met (stop it if so)
            ack_time = datetime.datetime.now()
            if abs(ack_time - self.start_time) > datetime.timedelta(minutes = self.video_len):
                self.is_recording = False

if __name__ == "__main__":
    configuration = Configuration.Configuration("config.xml")
    print configuration
    comunicator = Comunicator.Comunicator(configuration)
    dc = Comunicator.DataCarriage()
    dc.lines = ["Ahoj, ", "Svete!"]
    comunicator.set_data(dc)
    comunicator.start()
    downloader = Downloader.Downloader(configuration)
    decorator = Decorator.Decorator(configuration)
    recorder = Recorder(configuration)
    try:
        while True:
            downloader.download()
            decorator.decorate(comunicator.get_data().lines)
            recorder.next_frame()
    except KeyboardInterrupt:
        comunicator.shutdown()

