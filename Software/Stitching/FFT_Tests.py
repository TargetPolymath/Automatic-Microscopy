"""
Copyright 2020 Zachary J. Allen

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
"""

# FFT tests

import cv2
import numpy as np



A_test = cv2.imread("Test_A.png", 0)

img_f1 = np.fft.fft2(A_test)

img_f2 = np.fft.fftshift(img_f1)

img_f2_real = img_f2.real

img_f2_imag = img_f2.imag


img_f2_real_scaled = cv2.resize(img_f2_real, (round(img_f2_real.shape[0] * 0.2), round(img_f2_real.shape[1] * 0.2)))

img_f2_real_scaled_log = np.log(1+np.abs(img_f2_real_scaled))*10

cv2.imwrite("FFT_1x.png", img_f2_real_scaled_log);


# cv2.waitKey(0);
# cv2.destroyAllWindows();


A_test_4x = cv2.resize(A_test, (round(A_test.shape[1] * 4), round(A_test.shape[0] * 4)))[A_test.shape[0]:2*A_test.shape[0], A_test.shape[1]:2*A_test.shape[1]]

cv2.imwrite("4x.png", A_test_4x)

img_f1_4x = np.fft.fft2(A_test_4x)

img_f2_4x = np.fft.fftshift(img_f1_4x)

img_f2_real_4x = img_f2_4x.real

img_f2_imag_4x = img_f2_4x.imag


img_f2_real_scaled_4x = cv2.resize(img_f2_real_4x, (round(img_f2_real_4x.shape[0] * 0.2), round(img_f2_real_4x.shape[1] * 0.2)))

img_f2_real_scaled_4x_log = np.log(1+np.abs(img_f2_real_scaled_4x))*10

cv2.imwrite("FFT_4x.png", img_f2_real_scaled_4x_log);


