from flask import Flask, request, render_template
import numpy as np
from PIL import Image
import base64
import io
from tensorflow import keras
import pandas as pd
import tensorflow as tf

app = Flask(__name__)

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)


@app.route('/')
def index():
    return render_template('index.html')

#console
@app.route('/get_image', methods=['GET', 'POST'])
def get_image():
    print('Incoming...')
    image_string = request.get_json()
    print('image recieved')
    print('.............................................................................')
    im = Image.open(io.BytesIO(base64.b64decode(image_string['jsontext'].split(',')[1])))
    im.save('test_image.png', 'PNG')
    
    digit, label = predict(im)
    label2 = devanagri_label(label)
    return label2, 200


keras.backend.clear_session()
model = keras.models.load_model('devanagari_minst.h5')


def predict(image):
    image = image.convert('RGB')
    image = image.resize((32,32))
    input_arr = np.array([keras.preprocessing.image.img_to_array(image)]) / 255
    input_arr = input_arr[:, :, :, :3]
    res2 = model.predict(input_arr)
    return res2, np.argmax(res2)


with open('class_labels.json', 'r') as f:
    import json

    class_labels = json.load(f)

# inverting class labels dict

inv_class_labels = {v: k for k, v in class_labels.items()}
labels = pd.read_csv('labels.csv')


def devanagri_label(label):
    devanagri = labels.at[int(inv_class_labels.get(label)), "Devanagari label"]
    return devanagri


if __name__ == '__main__':
    app.run(debug=True)
