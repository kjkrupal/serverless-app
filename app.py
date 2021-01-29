#!/usr/bin/env python3

from aws_cdk import core

from serverless_app.serverless_app_stack import ServerlessAppStack


app = core.App()
ServerlessAppStack(app, "serverless-app")

app.synth()
