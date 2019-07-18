import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="figure-eight-client",
    version="1.0.5",
    author="Nathan Evans",
    author_email="evans.nathan.j@gmail.com",
    description="Simple client for the Figure Eight API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/de1ux/figure-eight-python-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',

    ]
)