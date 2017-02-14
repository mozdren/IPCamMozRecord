import Configuration
import WebInterface
import Recorder
import Downloader
import Decorator
import OldRemover

if __name__ == "__main__":
    configuration = Configuration.Configuration("config.xml")
    webinterface = WebInterface.WebInterface(configuration)
    recorder = Recorder.Recorder(configuration)
    downloader = Downloader.Downloader(configuration)
    decorator = Decorator.Decorator(configuration)
    oldremover = OldRemover.OldRemover(configuration)
    webinterface.start()
    oldremover.start()
    try:
        while True:
            downloader.download()
            decorator.decorate(comunicator.get_data().lines)
            recorder.next_frame()
    except KeyboardInterrupt:
        webinterface.shutdown()
        oldremover.shutdown()
    
