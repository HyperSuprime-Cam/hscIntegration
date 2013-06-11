import os, os.path
from hsc.integration.test import CommandsTest
from hsc.integration.ccdValidation import ButlerValidationTest
from hsc.integration.camera import getCameraInfo
import hsc.pipe.base.camera as hscCamera

class DataTest(CommandsTest, ButlerValidationTest):
    def __init__(self, name, camera, source, dataIdList, datasetType="raw"):
        self.camera = camera
        self.dataIdList = dataIdList
        self.datasetType = datasetType
        self.fitsFiles = set()
        inputs = []
        for dirpath, dirnames, filenames in os.walk(source):
            for f in filenames:
                if f.endswith('.fits'):
                    inputs.append(os.path.join(dirpath, f))
                    self.fitsFiles.add(f)
        cameraInfo = getCameraInfo(camera)
        self.registryDir = cameraInfo.addDir
        commandList = [[os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", cameraInfo.refileScript),
                        "--link", "--execute", "--root=@WORKDIR@"] + inputs,
                       [os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", "genInputRegistry.py"),
                        "--create", "--root=@WORKDIR@/" + self.registryDir, "--camera=" + cameraInfo.abbrev]
                       ]
        super(DataTest, self).__init__(name, ["setup", camera], commandList)

    def validate(self, workDir=".", **kwargs):
        found = set()
        for dirpath, dirnames, filenames in os.walk(os.path.join(workDir, self.registryDir)):
            for f in filenames:
                if f.endswith('.fits'):
                    found.add(f)
        self.assertEqual("Number of FITS files", len(found), len(self.fitsFiles))
        registry = os.path.join(workDir, self.registryDir, "registry.sqlite3")
        self.assertTrue("Registry created", os.path.isfile(registry))

        cameraInfo = getCameraInfo(self.camera)
        butler = hscCamera.getButler(self.camera, root=os.path.join(workDir, cameraInfo.addDir))
        for dataId in self.dataIdList:
            self.validateDataset(butler, dataId, self.datasetType)

        return True

class CalibTest(CommandsTest, ButlerValidationTest):
    def __init__(self, name, camera, detrend, dataIdList, source=None, validity=None):
        self.camera = camera
        self.detrend = detrend
        self.dataIdList = dataIdList
        self.source = source
        commandList = []
        cameraInfo = getCameraInfo(camera)
        if source is not None:
            # Get calibrations from the source
            for dirpath, dirnames, filenames in os.walk(source):
                targetDir = os.path.join("@WORKDIR@", cameraInfo.addDir, "CALIB",
                                         os.path.relpath(dirpath, source))
                for f in filenames:
                    commandList.append(["ln", "-s", os.path.join(dirpath, f), os.path.join(targetDir, f)])

        generate = [os.path.join(os.environ['OBS_SUBARU_DIR'], "bin", "genCalibRegistry.py"),
                   "--create", "--root=@WORKDIR@/" + os.path.join(cameraInfo.addDir, "CALIB"),
                    "--camera=" + camera]
        if validity is not None:
            generate += ["--validity=%d" % validity]

        commandList.append(generate)
        super(CalibTest, self).__init__(name, ["calib", "setup", camera], commandList)

    def getTargetDir(self, workDir):
        cameraInfo = getCameraInfo(self.camera)
        return os.path.join(workDir, cameraInfo.addDir, "CALIB")

    def execute(self, workDir=".", **kwargs):
        if self.source is not None:
            # Make output directories first, so we can link
            target = self.getTargetDir(workDir)
            for dirpath, dirnames, filenames in os.walk(self.source):
                targetDir = os.path.join(target, os.path.relpath(dirpath, self.source))
                if not os.path.isdir(targetDir):
                    os.makedirs(targetDir)
        super(CalibTest, self).execute(workDir=workDir, **kwargs)

    def validate(self, workDir=".", **kwargs):
        target = self.getTargetDir(workDir)
        registry = os.path.join(target, "calibRegistry.sqlite3")
        self.assertTrue("Registry created", os.path.isfile(registry))

        cameraInfo = getCameraInfo(self.camera)
        butler = hscCamera.getButler(self.camera, root=os.path.join(workDir, cameraInfo.addDir))
        for dataId in self.dataIdList:
            self.validateDataset(butler, dataId, self.detrend)

        return True
