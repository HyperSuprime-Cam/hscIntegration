import os.path

class CameraInfo(object):
    """Base class for camera-specific options"""
    def __init__(self, **kwargs):
        for kw in ("addDir",            # Additional directory elements to add to workdir
                   "refileScript",      # Name of script for filing exposures
                   "override",          # Name of configuration override file for processCcd
                   "dbRaw",             # Name of script for registering raw exposures in PGSQL
                   "dbFrame",           # Name of script for registering processed frames in PGSQL
                   "dbExposure",        # Name of script for registering processed exposure in PGSQL
                   "inputCat",          # Name of instrument in inputCat script
                   ):
            assert(kw in kwargs)
            setattr(self, kw, kwargs[kw])


class SuprimeCamCameraInfo(CameraInfo):
    def __init__(self):
        super(SuprimeCamCameraInfo).__init__(
            addDir = "SUPA",
            refileScript = "refileSupaFiles.py",
            override = os.path.join(os.environ['HSCPIPE_DIR'], 'config', 'suprimecam.py')
            dbRaw = "regist_raw_Suprime.py",
            dbFrame = "frame_regist_CorrSuprime.py",
            dbExposure = "exposure_regist_CorrSuprime.py",
            inputCat = "SUP",
            )

class HscCameraInfo(CameraInfo):
    def __init__(self):
        super(SuprimeCamCameraInfo).__init__(
            addDir = "HSC",
            refileScript = "refileHscFiles.py",
            override = os.path.join(os.environ['HSCPIPE_DIR'], 'config', 'hsc.py')
            dbRaw = "regist_raw_Hsc.py",
            dbFrame = "frame_regist_CorrHsc.py",
            dbExposure = "exposure_regist_CorrHsc.py",
            inputCat = "HSC",
            )


def getCameraInfo(camera):
    """Factory function to produce desired CameraInfo derived class"""
    if camera.lower() == "suprimecam":
        return SuprimeCamCameraInfo()
    if camera.lower() == "hsc":
        return HscCameraInfo()
    raise RuntimeError("Unrecognised camera name: %s" % camera)
