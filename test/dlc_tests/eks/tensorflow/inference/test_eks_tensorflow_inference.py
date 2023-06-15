import os
import random

import pytest

from invoke import run

from dlc_test_utils import eks as eks_utils
import dlc_test_utils


@pytest.mark.model("mnist")
def test_eks_tensorflow_neuron_inference(tensorflow_inference_neuron):
    num_replicas = "1"

    rand_int = random.randint(4001, 6000)

    processor = "neuron"

    model_name = "mnist_neuron"
    yaml_path = os.path.join(
        os.sep, "tmp", f"tensorflow_single_node_{processor}_inference_{rand_int}.yaml"
    )
    inference_service_name = selector_name = f"simple-{processor}-{rand_int}"
    model_base_path = get_eks_tensorflow_model_base_path(tensorflow_inference_neuron, model_name)
    command, args = get_tensorflow_command_args(
        tensorflow_inference_neuron, model_name, model_base_path
    )

    search_replace_dict = {
        "<NUM_REPLICAS>": num_replicas,
        "<SELECTOR_NAME>": selector_name,
        "<INFERENCE_SERVICE_NAME>": inference_service_name,
        "<DOCKER_IMAGE_BUILD_ID>": tensorflow_inference_neuron,
        "<COMMAND>": command,
        "<ARGS>": args,
    }

    search_replace_dict["<NUM_INF1S>"] = "1"

    eks_utils.write_eks_yaml_file_from_template(
        eks_utils.get_single_node_inference_template_path("tensorflow", processor),
        yaml_path,
        search_replace_dict,
    )

    secret_yml_path = eks_utils.get_aws_secret_yml_path()

    try:
        run("kubectl apply -f {}".format(yaml_path))

        port_to_forward = random.randint(49152, 65535)

        if eks_utils.is_service_running(selector_name):
            eks_utils.eks_forward_port_between_host_and_container(
                selector_name, port_to_forward, "8501"
            )

        inference_string = '\'{"instances": ' + "{}".format([[0 for i in range(784)]]) + "}'"
        assert dlc_test_utils.request_tensorflow_inference(
            model_name=model_name, port=port_to_forward, inference_string=inference_string
        )
    finally:
        run(f"kubectl delete deployment {selector_name}")
        run(f"kubectl delete service {selector_name}")


@pytest.mark.skip(reason="Will be enabled once infrastructure changes are made")
@pytest.mark.model("mnist")
def test_eks_tensorflow_neuronx_inference(tensorflow_inference_neuronx):
    num_replicas = "1"

    rand_int = random.randint(4001, 6000)

    processor = "neuronx"
    model_name = "simple_neuronx"

    yaml_path = os.path.join(
        os.sep, "tmp", f"tensorflow_single_node_{processor}_inference_{rand_int}.yaml"
    )
    inference_service_name = selector_name = f"simple-{processor}-{rand_int}"
    model_base_path = get_eks_tensorflow_model_base_path(tensorflow_inference_neuronx, model_name)
    command, args = get_tensorflow_command_args(
        tensorflow_inference_neuronx, model_name, model_base_path
    )

    search_replace_dict = {
        "<NUM_REPLICAS>": num_replicas,
        "<SELECTOR_NAME>": selector_name,
        "<INFERENCE_SERVICE_NAME>": inference_service_name,
        "<DOCKER_IMAGE_BUILD_ID>": tensorflow_inference_neuronx,
        "<COMMAND>": command,
        "<ARGS>": args,
    }

    search_replace_dict["<NUM_INF1S>"] = "1"

    eks_utils.write_eks_yaml_file_from_template(
        eks_utils.get_single_node_inference_template_path("tensorflow", processor),
        yaml_path,
        search_replace_dict,
    )

    secret_yml_path = eks_utils.get_aws_secret_yml_path()

    try:
        run("kubectl apply -f {}".format(yaml_path))

        port_to_forward = random.randint(49152, 65535)

        if eks_utils.is_service_running(selector_name):
            eks_utils.eks_forward_port_between_host_and_container(
                selector_name, port_to_forward, "8501"
            )

        inference_string = "'{\"instances\": [[1.0, 2.0, 5.0]]}'"
        assert dlc_test_utils.request_tensorflow_inference(
            model_name=model_name, port=port_to_forward, inference_string=inference_string
        )
    finally:
        run(f"kubectl delete deployment {selector_name}")
        run(f"kubectl delete service {selector_name}")


@pytest.mark.model("half_plus_two")
def test_eks_tensorflow_half_plus_two_inference(tensorflow_inference):
    __test_eks_tensorflow_half_plus_two_inference(tensorflow_inference)


@pytest.mark.model("half_plus_two")
def test_eks_tensorflow_half_plus_two_inference_graviton(tensorflow_inference_graviton):
    __test_eks_tensorflow_half_plus_two_inference(tensorflow_inference_graviton)


def __test_eks_tensorflow_half_plus_two_inference(tensorflow_inference):
    num_replicas = "1"

    rand_int = random.randint(4001, 6000)

    processor = "gpu" if "gpu" in tensorflow_inference else "cpu"

    model_name = f"saved_model_half_plus_two_{processor}"
    yaml_path = os.path.join(
        os.sep, "tmp", f"tensorflow_single_node_{processor}_inference_{rand_int}.yaml"
    )
    inference_service_name = selector_name = f"half-plus-two-service-{processor}-{rand_int}"
    model_base_path = get_eks_tensorflow_model_base_path(tensorflow_inference, model_name)
    command, args = get_tensorflow_command_args(tensorflow_inference, model_name, model_base_path)
    test_type = dlc_test_utils.get_eks_k8s_test_type_label(tensorflow_inference)
    search_replace_dict = {
        "<NUM_REPLICAS>": num_replicas,
        "<SELECTOR_NAME>": selector_name,
        "<INFERENCE_SERVICE_NAME>": inference_service_name,
        "<DOCKER_IMAGE_BUILD_ID>": tensorflow_inference,
        "<COMMAND>": command,
        "<ARGS>": args,
        "<TEST_TYPE>": test_type,
    }

    if processor == "gpu":
        search_replace_dict["<NUM_GPUS>"] = "1"

    eks_utils.write_eks_yaml_file_from_template(
        eks_utils.get_single_node_inference_template_path("tensorflow", processor),
        yaml_path,
        search_replace_dict,
    )

    try:
        run("kubectl apply -f {}".format(yaml_path))

        port_to_forward = random.randint(49152, 65535)

        if eks_utils.is_service_running(selector_name):
            eks_utils.eks_forward_port_between_host_and_container(
                selector_name, port_to_forward, "8500"
            )

        assert dlc_test_utils.request_tensorflow_inference(model_name=model_name, port=port_to_forward)
    finally:
        run(f"kubectl delete deployment {selector_name}")
        run(f"kubectl delete service {selector_name}")


@pytest.mark.skipif(
    not dlc_test_utils.is_nightly_context(), reason="Running additional model in nightly context only"
)
@pytest.mark.model("albert")
def test_eks_tensorflow_albert(tensorflow_inference):
    __test_eks_tensorflow_albert(tensorflow_inference)


@pytest.mark.model("albert")
def test_eks_tensorflow_albert_graviton(tensorflow_inference_graviton):
    __test_eks_tensorflow_albert(tensorflow_inference_graviton)


def __test_eks_tensorflow_albert(tensorflow_inference):
    num_replicas = "1"

    rand_int = random.randint(4001, 6000)

    processor = "gpu" if "gpu" in tensorflow_inference else "cpu"

    model_name = f"albert"
    yaml_path = os.path.join(
        os.sep, "tmp", f"tensorflow_single_node_{processor}_inference_{rand_int}.yaml"
    )
    inference_service_name = selector_name = f"albert-{processor}-{rand_int}"
    model_base_path = get_eks_tensorflow_model_base_path(tensorflow_inference, model_name)
    command, args = get_tensorflow_command_args(tensorflow_inference, model_name, model_base_path)
    test_type = dlc_test_utils.get_eks_k8s_test_type_label(tensorflow_inference)
    search_replace_dict = {
        "<NUM_REPLICAS>": num_replicas,
        "<SELECTOR_NAME>": selector_name,
        "<INFERENCE_SERVICE_NAME>": inference_service_name,
        "<DOCKER_IMAGE_BUILD_ID>": tensorflow_inference,
        "<COMMAND>": command,
        "<ARGS>": args,
        "<TEST_TYPE>": test_type,
    }

    if processor == "gpu":
        search_replace_dict["<NUM_GPUS>"] = "1"

    eks_utils.write_eks_yaml_file_from_template(
        eks_utils.get_single_node_inference_template_path("tensorflow", processor),
        yaml_path,
        search_replace_dict,
    )

    try:
        run("kubectl apply -f {}".format(yaml_path))

        port_to_forward = random.randint(49152, 65535)

        if eks_utils.is_service_running(selector_name):
            eks_utils.eks_forward_port_between_host_and_container(
                selector_name, port_to_forward, "8500"
            )

        assert dlc_test_utils.request_tensorflow_inference_nlp(
            model_name=model_name, port=port_to_forward
        )
    finally:
        run(f"kubectl delete deployment {selector_name}")
        run(f"kubectl delete service {selector_name}")


def get_tensorflow_command_args(image_uri, model_name, model_base_path):
    if "neuron" in image_uri:
        model_server = "/usr/local/bin/tensorflow_model_server_neuron"
        port = 8500
        rest_api_port = 8501
        s3_location = "s3://aws-dlc-sample-models"
    else:
        model_server = "/usr/bin/tensorflow_model_server"
        port = 8501
        rest_api_port = 8500
        s3_location = "s3://tensoflow-trained-models"
    if dlc_test_utils.is_below_framework_version("2.7", image_uri, "tensorflow"):
        command = f"[{model_server}]"
        args = f"['--port={port}', '--rest_api_port={rest_api_port}', '--model_name={model_name}', '--model_base_path={model_base_path}']"
    else:
        command = "['/bin/sh', '-c']"
        args = f"['mkdir -p /tensorflow_model && aws s3 sync {s3_location}/{model_name}/ /tensorflow_model/{model_name}/ && {model_server} --port={port} --rest_api_port={rest_api_port} --model_name={model_name} --model_base_path={model_base_path}']"
    return command, args


def get_eks_tensorflow_model_base_path(image_uri, model_name):
    """
    Retrieve model base path based on version of TensorFlow
    Requirement: Model defined in TENSORFLOW_MODELS_PATH should be hosted in S3 location for TF version less than 2.6.
                 Starting TF2.7, the models are referred locally as the support for S3 is moved to a separate python package `tensorflow-io`
    :param image_uri: ECR image URI
    :return: <string> model base path
    """
    if dlc_test_utils.is_below_framework_version("2.7", image_uri, "tensorflow"):
        if "neuron" in image_uri:
            s3_model_bucket = "s3://aws-dlc-sample-models"
        else:
            s3_model_bucket = dlc_test_utils.TENSORFLOW_MODELS_BUCKET
        model_base_path = f"{s3_model_bucket}/{model_name}"
    else:
        model_base_path = f"/tensorflow_model/{model_name}"
    return model_base_path
