import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="dlc_test_utils",
    description="Library for all DLC Test Utilities",
    packages=find_packages(exclude=("test",)),
    install_requires=[
        "botocore",
        "boto3",
        "docker==4.2.0",
        "fabric",
        "invoke",
        "packaging",
        "retrying",
        "ruamel.yaml",
        "tenacity",
        "toml",
    ],
    extras_require={
        "test": ["mock", "pytest", "pytest-cov", "pytest-rerunfailures", "pytest-xdist"]
    },
)
