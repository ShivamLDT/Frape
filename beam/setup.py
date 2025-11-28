"""
Setup script for Beam package
"""
from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import sys
import platform


class PostInstallCommand(install):
    """Post-installation command to install beam in WSL on Windows"""
    
    def run(self):
        # Run the standard install
        install.run(self)
        
        # On Windows, try to install in WSL automatically
        if platform.system() == "Windows":
            try:
                from beam.install_wsl import install_beam_in_wsl
                install_beam_in_wsl()
            except Exception as e:
                # Don't fail the installation if WSL setup fails
                print(f"\n⚠️  Could not auto-install in WSL: {e}")
                print("   You can install manually in WSL if needed.")


# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="beam-cli",
    version="1.0.0",
    description="Beam - A SaaS-ready wrapper for Frappe Bench",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Beam Team",
    author_email="team@beam.example.com",
    url="https://github.com/yourorg/beam",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "frappe-bench>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "beam=beam.cli:main",
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
    ],
    keywords="frappe bench saas deployment management",
)

