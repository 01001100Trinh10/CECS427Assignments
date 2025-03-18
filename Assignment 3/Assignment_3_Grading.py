import subprocess
import os


directory_path = './'

# List all files and directories in the specified directory
files_and_dirs = os.listdir(directory_path)
files_and_dirs = sorted(files_and_dirs)

for f in files_and_dirs:
    if f.endswith('.py') and not f.endswith('Assignment_3_Grading.py'):
        print("---------------------")
        print(f"python3 {f} traffic.gml 4 0 3 --plot")
        subprocess.run(["python3", f,  "traffic.gml", "4", "0", "3", "--plot"])
        print(f"python3 {f} traffic2.gml 4 0 5 --plot")
        subprocess.run(["python3", f,  "traffic2.gml", "4", "0", "5", "--plot"])

