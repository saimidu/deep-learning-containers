import json
import numpy as np
import json
import io
from PIL import Image
import requests
import os
import io
from PIL import Image
import numpy as np

is_neuron_host = int(os.environ.get("NEURON_CORE_HOST_TOTAL", 0)) > 0
print("IS NEURON HOST {}".format(is_neuron_host))

if is_neuron_host:
    import grpc
    import gzip
    import tensorflow as tf
    from tensorflow_serving.apis import predict_pb2, prediction_service_pb2_grpc
    from google.protobuf.json_format import MessageToJson

    prediction_services = {}
    compression_algo = gzip

def handler(data, context):
    f = data.read()
    f = io.BytesIO(f)
    image = Image.open(f).convert('RGB')
    batch_size = 1
    image = np.asarray(image.resize((224, 224)))
    image = np.concatenate([image[np.newaxis, :, :]] * batch_size)

    if not is_neuron_host:
        body = json.dumps({"signature_name": "serving_default", "instances": image.tolist()})
        response = requests.post(context.rest_uri, data=body)
        if response.status_code != 200:
            raise ValueError(response.content.decode('utf-8'))

        response_content_type = context.accept_header
        prediction = response.content
        return prediction, response_content_type
    else:
        request = predict_pb2.PredictRequest()
        request.model_spec.name = 'compiled_models'
        request.model_spec.signature_name = 'serving_default'
        request.inputs['images'].CopyFrom(
            tf.compat.v1.make_tensor_proto(image, shape=image.shape, dtype=tf.float32))

        # Call Predict gRPC service
        result = get_prediction_service(context).Predict(request, 60.0)
        print("Returning the response for grpc port: %s" % (context.grpc_port))

        # Return response
        jsonObj = MessageToJson(result)
        return jsonObj, "application/json"

def get_prediction_service(context):
    #global prediction_service
    if not context.grpc_port in prediction_services:
        #print("Creating service for port %s" % context.grpc_port)
        channel = grpc.insecure_channel("localhost:{}".format(context.grpc_port))
        prediction_services[context.grpc_port] = prediction_service_pb2_grpc.PredictionServiceStub(channel)
    return prediction_services[context.grpc_port]
