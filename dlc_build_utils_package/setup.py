import os

from setuptools import find_packages, setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="dlc_build_utils",
    description="Library for all DLC Build Utilities",
    packages=find_packages(exclude=("test",)),
    install_requires=[
        "botocore",
        "boto3",
        "docker==4.2.0",
        "invoke",
        "packaging",
        "ruamel.yaml",
        "toml",
    ],
    extras_require={
        "test": ["mock", "pytest", "pytest-cov", "pytest-rerunfailures", "pytest-xdist"]
    },
)
