import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

dependencies = ['numpy',
                'scipy',
                'pandas',
                'ply',
                'matplotlib']

setuptools.setup(
    name="pyxpp",
    version="0.1.1",
    author="Mark Olenik",
    author_email="mark.olenik@gmail.com",
    description="An XPP Python wrapper powered by PLY",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markolenik/PyXPP",
    packages=setuptools.find_packages(),
    install_requires=dependencies,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
    ),
)
