#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  9 14:48:04 2024

@author: danielmendoza
"""

import os
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array, load_img
import numpy as np
from PIL import UnidentifiedImageError

# Path to the minority class images
input_folder = '/Users/danielmendoza/Desktop/Fall2024/Capstone/NIS/NIS-NEU-data-prac-240930/D_nonD/withoutD/Originals'
output_folder = '/Users/danielmendoza/Desktop/Fall2024/Capstone/NIS/NIS-NEU-data-prac-240930/D_nonD/withoutD/Augmented'
#os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist

# Set up the data generator with transformations
datagen = ImageDataGenerator(
    rotation_range=180,      # Random rotations between 0 and 40 degrees
    width_shift_range=0.5,  # Random horizontal shifts
    height_shift_range=0.5, # Random vertical shifts
    shear_range=0.5,        # Shear transformations
    zoom_range=0.5,         # Zooming in/out
    horizontal_flip=True,   # Randomly flip images
    fill_mode='constant',  # Try 'constant', 'reflect', or 'wrap'
    cval=0                 # Only relevant for 'constant' mode; fills empty areas with black
)

# Number of synthetic images to generate per original image
images_per_image = 7

# Loop through each image in the input folder
for image_name in os.listdir(input_folder):
    # Check if the file is an image by its extension
    if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue  # Skip non-image files

    img_path = os.path.join(input_folder, image_name)
    try:
        img = load_img(img_path)  # Load the image
        x = img_to_array(img)     # Convert the image to a numpy array
        x = np.expand_dims(x, axis=0)  # Add batch dimension

        # Generate new images
        i = 0
        for batch in datagen.flow(x, batch_size=1, save_to_dir=output_folder,
                                  save_prefix='aug', save_format='jpg'):
            i += 1
            if i >= images_per_image:
                break  # Stop once we reach the desired number of augmentations per image

    except UnidentifiedImageError:
        print(f"Skipping file {image_name} as it could not be identified as an image.")
        

        
        