import os
import shutil
import zipfile
import yaml
from google.colab import drive

drive.mount('/content/drive')

master_dir = '/content/master_dataset'
splits = ['train', 'val']

classes = {
    'potholes': {'zip': '/content/drive/MyDrive/Pothole Detection.v9i.yolov8 (1).zip', 'id': 0},
    'water_leak': {'zip': '/content/drive/MyDrive/pipeline_leakage1.v2i.yolov8.zip', 'id': 1},
    'garbage': {'zip': '/content/drive/MyDrive/Garbage.v3i.yolov8.zip', 'id': 3},
}

for split in splits:
    os.makedirs(f'{master_dir}/{split}/images', exist_ok=True)
    os.makedirs(f'{master_dir}/{split}/labels', exist_ok=True)
for class_name, info in classes.items():
    temp_dir = f'/content/temp_{class_name}'

    with zipfile.ZipFile(info['zip'], 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    new_id = str(info['id'])

    for split in splits:
        img_folder = os.path.join(temp_dir, split, 'images')
        lbl_folder = os.path.join(temp_dir, split, 'labels')

        if not os.path.exists(img_folder):
            print(f"   -> Warning: {img_folder} not found. Skipping {split} for {class_name}.")
            continue

        max_images_allowed = 3000 if split == 'train' else 500
        copied_count = 0

        for img_file in os.listdir(img_folder):
            if copied_count >= max_images_allowed:
                break

            if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            base_name = os.path.splitext(img_file)[0]
            txt_file = base_name + '.txt'

            old_txt_path = os.path.join(lbl_folder, txt_file)

            if os.path.exists(old_txt_path):
                new_img_name = f"{class_name}_{img_file}"
                new_txt_name = f"{class_name}_{txt_file}"
                shutil.copy(os.path.join(img_folder, img_file),
                            os.path.join(master_dir, split, 'images', new_img_name))

                new_txt_path = os.path.join(master_dir, split, 'labels', new_txt_name)
                with open(old_txt_path, 'r') as f_in, open(new_txt_path, 'w') as f_out:
                    for line in f_in:
                        parts = line.strip().split()
                        if parts:
                            parts[0] = new_id 
                            f_out.write(" ".join(parts) + "\n")

                copied_count += 1

        print(f"   -> Copied {copied_count} files for {split}.")

    shutil.rmtree(temp_dir)

val_images_path = os.path.join(master_dir, 'val', 'images')
if not os.listdir(val_images_path):
    print("No validation images were found from the original dataset")

    train_images_path = os.path.join(master_dir, 'train', 'images')
    train_labels_path = os.path.join(master_dir, 'train', 'labels')
    val_labels_path = os.path.join(master_dir, 'val', 'labels')

    all_train_images = [f for f in os.listdir(train_images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    num_total_train_images = len(all_train_images)

    if num_total_train_images == 0:
        print("Error: No training images available to create a validation set.")
    else:
        import random
        random.seed(42)

        num_val_to_move = int(num_total_train_images * 0.15)
        if num_val_to_move == 0 and num_total_train_images > 0:
            num_val_to_move = 1


        val_image_names = random.sample(all_train_images, num_val_to_move)

        for img_file_name in val_image_names:
            base_name = os.path.splitext(img_file_name)[0]
            label_file_name = base_name + '.txt'

            shutil.move(os.path.join(train_images_path, img_file_name),
                        os.path.join(val_images_path, img_file_name))
            shutil.move(os.path.join(train_labels_path, label_file_name),
                        os.path.join(val_labels_path, label_file_name))

        print(f"   ✅ {num_val_to_move} images and labels moved to validation set.")

yaml_content = {
    'train': f'{master_dir}/train/images',
    'val': f'{master_dir}/val/images',
    'nc': 3, # We now have 3 total classes
    'names': ['pothole', 'water_leak', 'garbage']
}

with open(f'{master_dir}/data.yaml', 'w') as f:
    yaml.dump(yaml_content, f, default_flow_style=False)

