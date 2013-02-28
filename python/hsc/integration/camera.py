import os.path

try:
    import hsc.hscDb as hscDb
except ImportError:
    print "WARNING: can't import hscDb"
    class DummyHscDb(object):
        def __init__(self):
            self.suppipe_file_mng_tab = "UNKNOWN"
            self.hscpipe_file_mng_tab = "UNKNOWN"
    hscDb = DummyHscDb()


class CameraInfo(object):
    """Base class for camera-specific options"""
    def __init__(self, **kwargs):
        for kw in ("addDir",            # Additional directory elements to add to workdir
                   "abbrev",            # Abbreviation of name, used in some scripts
                   "refileScript",      # Name of script for filing exposures
                   "override",          # Name of configuration override file for processCcd
                   "dbRaw",             # Name of script for registering raw exposures in PGSQL
                   "dbFrame",           # Name of script for registering processed frames in PGSQL
                   "dbExposure",        # Name of script for registering processed exposure in PGSQL
                   "inputCat",          # Name of instrument in inputCat script
                   "fileTable",         # Name of database table with file information
                   "mapper",            # Name of mapper (for _mapper file)
                   ):
            assert(kw in kwargs)
            setattr(self, kw, kwargs[kw])


class SuprimeCamCameraInfo(CameraInfo):
    def __init__(self):
        super(SuprimeCamCameraInfo, self).__init__(
            addDir = "SUPA",
            abbrev = "SC",
            refileScript = "refileSupaFiles.py",
            override = os.path.join(os.environ['HSCPIPE_DIR'], 'config', 'suprimecam.py'),
            dbRaw = "regist_raw_Suprime.py",
            dbFrame = "frame_regist_CorrSuprime.py",
            dbExposure = "exposure_regist_CorrSuprime.py",
            inputCat = "SUP",
            fileTable = hscDb.suppipe_file_mng_tab,
            mapper = "lsst.obs.suprimecam.SuprimecamMapper",
            )

class HscSimCameraInfo(CameraInfo):
    def __init__(self):
        super(HscSimCameraInfo, self).__init__(
            addDir = "HSC",
            abbrev = "HSC",
            refileScript = "refileHSCFiles.py",
            override = os.path.join(os.environ['HSCPIPE_DIR'], 'config', 'hsc.py'),
            dbRaw = "regist_raw_Hsc.py",
            dbFrame = "frame_regist_CorrHsc.py",
            dbExposure = "exposure_regist_CorrHsc.py",
            inputCat = "HSC",
            fileTable = hscDb.hscpipe_file_mng_tab,
            mapper = "lsst.obs.hscSim.HscSimMapper",
            )


def getCameraInfo(camera):
    """Factory function to produce desired CameraInfo derived class"""
    if camera.lower() == "suprimecam":
        return SuprimeCamCameraInfo()
    if camera.lower() == "hscsim":
        return HscSimCameraInfo()
    raise RuntimeError("Unrecognised camera name: %s" % camera)
