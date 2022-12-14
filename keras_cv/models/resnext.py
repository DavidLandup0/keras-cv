# Copyright 2022 The KerasCV Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tensorflow as tf


class GroupConv2D(tf.keras.layers.Layer):
    def __init__(self, input_channels, output_channels, groups, kernel_size, strides=(1, 1), padding='valid', **kwargs):
        super(GroupConv2D, self).__init__()
        self.kernel_size = kernel_size
        self.strides = strides
        self.padding = padding
        self.group_in_num = input_channels // groups
        self.group_out_num = output_channels // groups
        self.conv_list = []
        for i in range(self.groups):
            self.conv_list.append(tf.keras.layers.Conv2D(filters=self.group_out_num, kernel_size=kernel_size, strides=strides,
                                                         padding=padding,
                                                         **kwargs))

    def call(self, inputs, **kwargs):
        feature_map_list = []
        for i in range(self.groups):
            x_i = self.conv_list[i](inputs[:, :, :, i*self.group_in_num: (i + 1) * self.group_in_num])
            feature_map_list.append(x_i)
        out = tf.concat(feature_map_list, axis=-1)
        return out                                                     


def ConvBlock(inputs, filters, kernel_size, strides, padding):
    x = tf.keras.layers.Conv2D(filters=filters,kernel_size=kernel_size,strides=strides,padding=padding)(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.nn.relu(x)
    return x

def ResNeXt_BottleNeck(inputs, filters, strides, groups):
    x = ConvBlock(inputs, filters, (1,1), 1, "same")
    x = GroupConv2D(input_channels=filters,output_channels=filters, kernel_size=(3, 3),
                    strides=strides,padding="same",groups=groups)(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.nn.relu(x)
    x = ConvBlock(x, 2 * filters, (1,1), 1, "same")
    shortcut = ConvBlock(inputs, filters = 2 * filters, kernel_size=(1,1), strides=strides, padding="same")
    outputs = tf.keras.layers.add([x, shortcut])
    return outputs
