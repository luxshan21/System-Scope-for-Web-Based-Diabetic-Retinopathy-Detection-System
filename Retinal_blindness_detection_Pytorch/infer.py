import matplotlib.pyplot as plt
import numpy as np
from model import Model

file = r"C:\Users\luxsh\Desktop\Retinal_blindness_detection_Pytorch\Retinal_blindness_detection_Pytorch\sampleimages\eye2.png"
classes = ['No DR', 'Mild', 'Moderate', 'Severe', 'Proliferative DR']

model = Model(num_classes=5)
model.load_model(r"C:\Users\luxsh\Desktop\Retinal_blindness_detection_Pytorch\Retinal_blindness_detection_Pytorch\classifier.pt\classifier.pt")
value, out_img = model.test_with_single_image(file, classes)

print("Value:", value)
print(classes[value])
plt.imshow(np.array(out_img))
plt.show()