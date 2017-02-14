import xml.etree.ElementTree as ET

class Camera(object):
    def __init__(self, name, fullname, source):
        self.name = name
        self.fullname = fullname
        self.source = source
        self.data = None
    def __str__(self):
        return "{0} - {1}".format(self.name, self.source)
        
def load_cameras(filename):
    try:
        cameras = []
        tree = ET.parse(filename)
        for ce in tree.findall("cameras/camera"):
            name = ce.find("name").text
            fullname = ce.find("fullname").text
            source = ce.find("source").text
            c = Camera(name, fullname, source)
            cameras.append(c)
        return cameras
    except Exception as e:
        print "ERR: Config file error: " + str(e)
        return None

if __name__ == "__main__":
    cams = load_cameras("config.xml")
    if cams != None:
        for c in cams:
            print c
    else:
        print str(cams)

