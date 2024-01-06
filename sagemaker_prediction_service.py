from flask import Flask, request, jsonify
import boto3
import json

app = Flask(__name__)

sagemaker_runtime = boto3.client('sagemaker-runtime')

@app.route('/predict', methods=['POST'])
def predict():
    data = json.dumps(request.json)
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName='sagemaker-endpoint-URL',  
        Body=data,
        ContentType='application/json'
    )
    result = json.loads(response['Body'].read().decode())
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
