import boto3, random, string, requests, json
import StringIO
import zipfile
import mimetypes

def sendresponse(event, context, responsestatus, responsedata, reason):
    """Send a Success or Failure event back to CFN stack"""
    payload = {
        'StackId': event['StackId'],
        'Status' : responsestatus,
        'Reason' : reason,
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'PhysicalResourceId': event['LogicalResourceId'] + \
            ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) \
            for _ in range(10)),
        'Data': responsedata
    }
    requests.put(event['ResponseURL'], data=json.dumps(payload))
    print "Sent %s to %s" % (json.dumps(payload), event['ResponseURL'])


def handler(event, context):

    try:

        print event
        requesttype = ''
        s3 = boto3.resource('s3')

        ##Get the request type passed in by CloudFormation
        requesttype = event['RequestType']

        if requesttype == 'Delete': # if delete -- add code to clean up SiteBucket if desired (todo...)
            print "Delete Requesttype Processing Started"
            sendresponse(event, context, 'SUCCESS', {}, "")
            return

        ##Get values passed in from CloudFormation
        source_bucket = event['ResourceProperties']['SourceBucket']
        source_object = event['ResourceProperties']['SourceObject']
        destination_bucket = event['ResourceProperties']['DestinationBucket']

        print "Getting source files from " + source_bucket + "/" + source_object

        ##create the boto S3 objects to interact with buckets
        sitehosting_bucket = s3.Bucket(destination_bucket)
        source_code_bucket = s3.Bucket(source_bucket)

        content_zip = StringIO.StringIO()
        source_code_bucket.download_fileobj(source_object, content_zip)

        with zipfile.ZipFile(content_zip) as myzip:
            for nm in myzip.namelist():
                print "Filename: " + nm
                folder, new_filename = nm.split("/",1) ##Remove zipname and trailing slash from file name
                print "New Filename: " + new_filename ##All zip contents will now be deployed directly inside bucket
                if not nm.endswith("/"):
                    ## Get the object
                    obj = myzip.open(nm)
                    ## Determine the mimetype
                    obj_mime_type = mimetypes.guess_type(nm)[0]
                    
                    if obj_mime_type is None:
                        print "Cannot guess the mime type for file: " + nm
                        sitehosting_bucket.upload_fileobj(obj, new_filename)
                    else:
                        sitehosting_bucket.upload_fileobj(obj, new_filename,
                            ExtraArgs={'ContentType': obj_mime_type})
                    ## sitehosting_bucket.Object(nm).Acl().put(ACL='public-read') -- commented out until SAR allows giving this function proper permissions to modify ACLs (via managed policy)


        print "Job done!"

    except:
        raise

    responsedata = {} # dictionary to store our return data
    sendresponse(event, context, 'SUCCESS', responsedata, "N/A")