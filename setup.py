import setuptools

VERSION = "0.1"

DESCRIPTION = "Generic binary serialization/deserialization handler"
LONG_DESCRIPTION = open('README.md').read()

setuptools.setup(
    name="BinSerialize",
    version=VERSION,
    author="monkeyman192",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=setuptools.find_packages(),
    license="MIT",
    platform="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)