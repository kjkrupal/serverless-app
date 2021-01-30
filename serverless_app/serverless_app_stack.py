from aws_cdk import (
    core,
    aws_s3,
    aws_lambda,
    aws_dynamodb,
    aws_iam,
    aws_lambda_event_sources,
)

from . import constants

image_bucket_name = constants.IMAGE_BUCKET_NAME


class ServerlessAppStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create S3 bucket here.
        bucket = aws_s3.Bucket(self, image_bucket_name)

        # CFN output for S3 bucket creation.
        core.CfnOutput(
            self,
            "image-bucket",
            value=bucket.bucket_name,
            description="Bucket for uploading images",
        )

        # Create dynamodb table for storing image labels here.
        table = aws_dynamodb.Table(
            self,
            "image-lables",
            partition_key=aws_dynamodb.Attribute(
                name="image", type=aws_dynamodb.AttributeType.STRING
            ),
        )

        # CFN output for dynamodb table creation.
        core.CfnOutput(
            self,
            "image-lables-ddb-table",
            value=table.table_name,
            description="DDB table for storing image lables.",
        )

        function = aws_lambda.Function(
            self,
            "rekognitionFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler="handler.main",
            code=aws_lambda.Code.asset("./rekognitionLambda"),
            timeout=core.Duration.seconds(30),
            memory_size=1024,
        )
        function.add_environment("TABLE", table.table_name)
        function.add_environment("BUCKET", bucket.bucket_name)
        function.add_event_source(
            aws_lambda_event_sources.S3EventSource(
                bucket=bucket, events=[aws_s3.EventType.OBJECT_CREATED]
            )
        )
        bucket.grant_read(function)
        table.grant_write_data(function)

        function.add_to_role_policy(
            statement=aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["rekognition:DetectLabels"],
                resources=["*"],
            )
        )
