import os
import psycopg2

import hsc.hscDb as hscDb

from hsc.integration.test import Test, CommandsTest, guard
from hsc.integration.camera import getCameraInfo

class DbValidateTest(Test):
    """Mixin class to validate database"""
    def __init__(self, name, dbHost=None, dbName=None, dbUser=None, dbPass=None,
                 query=None, numRowsValidate=None, rowValidate=None):
        super(DbValidateTest, self).__init__(name)
        self.dbHost = dbHost
        self.dbName = dbName
        self.dbUser = dbUser
        self.dbPass = dbPass
        self.query = query
        self.numRowsValidate = numRowsValidate
        self.rowValidate = rowValidate

    @guard
    def validateDatabase(self):
        db = psycopg2.connect(host=self.dbHost, database=self.dbName,
                              user=self.dbUser, password=self.dbPass)
        cursor = db.cursor()
        cursor.execute(self.query)
        rows = cursor.fetchall()
        numRows = len(rows)
        if self.numRowsValidate is not None:
            self.assertTrue("Number of rows (%d)" % numRows, self.numRowsValidate(numRows))
        if self.rowValidate is not None:
            for i, r in enumerate(rows):
                self.assertTrue("Row %d (%s)" % (i, r), self.rowValidate(row))
        cursor.close()
        db.close()

    def preHook(self, **kwargs):
        pgpass = open("dot.pgpass", "w")
        pgpass.write("*:*:*:%s:%s\n" % (self.dbUser, self.dbPass))
        os.environ['PGPASSFILE'] = os.path.abspath("dot.pgpass")
        pgpass.close()
        os.chmod("dot.pgpass", 0600)


class DbCreateTest(CommandsTest, DbValidateTest):
    def __init__(self, name, camera, dbType, dbHost, dbName, dbUser, dbPass, dbPort=5432, **kwargs):
        command = os.path.join(os.environ['HSCDB_DIR'], 'bin', 'create_HscDb.py')
        command += " --dbtype=" + dbType
        command += " --dbname=" + dbName
        self.dbPort = dbPort

        cameraInfo = getCameraInfo(camera)
        query = "SELECT * FROM %s" % cameraInfo.fileTable
        numRowsValidate = lambda num: num == 0

        super(DbCreateTest, self).__init__(name, ["echo $PGPASSFILE", command], dbHost=dbHost, dbName=dbName, 
                                           dbUser=dbUser, dbPass=dbPass, query=query,
                                           numRowsValidate=numRowsValidate, **kwargs)

    def validate(self, **kwargs):
        self.validateDatabase()


class DbRawTest(CommandsTest, DbValidateTest):
    def __init__(self, name, camera, dbHost, dbName, dbUser, dbPass, source, **kwargs):
        cameraInfo = getCameraInfo(camera)

        commandList = []
        self.fileList = []
        for dirpath, dirnames, filenames in os.walk(source):
            for f in filenames:
                if not f.endswith('.fits'):
                    continue
                self.fileList.append(f)

                command = os.path.join(os.environ['HSCDB_DIR'], 'bin', cameraInfo.dbRaw)
                command += " --execute --copy --root=@WORKDIR@"
                command += " " + os.path.join(dirpath, f)
                commandList.append(command)

        query = "SELECT * FROM %s" % cameraInfo.fileTable
        numRowsValidate = lambda num: num == len(self.fileList)

        super(DbRawTest, self).__init__(name, commandList, dbHost=dbHost, dbName=dbName, dbUser=dbUser,
                                        dbPass=dbPass, query=query, numRowsValidate=numRowsValidate,
                                        **kwargs)

#    def preHook(self, workDir=".", **kwargs):
#        suprimeDataDir = os.path.split(os.path.abspath(workDir))
#        if suprimeDataDir[-1] in ("SUPA", "HSC"):
#            # hsc.pipe.base.camera.getButler will add this directory on
#            suprimeDataDir = suprimeDataDir[:-1]
#        os.environ['SUPRIME_DATA_DIR'] = os.path.join(*suprimeDataDir)


    def validate(self, **kwargs):
        self.validateDatabase()

"""
class DbProcessedTest:
    def __init__(self, name, camera, dbName, dbType, **kwargs):
        for ccd in range(numCcd):
            command = os.path.join(os.environ['HSCDB_DIR'], 'bin',
                                   'frame_regist_Corr' + camera.capitalize() + '.py')
            

        command = os.path.join(os.environ['HSCDB_DIR'], 'bin',
                               'exposure_regist_Corr' + camera.capitalize() + '.py')

class DbSourcesTest:
    inputframeobj1.py
    inputframeobj1.py
    inputframeobj1.py

    inputframeobj2.py
    inputframeobj2.py
    inputframeobj2.py


  Usage   : ./inputframeobj1.py Instrument Catalog FITSFile RerunID
    Instrument : SUP | HSC
    Catalog    : frame_match | frame_source | frame_icsource
  Example : ./inputframeobj1.py SUP frame_match ML01269690.fits fh-qa-20120508


  Usage   : ./inputframeobj2.py Instrument Catalog FrameID RerunID
    Instrument : SUP | HSC
    Catalog    : frame_match | frame_source | frame_icsource
  Example : ./inputframeobj2.py SUP frame_match SUPA01269690 fh-qa-20120508

"""
