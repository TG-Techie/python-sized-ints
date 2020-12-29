import setuptools
import sized_ints

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sized-ints",
    version=sized_ints.__version__,
    author="TG-Techie (Jonah Y-M)",
    author_email="tgtechie01@gmail.com",
    description="convenient add sized ints to python (u8, i8, int64_t, etc)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TG-Techie/python-sized-ints",
    packages=['sized_ints'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
