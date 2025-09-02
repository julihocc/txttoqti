from setuptools import setup, find_packages

setup(
    name="txttoqti",
    version="1.0.0",
    author="Educational Tools Team",
    author_email="team@example.com",
    description="Universal converter from text-based question banks to Canvas LMS QTI packages",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/txttoqti",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # Add your runtime dependencies here
    ],
    extras_require={
        "dev": [
            # Add your development dependencies here
        ],
    },
    entry_points={
        "console_scripts": [
            "txttoqti=txttoqti.cli:main",  # Assuming you have a main function in cli.py
        ],
    },
)