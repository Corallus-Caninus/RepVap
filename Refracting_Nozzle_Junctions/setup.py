import setuptools

# TODO: remove this and extract junctions up a level. 
#       Python package structure is... weird. 
#       Need to button this up for pub release 

setuptools.setup(
    name="RefractingNozzleJunctions", 
    version="0.0.1",
    author="Josh Ward",
    author_email="ward.joshua92@yahoo.com",
    description="A small example package",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    # classifiers=[
    #     " Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ],
    python_requires='>=3.6',
)