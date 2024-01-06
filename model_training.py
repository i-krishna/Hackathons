import sagemaker
from sagemaker import get_execution_role
from sagemaker.amazon.amazon_estimator import get_image_uri
from sagemaker.session import s3_input, Session

# Initialize SageMaker variables
bucket = sagemaker.Session().default_bucket()
prefix = 'sagemaker/freestyle-libre-diabetes'
role = get_execution_role()

# Location of preprocessed data in S3
train_data = f's3://{bucket}/{prefix}/train'
validation_data = f's3://{bucket}/{prefix}/validation'

# Define the model 
container = get_image_uri(boto3.Session().region_name, 'xgboost', '1.0-1')

xgb = sagemaker.estimator.Estimator(container,
                                    role, 
                                    instance_count=1, 
                                    instance_type='ml.m4.xlarge',
                                    output_path=f's3://{bucket}/{prefix}/output')

# Set hyperparameters
xgb.set_hyperparameters(max_depth=5,
                        eta=0.2,
                        gamma=4,
                        min_child_weight=6,
                        subsample=0.8,
                        objective='binary:logistic',
                        num_round=100)

# Train model
xgb.fit({'train': s3_input(train_data), 'validation': s3_input(validation_data)})

# Deploy model to an endpoint
xgb_predictor = xgb.deploy(initial_instance_count=1, instance_type='ml.m4.xlarge')
