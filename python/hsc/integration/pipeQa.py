import os, os.path
from hsc.integration.test import CommandsTest
from hsc.integration.camera import getCameraInfo

class PipeQaTest(CommandsTest):
    def __init__(self, name, camera, visits, rerun, target):
        self.camera = camera
        self.visits = visits
        self.target = target
        self.rerun = rerun

        mkdir = "mkdir -p " + os.path.join(target, rerun)
        newQa = os.path.join(os.environ['TESTING_DISPLAYQA_DIR'], 'bin', 'newQa.py') + " " + rerun
        pipeQa = os.path.join(os.environ['TESTING_PIPEQA_DIR'], 'bin', 'pipeQa.py') + \
            " -C " + camera + " -v (" + "|".join(map(str, visits)) + ") -R " + rerun + " ."

        super(PipeQaTest, self).__init__(name, ["qa", camera], [mkdir, newQa, pipeQa])
        

    def preHook(self, workDir=".", **kwargs):
        os.environ['TESTBED_PATH'] = workDir
        os.environ['WWW_ROOT'] = self.target
        os.environ['WWW_RERUN'] = self.rerun


    def validate(self, workDir=".", **kwargs):
        pass
