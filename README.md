# SampleStaticSiteForSAR
Sample static site and SAM template for deployment via Serverless Application Repository.  This is an MVP implementation to prove out the ability to deploy a static website via the Serverless Application Repository.

## Description

This repo consists of the following main components:

- A SAM template that defines (template.yaml)
  - S3 bucket for a static website to be deployed to
  - S3 bucket policy to make all items public for the bucket above
  - A Lambda function that is to be used as a CloudFormation custom resource for the deployment of static site assets
  - A 'Custom Resource' which points to the Arn of the function created above - this will result in the above function being called exactly once to perform the work of deploying the static site assets from a publicly available S3 bucket to the destination site hosting bucket created above
    - Take a close look at the 'Properties' section of the Custom Resource - this is how you let the function know where to grab the static website's source files - this presumes the files are in a single ZIP stored in a publicly accessible S3 bucket 
- Source code for the Lambda function referenced in the template (deploy.py)
- Dependencies for the 'requests' module used by the Lambda function to call back to Cloudformation and return a SUCCESS of FAILURE code

## How to use this template

Once you've downloaded the contents to your local repo, do the following:

1. Zip up all the contents of the static file you'd like to deploy and upload them in a publicly acessible S3 bucket that you own
2. Update "SourceBucket" and "SourceObject" properties of the Custom Resource in the template.yaml file to reference the location where you've placed your static website assets.  You can re-use this bucket in Step #4 below or use a different one.  Assume this bucket is yourBucketName.
3. Run the following command from the AWS CLI "aws cloudformation package --template-file template.yaml --output-file output-template.yaml --s3-bucket yourBucketName"
4. Once the output-template.yaml is generated, you can go into the Publisher area of the Serverless Application Repository and upload that file to publish your app.
