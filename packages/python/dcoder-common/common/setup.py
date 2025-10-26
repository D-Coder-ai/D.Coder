from setuptools import setup, find_packages

setup(
    name="dcoder-common",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
    ]
)
