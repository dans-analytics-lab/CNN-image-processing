#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 20:18:22 2024

@author: danielmendoza
"""

''' CNN for Image Classification: Binary D/non-D Classification '''
'''Use this script as a base to train a neural network on cell images'''

'''Run on GPUs''' #Checking how many GPUs are available to train model faster. 
import tensorflow as tf
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))


# Importing dependencies
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import label_binarize
from tensorflow.keras.callbacks import ReduceLROnPlateau



# Define the directory containing your images (all in one folder)
dataset_dir = '/Users/danielmendoza/Desktop/Fall2024/Capstone/NIS/NIS-NEU-data-prac-240930/D_nonD'
 
# ImageDataGenerator with validation split (e.g., 80% training, 20% validation)
datagen = ImageDataGenerator(
    rescale=1./255,          # Rescale pixel values to [0, 1]
    validation_split=0.25,   # Reserve 20% of data for validation
    rotation_range=10,       # Randomly rotate images
    width_shift_range=0.05,   # Horizontal shifts
    height_shift_range=0.05,  # Vertical shifts
    shear_range=0.05,         # Shear transformation
    zoom_range=0.05,          # Random zoom
    horizontal_flip=True,    # Randomly flip images horizontally
    fill_mode='nearest'      # Fill mode for pixels outside input boundaries
)


# Image preprocessing using ImageDataGenerator
img_size = (244, 244)
batch_size = 64

# Augmentation and rescaling for training set
train_datagen = ImageDataGenerator(rescale=1./255, rotation_range=10, width_shift_range=0.1, height_shift_range=0.1, zoom_range=0.05, horizontal_flip=True)
test_datagen = ImageDataGenerator(rescale=1./255)


# Data Generators
# Load training data from the directory (80% training, 20% validation)
train_generator = datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary',  # Use 'categorical' if there are multiple classes
    subset='training' ,
    shuffle= True         # Training data
)
 
validation_generator = datagen.flow_from_directory(
    dataset_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary',  # Use 'categorical' if there are multiple classes
    subset='validation',
    shuffle=False        # Validation data
)

''' Defining F1 Score metric'''
from tensorflow.keras import backend as K

# Define a custom F1 score function
def f1_score(y_true, y_pred):
    y_pred = K.round(y_pred)  # Round predictions to 0 or 1
    tp = K.sum(K.cast(y_true * y_pred, 'float'), axis=0)
    fp = K.sum(K.cast((1 - y_true) * y_pred, 'float'), axis=0)
    fn = K.sum(K.cast(y_true * (1 - y_pred), 'float'), axis=0)

    precision = tp / (tp + fp + K.epsilon())
    recall = tp / (tp + fn + K.epsilon())
    f1 = 2 * precision * recall / (precision + recall + K.epsilon())
    return f1

'''Defining focal loss'''

def focal_loss(gamma=2.0, alpha=0.25):
    """
    Focal Loss for binary classification.
    
    Parameters:
    - gamma: focuses on hard-to-classify cases (higher = more focus on hard examples)
    - alpha: adjusts the balance between classes (higher alpha for minority class)
    
    Returns:
    - A loss function that can be used in model.compile(loss=...)
    """
    def focal_loss_fixed(y_true, y_pred):
        # Clip predictions to prevent log(0) errors
        y_pred = K.clip(y_pred, 1e-7, 1 - 1e-7)
        
        # Compute cross-entropy loss for binary classification
        cross_entropy = -y_true * K.log(y_pred) - (1 - y_true) * K.log(1 - y_pred)
        
        # Apply focal loss formula
        weight = alpha * y_true * K.pow(1 - y_pred, gamma) + (1 - alpha) * (1 - y_true) * K.pow(y_pred, gamma)
        focal_loss_value = weight * cross_entropy
        
        # Return mean focal loss
        return K.mean(focal_loss_value)
    
    return focal_loss_fixed


'''# Build CNN model'''
model = tf.keras.models.Sequential([
    
    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(244, 244, 3)),
    tf.keras.layers.MaxPooling2D(2, 2),
    tf.keras.layers.Dropout(0.5),
    
    #tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
    #tf.keras.layers.MaxPooling2D(2, 2),
    #tf.keras.layers.Dropout(0.5),
    
    #tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    #tf.keras.layers.MaxPooling2D(2, 2),
    #tf.keras.layers.Dropout(0.5),
    
    #tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
    #tf.keras.layers.MaxPooling2D(2, 2),
    #tf.keras.layers.Dropout(0.5),
    
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Compile the model
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005), loss='binary_crossentropy', metrics=['accuracy', f1_score])

# Model summary
model.summary()

# Learning rate scheduler
lr_scheduler = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-6, verbose=1)

# Train model
history = model.fit(
    train_generator,
    epochs=10,
    validation_data=validation_generator,
    callbacks=[lr_scheduler]
)

''' Do not use this for now
# Train the model
history = model.fit(
    train_generator,
    #steps_per_epoch=train_generator.samples // batch_size,
    epochs=10,
    validation_data=validation_generator,
    #validation_steps=validation_generator.samples // batch_size
)
'''

# Learning Curves for Accuracy and Loss
def plot_learning_curves(history):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    
    epochs_range = range(len(acc))

    plt.figure(figsize=(12, 6))
    
    # Accuracy Plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')

    # Loss Plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')

    plt.tight_layout()
    plt.show()

# Plot learning curves
plot_learning_curves(history)

# Evaluate model on test set
validation_loss, test_acc = model.evaluate(validation_generator)
print(f'Test Accuracy: {test_acc * 100:.2f}%')

# Predicting on the validation set
validation_predictions = model.predict(validation_generator)
validation_predictions_labels = (validation_predictions > 0.55).astype(int).flatten()
true_labels = validation_generator.classes

# Classification report
class_report = classification_report(true_labels, validation_predictions_labels, target_names=['D', 'non_D'])
print("Classification Report:")
print(class_report)

# Confusion matrix
conf_matrix = confusion_matrix(true_labels, validation_predictions_labels)

# Plot Confusion Matrix
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, cmap="Blues", fmt="d", xticklabels=['D', 'Non_D'], yticklabels=['D', 'non_D'])
plt.title("Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.show()





