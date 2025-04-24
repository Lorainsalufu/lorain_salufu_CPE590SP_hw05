# Lorain_Salufu_CPE590-ST_hw05.
To run the webapp, make sure to make a directory to store the following data tree:
~/(any_folder_name)
  -mnistapp.py
  -MNIST_digit_classifier.onnx
  -static
    -css
      -styles.css
    -js
      -script.js
  -templates
    -index.html

Next, open any powershell able to run python, such as Anaconda Prompt



Move to the directory into the (any_folder_name) using "cd any_folder_name"
Run "-n pythonenv python=3.10 -y " and "uv pythonenv" to create and then open a virtual python environment
Install dependencies using:
"pip install flask numpy onnxruntime pandas scikit-learn gunicorn flask_wtf werkzeug wtforms pillow python-magic-bin."
Finally, the webpage can be open through "python app.py."

URL of python notebook used for the first part of the homework: 
https://colab.research.google.com/drive/1uZlQMeK8Ee3EV04ZycGQN0zK0t0Nln5x?usp=shari
