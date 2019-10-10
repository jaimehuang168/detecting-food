import sys
import os
from keras.preprocessing.image import ImageDataGenerator
from keras import optimizers
from keras.models import Sequential, Model
from keras.layers import Dropout, Flatten, Dense, Activation
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras import callbacks
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' ##Fixing some random errors!


##Folder structure
#   data/
#        train/
#            elephants/ ### 1024 pictures
#                elephant001.jpg
#                elephant002.jpg
#                ...
#            tigers/ ### 1024 pictures
#               tiger001.jpg
#               tiger002.jpg
#               ...
#        validation/
#            elephants/ ### 416 pictures
#               elephant001.jpg
#               elephant002.jpg
#               ...
#            tigers/ ### 416 pictures
#               tiger001.jpg
#               tiger002.jpg
#               ...


#Change epocs by DEV variable
DEV = True
argvs = sys.argv
argc = len(argvs)

if argc > 1 and (argvs[1] == "--development" or argvs[1] == "-d"):
  DEV = True
  print("WARN: DEV MODE TRUE, training only 5 epochs!")

if DEV:
  epochs = 5
else:
  epochs = 20

#Data folders
train_data_dir = './data/train'
validation_data_dir = './data/validation'

img_width, img_height = 150, 150 #Sizes to resize
nb_train_samples = 2048  #Total pictures for training
nb_validation_samples = 832 #Total pictures for validating
nb_filters1 = 32
nb_filters2 = 64
conv1_size = 3
conv2_size = 2
pool_size = 2
classes_num = 2 #How many clases you have
batch_size = 32
lr = 0.0004 #Learning rate, SLOW!

##Layer 1
model = Sequential()
model.add(Conv2D(nb_filters1, (conv1_size, conv1_size), padding="same", input_shape=(img_width, img_height, 3)))
model.add(Activation("relu"))
model.add(MaxPooling2D(pool_size=(pool_size, pool_size)))

##Layer 2
model.add(Conv2D(nb_filters2, (conv2_size, conv2_size), padding="same"))
model.add(Activation("relu"))
model.add(MaxPooling2D(pool_size=(pool_size, pool_size), data_format='channels_first'))

##Layer 3
model.add(Flatten())
model.add(Dense(256))
model.add(Activation("relu"))
model.add(Dropout(0.5))
model.add(Dense(classes_num, activation='softmax'))

#Complie model
model.compile(loss='categorical_crossentropy',
              optimizer=optimizers.RMSprop(lr=lr),
              metrics=['accuracy'])

#Prepare pictures for train
train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

#Prepare pictures for validation
test_datagen = ImageDataGenerator(
    rescale=1. / 255)

#Passing generator to traing
train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical')

#Passing generator to validation
validation_generator = test_datagen.flow_from_directory(
    validation_data_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical')

#LOGS
log_dir = './tf-log/'
tb_cb = callbacks.TensorBoard(log_dir=log_dir, histogram_freq=0)
cbks = [tb_cb]

#Start traning
model.fit_generator(
    train_generator,
    steps_per_epoch=nb_train_samples,
    epochs=epochs,
    validation_data=validation_generator,
    callbacks=cbks,
    validation_steps=nb_validation_samples)

#Save data in models folder (if not exist, create)
target_dir = './models/'
if not os.path.exists(target_dir):
  os.mkdir(target_dir)
model.save('./models/model.h5')
model.save_weights('./models/weights.h5')