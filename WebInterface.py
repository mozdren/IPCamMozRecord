from SocketServer import ThreadingMixIn
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import time
import threading
import Configuration
import os
import datetime

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    
webconfiguration = None
webheader = None
webfooter = None

def freespace():
    global webconfiguration
    disk = os.statvfs(webconfiguration.data["storage_path"])
    return float(disk.f_bsize * disk.f_bavail / 1024 / 1024) / 1024.0

def get_links():
    toreturn = "<table><thead><th>Additional Links</th></thead>"
    toreturn += '<tr><td><a href="/videofiles">Video Files</td></tr>'
    toreturn += '<tr><td><a href="http://www.mozdren.eu/">mozdren.eu</td></tr>'
    toreturn += '</table>'
    return toreturn

def get_server_info_table():
    global webconfiguration
    toreturn = "<table><thead><th>Server Information</th><th></th></thead>"
    toreturn += '<tr><td align="right">System Name:</td><td>{0}</td></tr>'.format(webconfiguration.data["name"])
    toreturn += '<tr><td align="right">Video Resolution:</td><td>{0}x{1}</td></tr>'.format(webconfiguration.data["width"], webconfiguration.data["height"])
    toreturn += '<tr><td align="right">Minimal Free Disk Space:</td><td>{0} GB</td></tr>'.format(webconfiguration.data["minfreespace"])
    toreturn += '<tr><td align="right">Free Disk Space:</td><td>{0:.2f} GB</td></tr>'.format(freespace())
    toreturn += '<tr><td align="right">Web Interface Port:</td><td>{0}</td></tr>'.format(webconfiguration.data["webport"])
    toreturn += '<tr><td align="right">Communication Port:</td><td>{0}</td></tr>'.format(webconfiguration.data["comport"])
    toreturn += '<tr><td align="right">System Time:</td><td>{0}</td></tr>'.format(datetime.datetime.now())
    toreturn += '</table>'
    return toreturn

def get_web_header(title):
    global webheader
    if webheader != None:
        return webheader.format(title)
    try:
        with open("static/header.html") as headerfile:
            webheader = headerfile.read()
            return webheader.format(title)
    except Exception as e:
        print "Header file problem: " + str(e)
        webheader = "<html><head><title>{0}</title></head><body><h1>{0}</h1>"
        return webheader.format(title)

def get_web_footer():
    global webfooter
    if webfooter != None:
        return webfooter.format(datetime.datetime.now())
    try:
        with open("static/footer.html") as footerfile:
            webfooter = footerfile.read()
            return webfooter.format(datetime.datetime.now())
    except Exception as e:
        print "Header file problem: " + str(e)
        webfooter = "<br /><br />Generated: {0} - (c) mozdren.eu, 2017</body></html>"
        return webfooter.format(datetime.datetime.now())

def is_camera(handler):
    global webconfiguration
    cameras = webconfiguration.data["cameras"]
    for camera in cameras:
        if handler.path.endswith("/"+camera.name):
            return True
    return False

def send_camera_image(handler):
    split_path = handler.path.split("/")
    camera_name = split_path[len(split_path)-1]
    try:
        with open(camera_name+"_web.jpg") as imagefile:
            data = imagefile.read()
            handler.send_response(200)
            handler.send_header("Content-type","image/jpeg")
            handler.end_headers()
            handler.wfile.write(data)
            return
    except Exception as e:
        print "Error:" + str(e)
        handler.send_error(404, "Data does not exist!")
        return

def is_list_videofiles(handler):
    if handler.path.endswith("videofiles") or handler.path.endswith("videofiles/"):
        return True
    return False

def is_static(handler):
    if handler.path.find("..") != -1:
        return False
    if handler.path.startswith("//"):
        return False
    if handler.path.find("/static/") != -1:
        return True
    return False

def get_mime_type(path):
    if path.endswith(".ico"):
        return "image/x-icon"
    if path.endswith(".jpg"):
        return "image/jpeg"
    if path.endswith(".avi"):
        return "video/mpeg"
    if path.endswith(".html"):
        return "text/html"
    if path.endswith(".xml"):
        return "text/xml"
    if path.endswith(".txt"):
        return "text/plain"
    if path.endswith(".css"):
        return "text/css"
    if path.endswith(".gif"):
        return "image/gif"
    if path.endswith(".png"):
        return "image/png"
    if path.endswith(".svg"):
        return "image/svg+xml"
    if path.endswith(".tiff"):
        return "image/tiff"
    if path.endswith(".pdf"):
        return "application/pdf"
    return "application/octet-stream"

def send_static(handler):
    try:
        with open(handler.path[1:]) as staticfile:
            data = staticfile.read()
            handler.send_response(200)
            handler.send_header("Content-type",get_mime_type(handler.path))
            handler.end_headers()
            handler.wfile.write(data)
            return
    except Exception as e:
        print "Error:" + str(e)
        handler.send_error(404, "File does not exist!")
        return

def send_videofiles_list_page(handler):
    global webconfiguration
    toreturn = ""
    toreturn += get_web_header("Video Files")
    try:
        files = os.listdir(webconfiguration.data["storage_path"])
        files.sort()
        toreturn += "<table><thead><th>Video Filename</th></thead>"
        for filename in files:
            if filename.endswith(".avi"):
                toreturn += '<tr><td><a href="{0}">{1}</a></td></tr>'.format("videofiles/"+filename, filename)
        toreturn += "</table>"
    except Exception as e:
        print "Error listing video files: " + str(e)
        handler.send_error(404, "Error: listing files!")
        return
    toreturn += get_web_footer()
    handler.send_response(200)
    handler.send_header("Content-type","text/html")
    handler.end_headers()
    handler.wfile.write(toreturn)
    return

def is_videofile(handler):
    if handler.path.find("videofiles/") != -1 and handler.path.endswith(".avi"):
        return True
    return False

def send_videofile(handler):
    global webconfiguration
    path_split = handler.path.split("/")
    video_filename = webconfiguration.data["storage_path"] + path_split[len(path_split)-1]
    try:
        with open(video_filename) as videofile:
            data = videofile.read()
            handler.send_response(200)
            handler.send_header("Content-type","video/mpeg")
            handler.end_headers()
            handler.wfile.write(data)
            return
    except Exception as e:
        print "Can not find videofile: " + str(e)
        handler.send_error(404, "Error: videofile does not exist!")
        return

def is_icon(handler):
    if handler.path.endswith("/favicon.ico"):
        return True
    return False
    
def send_icon(handler):
    try:
        with open("static/favicon.ico") as iconfile:
            data = iconfile.read()
            handler.send_response(200)
            handler.send_header("Content-type","image/x-icon")
            handler.end_headers()
            handler.wfile.write(data)
            return
    except Exception as e:
        print "Can not find videofile: " + str(e)
        handler.send_error(404, "Error: No icon found!")
        return

def is_index(handler):
    if handler.path.endswith("/") or handler.path.endswith("/index.html"):
        return True
    return False

def get_cameras_table():
    global webconfiguration
    toreturn = "<table><thead><th>Configured Cameras</th></thead>"
    cameras = webconfiguration.data["cameras"]
    for cam in cameras:
        toreturn += '<tr><td><a href="/{0}">{1}</a></td></tr>'.format(cam.name, cam.fullname)
    toreturn += "</table>"
    return toreturn

def send_index(handler):
    global webconfiguration
    global webconfiguration
    toreturn = ""
    toreturn += get_web_header("Home Page")
    try:
        toreturn += get_cameras_table()
        toreturn += get_links()
        toreturn += get_server_info_table()
    except Exception as e:
        print "Error listing video files: " + str(e)
        handler.send_error(404, "Error: listing files!")
        return
    toreturn += get_web_footer()
    handler.send_response(200)
    handler.send_header("Content-type","text/html")
    handler.send_header("Refresh","10")
    handler.end_headers()
    handler.wfile.write(toreturn)
    return

class WebInterfaceHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if is_camera(self): # image
            send_camera_image(self)
            return
        if is_list_videofiles(self): # list of video files
            send_videofiles_list_page(self)
            return
        if is_videofile(self): # video file
            send_videofile(self)
            return
        if is_icon(self):
            send_icon(self)
            return
        if is_static(self):
            send_static(self)
            return
        if is_index(self):
            send_index(self)
            return
        else:
            self.send_error(404, "File does not exist!")
            return

class WebInterface(threading.Thread):
    def __init__(self, configuration):
        threading.Thread.__init__(self)
        global webconfiguration
        webconfiguration = configuration
        self.configuration = configuration
        self.port = configuration.data["webport"]
        self.httpServer = ThreadedHTTPServer(('', self.port), WebInterfaceHandler)
        
    def run(self):
        print "Web Interface Initialized"
        self.httpServer.serve_forever()
    
    def shutdown(self):
        print "Web Interface Shutting down"
        self.httpServer.shutdown()

if __name__ == "__main__":
    configuration = Configuration.Configuration("config.xml")
    webinterface = WebInterface(configuration)
    webinterface.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        webinterface.shutdown()
    
