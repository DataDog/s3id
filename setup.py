"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="s3id",
    version="0.1.4",
    description="A library to calculate, match, and return details about S3 Object ETags.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DataDog/s3id",
    author="Christopher Harris",
    author_email="cnharris@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="AWS, S3, ETag, MD5, match, chunk, multi-part, upload",
    packages=find_packages(include=["s3id"], exclude=["tests*"]),
    python_requires=">=3.6, <4",
    project_urls={
        "Bug Reports": "https://github.com/DataDog/s3id/issues",
        "Source": "https://github.com/DataDog/s3id/",
    },
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
