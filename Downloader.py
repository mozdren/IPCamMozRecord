import urllib2
import threading
import Configuration
import cv

def download(url):
    try:
        response = urllib2.urlopen(url, timeout = 5)
        data = response.read()
        return data
    except Exception, e:
        print str(e)
        return None

class DownloaderThread(threading.Thread):
    def __init__(self, camera, width, height):
        threading.Thread.__init__(self)
        self.url = camera.source
        self.filename = camera.name + ".jpg"
        self.width = width
        self.height = height
    def run(self):
        is_ok = False
        with open(self.filename , "w") as myfile:
            data = download(self.url)
            if data != None:
                myfile.write(data)
                is_ok = True
        if is_ok:
            image = cv.LoadImage(self.filename)
            image_out = cv.CreateImage((self.width,self.height), cv.IPL_DEPTH_8U, 3)
            cv.Resize(image, image_out)
            cv.SaveImage(self.filename, image_out)
        else:
            image_out = cv.CreateImage((self.width, self.height), cv.IPL_DEPTH_8U, 3)
            cv.Set(image_out, (0,0,0))
            cv.SaveImage(self.filename, image_out)

class Downloader(object):
    def __init__(self, configuration):
        self.cameras = configuration.data["cameras"]
        self.width = configuration.data["width"]
        self.height = configuration.data["height"]
    def download(self):
        threads = []
        for cam in self.cameras:
            threads.append(DownloaderThread(cam, self.width, self.height))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
if __name__ == "__main__":
    configuration = Configuration.Configuration("config.xml")
    print configuration
    downloader = Downloader(configuration)
    downloader.download()

