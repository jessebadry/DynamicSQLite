import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DynamicSQLite-JesseBadry",
    version="0.0.1",
    author="Jesse Badry",
    author_email="author@example.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jessebadry/DynamicSQLite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License ",
        "Operating System :: OS Independent",
    ],
)
