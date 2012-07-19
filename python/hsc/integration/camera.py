
class CameraInfo(object):
    def __init__(self, camera):
        if camera.lower() in ("suprimecam", "suprime-cam", "sc"):
            self.addDir = "SUPA"
            self.refileScript = "refileSupaFiles.py"
        elif camera.lower() in ("hsc", "hscsim"):
            self.addDir = "HSC"
            self.refileScript = "refileHSCFiles.py"
        else:
            raise RuntimeError("Unrecognised camera: %s" % camera)
