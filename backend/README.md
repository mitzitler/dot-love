## Backend - CarWorld Serverless
``` sh
|--infra
|---+ infrastructure as code
  |
  |--lambda
  |---+ api endpoints as lambda functions
  |
  |--infra
  |---+ cloudformation to build and deploy the infrastructure stored here
    |
    |--CWCore Stack
    |---+ CWAPIGW, AuthController, AuthDB
    |--CWCommerce Stack
    |---+ CommerceController, CommerceDB
    |}--(CWForum Stack)?
  |
  |--tests
    |---+ idk it works on my machine
```

![CarWorld System Diagram](backend/CWSystemDiagram.jpg/infra?raw=true "CarWorld System Design")

### Deployment
Starting from the `backend` directory, create and enter a virtualenv (MacOS and Linux):
```
python3 -m venv .venv
source .venv/bin/activate # or .venv\Scripts\activate.bat for Windows
```
Install Python packages:
```
pip install -r requirements.txt
```
Make sure to install these packages into special sub-directories (that will get packaged into lambda layers):
```
pip install pyjwt==2.6.0 typing-extensions==3.7.4.1 --target ./lambda/validator/jwt-dependency-layer/python/lib/python3.11/site-packages
pip install stripe --target ./lambda/commerce/stripe-layer/python/lib/python3.11/site-packages
pip install aws-lambda-powertools --target ./lambda/commerce/powertools-layer/python/lib/python3.11/site-packages
```
Soemthing to keep an eye out for is that if the Python version you are using to create the venv and make these `pip` calls is not the same as the version in the Lambda's runtime (currently Python 3.11), you might get some mysterious errors from the validator function along the lines of [this Stack Overflow post](https://stackoverflow.com/questions/57189352/aws-lambda-unable-to-import-module-python-handler-no-module-named-cffi-bac).

The `auth` lambda function is written in JavaScript (the rest are written in Python). It needs a little extra love:
```
cd lambda/auth
npm i
mkdir zip # or rm zip/function.zip
zip -r zip/function.zip index.js package-lock.json package.json node_modules/
cd ../..
```
Then synthesize the CloudFormation template:
```
cdk synth
```
Now you can deploy with `cdk deploy` (you'll need some AWS credentials though), AND you will need to login to the AWS console and manually upload the `function.zip` file from `lambda/auth/zip` to the Auth lambda.

At the moment, when running the frontend development server, you'll need to log into the AWS console, pull up your newly created API Gateway, and find and replace it's ID string into the URLs in the `CW_API_ENDPOINTS` variable in `frontend/src/AppConstants.tsx` for the frontend to be pointed at the new deployment.
