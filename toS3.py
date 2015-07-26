import tinys3
import getopt
import sys
import os

S3_ACCESS_KEY='AKIAIFKRJ2SS7OLNABCQ'
S3_SECRET_KEY='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'

helpText = """toS3.py version 1.0 (2014-06-02)

This script uploads files to Valuerz S3 buckets.

Command line syntax:

python toS3.py <options> <filename> <s3 filename> <bucket>

"""

def uploadToS3(fileName, s3_fileName, bucket):
    conn = tinys3.Connection(S3_ACCESS_KEY, S3_SECRET_KEY, tls=True)

    f = open(fileName, 'rb')
    conn.upload(s3_fileName, f, bucket)

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hb:r:",
            ["help", "bucket=", "remove="]
        )
    except getopt.GetoptError:
        print helpText
        exit(1)

    localFile = args[0]
    s3file = args[1]
    bucket = args[2]
    remove = False

    for opt,arg in opts:
        if opt in ("-h", "--help"):
            print helpText
            exit(1)
        elif opt in ("-r", "--remove"):
            remove = True
        #end if

    if os.path.exists(localFile):
        print "Uploading %s to %s:%s" % (localFile, bucket, s3file)
        uploadToS3(localFile, s3file, bucket)
        if remove:
            print "Removing %s" % localFile
            os.remove(localFile)
    else:
        print "File doesn't exist: %s" % localFile
