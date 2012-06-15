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
        elif camera.lower() in ("hsc", "hscsim"):
            refileScript = "refileHSCFiles.py"
            self.registryDir = "HSC"
        else:
            raise RuntimeError("Unrecognised camera: %s" % camera)
        commandList = [[os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", refileScript),
                        "--link", "--execute", "--root=" + target] + inputs,
                       [os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", "genInputRegistry.py"),
                        "--create", "--root=" + os.path.join(target, self.registryDir), "--camera=" + camera]
                       ]
        super(DataTest, self).__init__(name, commandList)

    def validate(self):
        found = set()
        for dirpath, dirnames, filenames in os.walk(os.path.join(self.target, self.registryDir)):
            for f in filenames:
                if f.endswith('.fits'):
                    found.add(f)
        self.assertEqual("Number of FITS files", len(found), len(self.fitsFiles))
        self.assertEqual("All FITS files filed", found, self.fitsFiles)
        registry = os.path.join(self.target, self.registryDir, "registry.sqlite3")
        self.assertTrue("Registry created", os.path.isfile(registry))
        return True

class CalibTest(CommandsTest):
    def __init__(self, name, camera, source, target, validity=None):
        self.target = target
        commandList = []
        for dirpath, dirnames, filenames in os.walk(source):
            targetDir = os.path.join(target, os.path.relpath(dirpath, source))
            if not os.path.isdir(targetDir):
                os.makedirs(targetDir)
            for f in filenames:
                commandList.append(["ln", "-s", os.path.join(dirpath, f), os.path.join(targetDir, f)])
        generate = [os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", "genCalibRegistry.py"),
                   "--create", "--root=" + target, "--camera=" + camera]
        if validity is not None:
            generate += ["--validity=%d" % validity]

        commandList.append(generate)
        super(CalibTest, self).__init__(name, commandList)

    def validate(self):
        registry = os.path.join(self.target, "calibRegistry.sqlite3")
        self.assertTrue("Registry created", os.path.isfile(registry))
        return True
