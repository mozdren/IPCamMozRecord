import threading
import time
import datetime
import os
import subprocess

def freespace(store_path):
    disk = os.statvfs(store_path)
    return float(disk.f_bsize * disk.f_bavail / 1024 / 1024) / 1024.0

class OldRemover(threading.Thread):
    def __init__(self, configuration):
        threading.Thread.__init__(self)
        self.can_work = True
        self.configuration = configuration
        self.storage_paths = [self.configuration.data["storage_path"]]
        self.limit = self.configuration.data["minfreespace"]
        self.iter = 0
    
    def shutdown(self):
        self.can_work = False
    
    def run(self):
        print "Old Files Remover for "+str(self.storage_paths)+" is running."
        print "The limit is set to "+str(self.limit)+" GB."
        while self.can_work:
            try:
                time.sleep(1)
                self.iter += 1
                if (self.iter > 60):
                    self.iter = 0
                    space_left = freespace(self.storage_paths[0])
                    if space_left < self.limit:
                        for storage_path in self.storage_paths:
                            proc = subprocess.Popen("find {0} | grep .avi$".format(storage_path), shell = True, stdout=subprocess.PIPE)
                            proc.wait()
                            data = proc.communicate()[0]
                            data = data.split("\n")
                            data = [x for x in data if x.endswith(".avi")]
                            data.sort()
                            print "found files count: " + str(len(data))
                            if len(data) > 0:
                                print "removing: "+str(data[0])
                                subprocess.call('rm "{0}"'.format(data[0]), shell = True)
                    else:
                        print "Space left at {0}: {1} GB.".format(self.storage_paths, space_left)
            except Exception as error:
                print "Error at OldRemover: {0}".format(error)

def test_module():
    old_remover = OldRemover(["/home"], 10)
    old_remover.start()
    time.sleep(50)
    old_remover.can_work = False

if __name__ == "__main__":
    test_module()
