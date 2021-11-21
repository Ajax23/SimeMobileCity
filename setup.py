import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simemobilecity",
    version="0.0.1",
    author="Hamzeh Kraus",
    author_email="hamzeh_kraus@web.de",
    description="Charging infrastructure simulation suite.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ajax23/SimeMobileCity",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=['osmnx', 'pandas', 'seaborn', 'scikit-learn'],
    include_package_data=True,
)
