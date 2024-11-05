from setuptools import setup, find_packages


setup(
    name="pdf_manager",
    version="0.0.1",  # Don't forget to change the `pyproject.toml` file
    author="Zaid Shoufan",
    description=(
        "`pdf_manager` is a python PDF manager that does it all."),
    packages=find_packages(),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=[
        "pillow",
        "pymupdf",
        "pypdf",
        ])
