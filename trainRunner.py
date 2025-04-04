import subprocess
import os
from tqdm import tqdm

dataset_path = 'dataset/DTU'
output_path = 'output/date'
depth_ratio = 0
r_value = 2
lambda_dist = 0

scans = [
    "scan24", "scan37", "scan40", "scan55", "scan63", "scan65",
    "scan69", "scan83", "scan97", "scan105", "scan106",
    "scan110", "scan114", "scan118", "scan122"
]

scans_test = ["scan122"]
#testoli = ["scan24", "scan37", "scan40", "scan55", "scan63"]

#testoli = ["scan69", "scan83", "scan97", "scan105", "scan106"]
testoli = ["scan24", "scan37", "scan40"]

#testoli = ["scan110", "scan114", "scan118", "scan122"]

for scan in tqdm(testoli, desc="Training DTU dataset"):
    scan_path = os.path.join(dataset_path, scan)
    output_folder = os.path.join(output_path, scan)

    command = [
        "python", "train_quantitize_kmeans.py",
        "-s", scan_path,
        "-m", output_folder,
        "-r", str(r_value)]
        #"--dynamic_resolution"
        #]
        #"--depth_ratio", str(depth_ratio),
        #"--lambda_dist", str(lambda_dist)
    #]

    print(f"\nTraining {scan}...")
    subprocess.run(command)

print("Training completed")