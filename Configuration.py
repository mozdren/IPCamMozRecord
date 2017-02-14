import Camera

class Configuration(object):
    def __init__(self, filename):
        import xml.etree.ElementTree as ET
        configxml = ET.parse(filename)
        self.data = {}
        self.data["name"] = configxml.find("name").text
        self.data["video_len"] = int(configxml.find("video/length").text)
        self.data["width"] = int(configxml.find("video/width").text)
        self.data["height"] = int(configxml.find("video/height").text)
        self.data["minfreespace"] = int(configxml.find("video/minfreespace").text)
        self.data["storage_path"] = configxml.find("video/storage").text
        self.data["webport"] = int(configxml.find("webport").text)
        if not self.data["storage_path"].endswith("/"):
            self.data["storage_path"] += "/"
        self.data["cameras"] = Camera.load_cameras(filename)
    def __str__(self):
        ret = "System Name: {0}\n".format(self.data["name"])
        ret += "Web Interface port: {0}\n".format(self.data["webport"])
        ret += "Video Length: {0} min.\n".format(self.data["video_len"])
        ret += "Width x Height: {0}x{1}\n".format(self.data["width"], self.data["height"])
        ret += "Sorage Path: {0}\n".format(self.data["storage_path"])
        ret += "Minimal Free Disk Space: {0} GB\n".format(self.data["minfreespace"])
        ret += "Cameras:\n"
        for cam in self.data["cameras"]:
            ret += "\tName: {0}\n".format(cam.name)
            ret += "\tSource: {0}\n\n".format(cam.source)
        return ret
