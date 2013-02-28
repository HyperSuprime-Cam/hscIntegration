import os
import psycopg2

import hsc.hscDb as hscDb

from hsc.integration.test import Test, CommandsTest, guard
from hsc.integration.camera import getCameraInfo

class DbValidateTest(Test):
    """Mixin class to validate database"""
    def __init__(self, name, keywords, dbHost=None, dbName=None, dbUser=None, dbPass=None,
                 query=None, numRowsValidate=None, rowValidate=None):
        super(DbValidateTest, self).__init__(name, keywords)
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

#
# To start postgres:
#
# price@master:/data1a/work/price/integration $ initdb -D `pwd`/db/
# price@master:/data1a/work/price/integration $ pg_ctl -D /data1a/work/price/integration/db -l logfile start
#


class DbCreateTest(CommandsTest, DbValidateTest):
    def __init__(self, name, camera, dbType, dbHost, dbName, dbUser, dbPass, dbPort=5432, **kwargs):
        command = os.path.join(os.environ['HSCDB_DIR'], 'bin', 'create_HscDb.py')
        command += " --dbhost=" + dbHost
        command += " --dbtype=" + dbType
        command += " --dbname=" + dbName
        command += " --dbuser=" + dbUser
        command += " --dbpass=" + dbPass
        command += " --drop"
        self.dbPort = dbPort

        cameraInfo = getCameraInfo(camera)
        query = "SELECT * FROM %s" % cameraInfo.fileTable
        numRowsValidate = lambda num: num == 0

        super(DbCreateTest, self).__init__(name, ["db", camera], [command], dbHost=dbHost, dbName=dbName, 
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
                command += " --execute --relocate=none --root=@WORKDIR@"
                command += " --dbhost " + dbHost
                command += " --dbname " + dbName
                command += " --dbuser " + dbUser
                command += " --dbpass " + dbPass
                command += " " + os.path.join(dirpath, f)
                commandList.append(command)

        query = "SELECT * FROM %s" % cameraInfo.fileTable
        numRowsValidate = lambda num: num == len(self.fileList)

        super(DbRawTest, self).__init__(name, ["db", camera], commandList, dbHost=dbHost, dbName=dbName,
                                        dbUser=dbUser, dbPass=dbPass, query=query,
                                        numRowsValidate=numRowsValidate, **kwargs)

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





"""
Here is the command lines which are called in the 
onsiteQa's top-level script (in runOnsiteQa).


# setups environments 
source /work/ana/products/loadLSST.sh
setup hscPipe 1.12.0c_hsc
setup -j -r /work/ana/astrometry_net_data/sdss-dr8/
setup -j -r /work/ana/local/hscDb/tip
setup -j -r /work/ana/local/psycopg2/2.4.5

# or simply  source /data/data1/ope/config/onsiteTest-hscPipe1.11.2_hsc-20130131comm/envExports.sh in 
# the actual operation.


### Frame analysis & Registration of Catalogs

rerun=fh-20130218a

#
# $HSCDB_DIR/policy/hscDb_param.paf should be edited before running the scProcessCcdOnsiteDb.py
# to point an appropriate database instance. In the recent operation, database instance is 
# created for every rerun for Steve-san's demand. 
# I run doSetupRerun.sh (attached) to do this preparation.
#
sh doSetupRerun.sh $rerun

#
# At Hilo cluster, the scProcessCccOnsiteDb.py is called via torque(pbs) in a jobArray mode 
# with a command like: 'qsub -t 0-103 qsub_script.sh.
# ex.
#  qsub -V -t 0-103 /data/data1/ope/log/2013-02-01/qsub_fram_hsc0901508_13302084_20130201-232507.sh
#
anaId=13302084 # provided by a toplevel script
registId=0     # provided by a toplevel script
configId=onsiteTest-hscPipe1.11.2_hsc-20130131com # provided by a toplevel script
overridingConfig=/data/data1/ope/config/$configId/onsite_user_config.py

visit=902048
ccd=0        

scProcessCcdOnsiteDb.py hscSim /data/data1/Subaru/HSC --calib /data/data1/Subaru/HSC/CALIB/ -C $overridingConfig --doraise --id visit=$visit ccd=$ccd --output /work/Subaru/HSC/rerun/$rerun --anaid $anaId --registid $registId

frameId="HSCA90204800"
ccd=000
logDir=/data/data1/ope/log/2013-02-18

outputDir=/work/Subaru/HSC/rerun/$rerun/00398/W-S-I+/output
filenameSrc=$outputDir/SRC-0901582-${ccd}.fits
filenameIcsrc=$outputDir/ICSRC-0901582-${ccd}.fits
filenameMl=$outputDir/ML-0901582-${ccd}.fits
filenameSrcml=$outputDir/SRCML-0901582-${ccd}.fits
inputcat1.py HSC frame_source   $frameId $rerun $filenameSrc   $logDir 
inputcat2.py HSC frame_source   $frameId $rerun $logDir
inputcat1.py HSC frame_icsource $frameId $rerun $filenameIcsrc $logDir
inputcat1.py HSC frame_match    $frameId $rerun $filenameMl    $logDir
inputcat2.py HSC frame_icsource $frameId $rerun $logDir 
inputcat2.py HSC frame_match    $frameId $rerun $logDir 


### Exposure analysis (solvetansip & collecting resulting values from frame analyses)

setup -j -r /work/ana/local/exposureQa/tip
overridingPaf=/data/data1/ope/config/$configId/onsite_user_policy_expana.pa

exposureQaOnsiteDb.py -i hscSim -I /data/data1/Subaru/HSC -O /data/data2/Subaru/HSC/rerun/$rerun -r $rerun -p $overridingPaf --analysisId $anaId --configId $configId $visit


Thank you!
Hisanori
#!/bin/sh

# This script setup environment variables with a new rerun and create 
# a new database instance with the name of the given rerun
# A paf file for database access is also modified & rsynced across the 
# master & slave nodes

#export DBNAME=fh-20130118-pipeQa-2
export DBNAME=$1

echo "Creating new hscana DB with the name: " $DBNAME
create_HscDb.py -d $DBNAME -T Red_Hsc -U hscana -H hsca-db01

####echo "Truncating HscPipe Raw data entries ..."
####psql -h hsca-db01 -d hscpipe -U hscana -c "\i /data/data1/devel/hscPipe1.1X/test_run/db_schema/registry/truncate.sql"

echo "Updating hscDb param for query_db and regist_db with the name: " $DBNAME
\mv /work/ana/local/hscDb/tip/policy/hscDb.paf /work/ana/local/hscDb/tip/policy/hscDb.paf.orig
cat /work/ana/local/hscDb/tip/policy/hscDb.paf.orig | sed -e "s/^query_db:.*$/query_db: \"$DBNAME\"/" -e "s/^regist_db:.*$/regist_db: \"$DBNAME\"/" > /tmp/hscDb.paf
\mv /tmp/hscDb.paf /work/ana/local/hscDb/tip/policy/hscDb.paf

echo "Rsyncing hscDb and pipeQA over slave nodes ..."
sh /work/ana/local/doRsyncHscDbPipeQa.sh
"""
