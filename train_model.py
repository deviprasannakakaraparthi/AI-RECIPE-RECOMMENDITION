import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
import json
import os

# Configuration
CSV_PATH = '/Users/jarnox/FOOD/recipes_cleaned.csv'
TFLITE_MODEL_PATH = '/Users/jarnox/FOOD/recipe_model.tflite'
METADATA_PATH = '/Users/jarnox/FOOD/metadata.json'

# 1. Load and Clean Dataset
print("Loading dataset...")
try:
    # Read only first 5000 rows to avoid malformed data issues later in the large file
    df = pd.read_csv(CSV_PATH, header=None, names=['id', 'title', 'ingredients_list', 'instructions', 'slug', 'ingredients_raw'], on_bad_lines='skip', nrows=5000)
    print(f"Loaded {len(df)} rows.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    exit(1)




# Basic cleaning
df = df.dropna(subset=['title', 'ingredients_list'])
# Filter out rows where title is too short or ingredients_list is too short (likely errors)
df = df[df['title'].str.len() > 3]
df = df[df['ingredients_list'].str.len() > 10]

# Limit to 5000 for training efficiency in this environment
df = df.head(5000)

print(f"Processing {len(df)} recipes...")

# 2. Preprocessing
def clean_ingredients(ing_str):
    try:
        # Remove brackets and quotes from string representation of list
        cleaned = str(ing_str).replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        # Remove extra spaces and make lowercase
        return cleaned.lower().strip()
    except:
        return ""

df['ingredients_clean'] = df['ingredients_list'].apply(clean_ingredients)

tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['ingredients_clean'])
total_words = len(tokenizer.word_index) + 1

input_sequences = tokenizer.texts_to_sequences(df['ingredients_clean'])
max_sequence_len = min(max([len(x) for x in input_sequences]), 50)
input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

# Labels (Index mapping)
recipe_list = df['title'].tolist() # Use the list directly to maintain order
recipe_to_idx = {recipe: i for i, recipe in enumerate(recipe_list)}
df['label'] = df['title'].map(recipe_to_idx)
total_labels = len(recipe_list)
labels = tf.keras.utils.to_categorical(df['label'], num_classes=total_labels)

# 3. Build Model
print("Building model...")
model = Sequential([
    Embedding(total_words, 128, input_length=max_sequence_len),
    LSTM(256, return_sequences=False),
    Dropout(0.3),
    Dense(512, activation='relu'),
    Dense(total_labels, activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 4. Train Model
# 50 epochs is enough for a baseline on this small set
print("Starting training...")
model.fit(input_sequences, labels, epochs=50, batch_size=64, verbose=1)

# 5. Save Model and TFLite Conversion
print("Exporting model to TFLite...")
model.export('recipe_model_export') 

converter = tf.lite.TFLiteConverter.from_saved_model('recipe_model_export')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
# Important for mobile compatibility with some ops
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
    tf.lite.OpsSet.SELECT_TF_OPS
]
tflite_model = converter.convert()

with open(TFLITE_MODEL_PATH, 'wb') as f:
    f.write(tflite_model)

# 6. Export Metadata
# Serialize word_index and labels
metadata = {
    'word_index': tokenizer.word_index,
    'labels': {str(i): recipe for i, recipe in enumerate(recipe_list)},
    'max_len': max_sequence_len
}

with open(METADATA_PATH, 'w') as f:
    json.dump(metadata, f)

print(f"Model training complete.")
print(f"Files generated: {TFLITE_MODEL_PATH}, {METADATA_PATH}")
