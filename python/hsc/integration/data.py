import os, os.path
from hsc.integration.integration import CommandsTest

class DataTest(CommandsTest):
    def __init__(self, name, camera, source, target):
        self.target = target
        self.fitsFiles = set()
        inputs = []
        for dirpath, dirnames, filenames in os.walk(source):
            for f in filenames:
                if f.endswith('.fits'):
                    inputs.append(os.path.join(dirpath, f))
                    self.fitsFiles.add(f)
        if camera.lower() in ("suprimecam", "suprime-cam", "sc"):
            refileScript = "refileSupaFiles.py"
            self.registryDir = "SUPA"
        elif camera.lower() in ("hsc"):
            refileScript = "refileHSCFiles.py"
            self.registryDir = "HSCA"
        else:
            raise RuntimeError("Unrecognised camera: %s" % camera)
        commandList = [[os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", refileScript),
                        "--copy", "--execute", "--root=" + target] + inputs,
                       [os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", "genInputRegistry.py"),
                        "--create", "--root=" + os.path.join(target, self.registryDir), "--camera=" + camera]
                       ]
        super(DataTest, self).__init__(name, commandList)

    def validate(self):
        found = set()
        for dirpath, dirnames, filenames in os.walk(self.target):
            for f in filenames:
                if f.endswith('.fits'):
                    found.add(f)
        self.assertEqual("Number of FITS files", len(found), len(self.fitsFiles))
        self.assertEqual("All FITS files filed", found, self.fitsFiles)
        registry = os.path.join(self.target, self.registryDir, "registry.sqlite3")
        self.assertTrue("Registry created", os.path.isfile(registry))
        return True
