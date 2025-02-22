import subprocess
import os

directory_path = './'
python ="python3"

# List all files and directories in the specified directory
files_and_dirs = os.listdir(directory_path)
files_and_dirs = sorted(files_and_dirs)

for f in files_and_dirs:
    if f.endswith('.py') and not f.endswith('Assignment_2_Grading.py'):
        print("---------------------")
        print(f)
        print(f"{python}  {f} karate.gml --components 2 --plot C")
        subprocess.run([python, f, "karate.gml", "--components",  "2", "--plot", "C"])

        print(f"{python}  {f} karate.gml --plot N")
        subprocess.run([python, f, "karate.gml",  "--plot", "N"])

        print(f"{python}  {f} homophily.gml --plot P --verify_homophily")
        subprocess.run([python, f, 'homophily.gml', '--plot', 'P', '--verify_homophily'])

        print(f"{python}  {f} balanced_graph.gml --plot P --verify_balanced_graph")
        subprocess.run([python, f, 'balanced_graph.gml', '--plot', 'P', '--verify_balanced_graph'])

        print(f"{python}  {f} imbalanced_graph.gml --plot P --verify_balanced_graph")
        subprocess.run([python, f, 'imbalanced_graph.gml', '--plot', 'P', '--verify_balanced_graph'])