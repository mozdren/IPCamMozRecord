import cv
import datetime
import Configuration
import Downloader
import threading

class DecoratorThread(threading.Thread):
    def __init__(self, configuration, camera, infolist, font, font_back):
        threading.Thread.__init__(self)
        self.configuration = configuration
        self.camera = camera
        self.infolist = infolist
        self.font = font
        self.font_back = font_back
        self.filename = camera.name + ".jpg"
        self.webfilename = camera.name+"_web.jpg"
    def run(self):
        image = cv.LoadImage(self.filename)
        dt = datetime.datetime.now()
        irows = []
        irows.append("System: {0}, Camera: {1}, Time: {2}".format(self.configuration.data["name"], self.camera.name, dt))
        irows += self.infolist
        posy = 20
        for r in irows:
            cv.PutText(image, r, (20,posy), self.font_back, (0,0,0))
            cv.PutText(image, r, (20,posy), self.font, (255,255,255))
            posy += 20
        cv.SaveImage(self.filename, image);
        cv.SaveImage(self.webfilename, image);
        
class Decorator(object):
    def __init__(self, configuration):
        self.configuration = configuration
        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1, 1, 0, 1, 8) 
        self.font_back = cv.InitFont(cv.CV_FONT_HERSHEY_PLAIN, 1, 1, 0, 6, 8)
    def decorate(self, infolist = []):
        threads = []
        cameras = self.configuration.data["cameras"]
        for camera in cameras:
            threads.append(DecoratorThread(self.configuration, camera, infolist, self.font, self.font_back))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

if __name__ == "__main__":
    configuration = Configuration.Configuration("config.xml")
    downloader = Downloader.Downloader(configuration)
    decorator = Decorator(configuration)
    downloader.download()
    decorator.decorate(["Ahoj,", "Svete!"])

