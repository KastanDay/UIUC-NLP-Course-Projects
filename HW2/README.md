# Install Instructions

Use the provided `environment.yml` or `environment_detailed.yml` to install the required dependencies. These dependencies target x86 systems, but may work on arm or ppcle systems.

```python
conda env create -f environment.yml
```

# Run instructions

Run the code with a single command:

```python
python identification.py
```

This will result in an `output.json` in your current working directly with the final results formatted as requested. 

The code was run on an x86 system with 64GB of ram with a 1080TI (11GB) on Ubuntu 20.04 LTS and CUDA version 11.7, but using CUDA toolkit 11.6 installed via conda for PyTorch compatibility.

Thank you for reading!