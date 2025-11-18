from deepface import DeepFace
import matplotlib.pyplot as plt
import os

# 保存人脸部分
def extract_and_save_face(image_path, output_dir):
    result = DeepFace.extract_faces(img_path=image_path, align=True)
    if result:
        face_image = result[0]['face']
        original_filename = os.path.basename(image_path)
        output_path = os.path.join(output_dir, original_filename)
        plt.imsave(output_path, face_image)
        return output_path
    return None

output_dir = './outImages'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 获取两张人脸图
extracted_face1_path = extract_and_save_face(img1_original_path, output_dir)
extracted_face2_path = extract_and_save_face(img2_original_path, output_dir)

if extracted_face1_path and extracted_face2_path:
    # 判断两张人脸是不是同一个人
    result_verify = DeepFace.verify(img1_path=extracted_face1_path,
                                     img2_path=extracted_face2_path,
                                     model_name='SFace',
                                     detector_backend='retinaface')
    # 展示结果，两个人不是同一个人
    print(result_verify)
else:
    print("Could not extract faces from one or both images.")