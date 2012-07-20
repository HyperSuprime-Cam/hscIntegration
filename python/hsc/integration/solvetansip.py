import os, os.path
from hsc.integration.test import CommandsTest
from hsc.integration.camera import CameraInfo

class SolveTansipTest(CommandsTest):
    def __init__(self, name, camera, visit, rerun=None, **kwargs):
        self.camera = camera
        self.visit = visit
        self.rerun = rerun

        cameraInfo = CameraInfo(camera)
        command = os.path.join(os.environ['SOLVETANSIP_DIR'], 'bin', 'solvetansip.py')
        command += " " + camera + " @WORKDIR@/" + cameraInfo.addDir + " --id visit=%d" % visit
        if rerun is not None:
            command += " --rerun=" + rerun

        super(SolveTansipTest, self).__init__(name, [command], **kwargs)


    def validate(self, *args, **kwargs):
        # No validation yet: we only care that it runs
        pass

