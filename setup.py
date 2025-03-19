from setuptools import setup, find_packages

setup(
    name="Reddit-Fetch",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
        "rich",
        "argparse"
    ],
    entry_points={
        "console_scripts": [
            "reddit-fetcher=reddit_fetch.main:cli_entry"
        ]
    },
    include_package_data=True,  # ✅ Ensure all necessary files are included
    author="Akash Pandey",
    author_email="pandeyak12@outlook.com",
    description="A tool to fetch and process Reddit saved posts.",
    long_description="Reddit-Fetch allows users to retrieve their saved posts from Reddit, format them into JSON or HTML, and store them locally.",
    long_description_content_type="text/markdown",
    url="https://github.com/akashpandey/Reddit-Fetch",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
