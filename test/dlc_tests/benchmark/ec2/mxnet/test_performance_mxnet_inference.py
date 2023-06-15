import os

import pytest

from dlc_test_utils import (
    CONTAINER_TESTS_PREFIX,
    get_framework_and_version_from_tag,
    UL20_CPU_ARM64_US_WEST_2,
)
from dlc_test_utils.ec2 import (
    execute_ec2_inference_performance_test,
    post_process_mxnet_ec2_performance,
)
from dlc_test_utils.benchmark_metrics import (
    MXNET_INFERENCE_CPU_IMAGENET_THRESHOLD,
    MXNET_INFERENCE_GPU_IMAGENET_THRESHOLD,
    get_threshold_for_image,
)

MX_PERFORMANCE_INFERENCE_GPU_CMD = os.path.join(
    CONTAINER_TESTS_PREFIX, "benchmark", "run_mxnet_inference_performance_gpu"
)
MX_PERFORMANCE_INFERENCE_CPU_CMD = os.path.join(
    CONTAINER_TESTS_PREFIX, "benchmark", "run_mxnet_inference_performance_cpu"
)

MX_EC2_GPU_INSTANCE_TYPE = "p3.16xlarge"
MX_EC2_CPU_INSTANCE_TYPE = "c5.18xlarge"
MX_EC2_GRAVITON_INSTANCE_TYPE = "c6g.4xlarge"


@pytest.mark.integration("imagenet dataset")
@pytest.mark.model("resnet50_v2")
@pytest.mark.parametrize("ec2_instance_type", [MX_EC2_GPU_INSTANCE_TYPE], indirect=True)
def test_performance_ec2_mxnet_inference_gpu(mxnet_inference, ec2_connection, gpu_only, py3_only):
    _, framework_version = get_framework_and_version_from_tag(mxnet_inference)
    threshold = get_threshold_for_image(framework_version, MXNET_INFERENCE_GPU_IMAGENET_THRESHOLD)
    execute_ec2_inference_performance_test(
        ec2_connection,
        mxnet_inference,
        MX_PERFORMANCE_INFERENCE_GPU_CMD,
        post_process=post_process_mxnet_ec2_performance,
        data_source="imagenet",
        threshold={"Throughput": threshold},
    )


@pytest.mark.integration("imagenet dataset")
@pytest.mark.model("resnet50_v2")
@pytest.mark.parametrize("ec2_instance_type", [MX_EC2_CPU_INSTANCE_TYPE], indirect=True)
def test_performance_ec2_mxnet_inference_cpu(mxnet_inference, ec2_connection, cpu_only, py3_only):
    _, framework_version = get_framework_and_version_from_tag(mxnet_inference)
    threshold = get_threshold_for_image(framework_version, MXNET_INFERENCE_CPU_IMAGENET_THRESHOLD)
    execute_ec2_inference_performance_test(
        ec2_connection,
        mxnet_inference,
        MX_PERFORMANCE_INFERENCE_CPU_CMD,
        post_process=post_process_mxnet_ec2_performance,
        data_source="imagenet",
        threshold={"Throughput": threshold},
    )


# TODO: Enable when releasing MXNet Graviton images
@pytest.mark.skip(reason="Enable when releasing MXNet Graviton Images")
@pytest.mark.integration("imagenet dataset")
@pytest.mark.model("resnet50_v2")
@pytest.mark.parametrize("ec2_instance_type", [MX_EC2_GRAVITON_INSTANCE_TYPE], indirect=True)
@pytest.mark.parametrize("ec2_instance_ami", [UL20_CPU_ARM64_US_WEST_2], indirect=True)
def test_performance_ec2_mxnet_inference_graviton_cpu(
    mxnet_inference_graviton, ec2_connection, cpu_only
):
    _, framework_version = get_framework_and_version_from_tag(mxnet_inference_graviton)
    threshold = get_threshold_for_image(framework_version, MXNET_INFERENCE_CPU_IMAGENET_THRESHOLD)
    execute_ec2_inference_performance_test(
        ec2_connection,
        mxnet_inference_graviton,
        MX_PERFORMANCE_INFERENCE_CPU_CMD,
        post_process=post_process_mxnet_ec2_performance,
        data_source="imagenet",
        threshold={"Throughput": threshold},
    )
