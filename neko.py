from tensorflow.keras.applications.vgg16 import VGG16
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Model

# VGG16モデルの読み込み（事前学習済み、出力層は除外）
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(150, 150, 3))

# 新しい出力層の追加
x = base_model.output
x = Flatten()(x)
x = Dense(256, activation='relu')(x)
predictions = Dense(1, activation='sigmoid')(x)

# 新しいモデルの作成
model = Model(inputs=base_model.input, outputs=predictions)

# モデルのコンパイル
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# モデルの保存
model.save('cat_detector.h5')
