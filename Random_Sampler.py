#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 16:06:16 2024

@author: danielmendoza
"""
'''Random Sampler'''

import os
import random
import shutil

def random_sample_images(source_folder, destination_folder, n):
    # Create destination folder if it doesn't exist
    os.makedirs(destination_folder, exist_ok=True)

    # List all files in the source folder
    all_files = os.listdir(source_folder)

    # Filter to keep only image files (optional, based on file extensions)
    image_files = [f for f in all_files if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

    # Check if n is not more than the available images
    if n > len(image_files):
        print(f"Requested {n} images, but only {len(image_files)} are available.")
        n = len(image_files)

    # Randomly select n files
    selected_files = random.sample(image_files, n)

    # Copy each selected file to the destination folder
    for file_name in selected_files:
        src_path = os.path.join(source_folder, file_name)
        dst_path = os.path.join(destination_folder, file_name)
        shutil.copy(src_path, dst_path)  # Copy file to new location

    print(f"Copied {n} images to {destination_folder}.")

# Example usage
source_folder = '/Users/danielmendoza/Desktop/Fall2024/Capstone/NIS/NIS-NEU-data-prac-240930/withD'
destination_folder = '/Users/danielmendoza/Desktop/Fall2024/Capstone/NIS/NIS-NEU-data-prac-240930/D_nonD/D_Samples'
n = 400  # Number of images to sample

random_sample_images(source_folder, destination_folder, n)
