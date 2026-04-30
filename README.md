# versaparse

A native, lightweight Python parser for AMETEK/Princeton Applied Research VersaStudio (`.par`) files. 

This package allows you to directly read proprietary `.par` files, automatically extracting the experiment metadata and converting the raw electrochemical data into easy-to-use Pandas DataFrames for quick analysis and plotting.

---

## Installation

You can install `versaparse` directly from this GitHub repository using `pip`. 

**Important:** It is highly recommended (and required on modern Macs) to install this package inside a Python Virtual Environment to prevent conflicts with your system's default Python.
```bash
pip install "git+https://github.com/zhenggroup/versaparse.git"
```

## Tutorial & Examples
The package revolves around a single, easy-to-use class called VersaData. Here is how to use it.
1. Loading a File
To parse a file, simply pass the file path to VersaData.
```python
import versaparse

# Load the experiment data
experiment = versaparse.VersaData('my_experiment.par')
print("File loaded successfully!")
```
2. Accessing Metadata
VersaStudio saves a lot of background information (like the instrument used, scan rates, and acquisition time). versaparse organizes this into a dictionary called metadata.
```python
# Check when the experiment was run
date_run = experiment.metadata['Experiment']['DateAcquired']
time_run = experiment.metadata['Experiment']['TimeAcquired']
print(f"Experiment run on {date_run} at {time_run}")

# Check the instrument serial number
print("Instrument SN:", experiment.metadata['Instrument']['SN'])
```
3. Finding and Extracting Data Segments
Electrochemical experiments are often broken into multiple "Segments" (e.g., Segment 0 might be Open Circuit, Segment 1 might be EIS, Segment 2 might be Chronoamperometry).
You can ask the package which segments exist, and extract the one you want as a Pandas DataFrame.
```python
# Find out what segments are inside this file
available_segments = experiment.get_segments_list()
print("Segments found:", available_segments) 
# Example Output: [0, 1, 2]

# Extract the data for Segment 2
df = experiment.get_segment(2)

# Look at the first 5 rows of the data
print(df[['Elapsed Time(s)', 'E(V)', 'I(A)']].head())
```

## Full Plotting Example
Here is a complete, copy-pasteable script that loads a file and plots the Current vs. Time for a specific segment. This is perfect for running in a Jupyter Notebook.
```python
import versaparse
import matplotlib.pyplot as plt

# 1. Load the data
experiment = versaparse.VersaData('my_experiment.par')

# 2. Extract Segment 2
df_seg2 = experiment.get_segment(2)

# 3. Create the plot
plt.figure(figsize=(8, 5))
plt.plot(
    df_seg2['Elapsed Time(s)'], 
    df_seg2['I(A)'], 
    color='blue', 
    linewidth=2,
    label='Raw Data'
)

# 4. Format the plot
plt.title('Chronoamperometry (Segment 2)', fontsize=14)
plt.xlabel('Elapsed Time (s)', fontsize=12)
plt.ylabel('Current (A)', fontsize=12)
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0)) # Scientific notation for current
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# 5. Show the plot
plt.tight_layout()
plt.show()
```

## Troubleshooting Common Errors
•	error: externally-managed-environment
This happens on modern Macs and Linux machines if you try to use pip outside of a virtual environment. Run python3 -m venv .venv and source .venv/bin/activate, then try installing again.
•	zsh: unknown file attribute: h or zsh: no matches found
Your Mac terminal is misinterpreting the URL. Make sure you put quotation marks around the git URL: pip install "git+https://...".
•	ModuleNotFoundError: No module named 'versaparse' in Jupyter
If you are using VS Code or Jupyter Notebooks, make sure you have selected your .venv environment as the active "Kernel" in the top right corner of your notebook window.
