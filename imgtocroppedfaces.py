#rotate 6 degrees

import cv2
import os
import numpy as np
from overlayimgoncard import imagefromcropping

foldername = "imagestoprocess"
output_folder = "finalimages"

initial_expand_factor = 1.5
retry_expand_factor = 4


distance_threshold = 4  # Adjust this threshold as needed
count = 0
# Load the YOLOv3-based face detection model
yolo_net = cv2.dnn.readNet("model_data/yolov3-face.cfg", "model_data/yolov3-wider_16000.weights")

def calculate_center(box):
    startX, startY, endX, endY = box
    centerX = (startX + endX) // 2
    centerY = (startY + endY) // 2
    return centerX, centerY

def euclidean_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def cropnoface(image,name):
    global count
    global returnedimgs
    (h, w) = image.shape[:2]
    object_net = cv2.dnn.readNet("model_data/yolov4.cfg", "model_data/yolov3.weights")
    blob = cv2.dnn.blobFromImage(image, 1.0 / 255.0, (416, 416), swapRB=True, crop=False)
    object_net.setInput(blob)
    object_layer_names = object_net.getLayerNames()
    object_output_layer_names = [object_layer_names[i - 1] for i in object_net.getUnconnectedOutLayers()]
    obj_detections = object_net.forward(object_output_layer_names)

    obj_boxes = []
    obj_centers = []

    for detection in obj_detections:
            for obj in detection:
                scores = obj[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5 and class_id == 0:  # Assuming class_id 0 represents a face
                    center_x, center_y, width, height = (obj[:4] * np.array([w, h, w, h])).astype(int)
                    x = int(center_x - width / 2)
                    y = int(center_y - height / 2)
                    obj_boxes.append((x, y, x + width, y + height))
                    obj_centers.append(calculate_center((x, y, x + width, y + height)))

    if len(obj_centers) > 1:
        # Find the face closest to the center of the image
        image_center = (w // 2, h // 2)
        closest_obj_index = np.argmin([euclidean_distance(image_center, center) for center in obj_centers])

        # Use the closest face as a reference for cropping
        reference_obj_box = obj_boxes[closest_obj_index]

        min_x, min_y, max_x, max_y = reference_obj_box

        # Expand the bounding box while staying within the image boundaries
        expand_factor = initial_expand_factor  # Use the initial expand factor
        min_x = max(0, int(min_x - (max_x - min_x) * expand_factor))
        min_y = max(0, int(min_y - (max_y - min_y) * expand_factor))
        max_x = min(w, int(max_x + (max_x - min_x) * expand_factor))
        max_y = min(h, int(max_y + (max_y - min_y) * expand_factor))

        # Crop the region between faces
        cropped_obj_region = image[min_y:max_y, min_x:max_x]

        # Retry with a larger expand factor if the image is small
        if cropped_obj_region.size != 0 and cropped_obj_region.shape[0] < 100 and cropped_obj_region.shape[1] < 100:
            # Retry with a larger expand factor
            expand_factor = retry_expand_factor
            min_x = max(0, int(min_x - (max_x - min_x) * expand_factor))
            min_y = max(0, int(min_y - (max_y - min_y) * expand_factor))
            max_x = min(w, int(max_x + (max_x - min_x) * expand_factor))
            max_y = min(h, int(max_y + (max_y - min_y) * expand_factor))
            cropped_obj_region = image[min_y:max_y, min_x:max_x]

        # Check if the height is more than 50 pixels greater than the width
        if cropped_obj_region.shape[0] > cropped_obj_region.shape[1] + 50:
            new_height = cropped_obj_region.shape[1] + 50
            max_y = min(min_y + new_height, h)

        # Check if the width is bigger than the height and adjust if necessary
        if cropped_obj_region.shape[1] > cropped_obj_region.shape[0] + 50:
            new_width = cropped_obj_region.shape[0] + 50
            max_x = min(min_x + new_width, w)
        cropped_obj_region = image[min_y:max_y, min_x:max_x]
        cropped_obj_region = cv2.resize(cropped_obj_region, (142, 149), cv2.INTER_LANCZOS4)
    elif len(obj_boxes)==1:
        min_x, min_y, max_x, max_y = obj_boxes[0]
        expand_factor = initial_expand_factor
        min_x = max(0, int(min_x - (max_x - min_x) * expand_factor))
        min_y = max(0, int(min_y - (max_y - min_y) * expand_factor))
        max_x = min(w, int(max_x + (max_x - min_x) * expand_factor))
        max_y = min(h, int(max_y + (max_y - min_y) * expand_factor))
        cropped_obj_region = image[min_y:max_y, min_x:max_x]
        cropped_obj_region = cv2.resize(cropped_obj_region, (142, 149), cv2.INTER_LANCZOS4)
    else:
        cropped_obj_region = image
        cropped_obj_region = cv2.resize(cropped_obj_region, (142, 149), cv2.INTER_LANCZOS4)
        
    if cropped_obj_region.size != 0:
        cropped_obj_region
        return imagefromcropping(cropped_obj_region, name)
        #cv2.imwrite(os.path.join(output_folder, f'cropped_region_{count}.png'), cropped_obj_region)
    
# Set an initial and retry expand factor

def startalg(imglist, namelist):
    returnedimgs = []
    nameindex=0
    for img in imglist:
        #=img = cv2.imread(os.path.join(foldername, filename))
        if img is not None:
            (h, w) = img.shape[:2]

            # Create a blob from the image and perform forward pass with YOLO
            blob = cv2.dnn.blobFromImage(img, 1.0 / 255.0, (416, 416), swapRB=True, crop=False)
            yolo_net.setInput(blob)
            layer_names = yolo_net.getLayerNames()
            output_layer_indices = yolo_net.getUnconnectedOutLayers()

            # Initialize an empty list to store the output layer names
            output_layer_names = []

            # Iterate through the output layer indices and get the corresponding layer names
            output_layer_names = [layer_names[i - 1] for i in output_layer_indices]
            detections = yolo_net.forward(output_layer_names)

            # List to store the bounding boxes and centers of all detected faces
            face_boxes = []
            face_centers = []

            for detection in detections:
                for obj in detection:
                    scores = obj[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]

                    if confidence > 0.5 and class_id == 0:  # Assuming class_id 0 represents a face
                        center_x, center_y, width, height = (obj[:4] * np.array([w, h, w, h])).astype(int)
                        x = int(center_x - width / 2)
                        y = int(center_y - height / 2)
                        face_boxes.append((x, y, x + width, y + height))
                        face_centers.append(calculate_center((x, y, x + width, y + height)))

            if not face_centers:
                returnedimgs.append(cropnoface(img,namelist[nameindex]))
                nameindex+=1
                continue

            # Filter out faces that are too far from each other
            if len(face_centers) > 1:
                # Find the face closest to the center of the image
                image_center = (w // 2, h // 2)
                closest_face_index = np.argmin([euclidean_distance(image_center, center) for center in face_centers])

                # Use the closest face as a reference for cropping
                reference_face_box = face_boxes[closest_face_index]

                min_x, min_y, max_x, max_y = reference_face_box

                # Expand the bounding box while staying within the image boundaries
                expand_factor = initial_expand_factor  # Use the initial expand factor
                min_x = max(0, int(min_x - (max_x - min_x) * expand_factor))
                min_y = max(0, int(min_y - (max_y - min_y) * expand_factor))
                max_x = min(w, int(max_x + (max_x - min_x) * expand_factor))
                max_y = min(h, int(max_y + (max_y - min_y) * expand_factor))

                # Crop the region between faces
                cropped_face_region = img[min_y:max_y, min_x:max_x]

                # Retry with a larger expand factor if the image is small
                if cropped_face_region.size != 0 and cropped_face_region.shape[0] < 100 and cropped_face_region.shape[1] < 100:
                    # Retry with a larger expand factor
                    expand_factor = retry_expand_factor
                    min_x = max(0, int(min_x - (max_x - min_x) * expand_factor))
                    min_y = max(0, int(min_y - (max_y - min_y) * expand_factor))
                    max_x = min(w, int(max_x + (max_x - min_x) * expand_factor))
                    max_y = min(h, int(max_y + (max_y - min_y) * expand_factor))
                    cropped_face_region = img[min_y:max_y, min_x:max_x]

                # Check if the height is more than 50 pixels greater than the width
                if cropped_face_region.shape[0] > cropped_face_region.shape[1] + 50:
                    new_height = cropped_face_region.shape[1] + 50
                    max_y = min(min_y + new_height, h)

                # Check if the width is bigger than the height and adjust if necessary
                if cropped_face_region.shape[1] > cropped_face_region.shape[0] + 50:
                    new_width = cropped_face_region.shape[0] + 50
                    max_x = min(min_x + new_width, w)
                cropped_face_region = img[min_y:max_y, min_x:max_x]
                cropped_face_region = cv2.resize(cropped_face_region, (142, 149), cv2.INTER_LANCZOS4)
            else:
                min_x, min_y, max_x, max_y = face_boxes[0]
                expand_factor = initial_expand_factor
                min_x = max(0, int(min_x - (max_x - min_x) * expand_factor))
                min_y = max(0, int(min_y - (max_y - min_y) * expand_factor))
                max_x = min(w, int(max_x + (max_x - min_x) * expand_factor))
                max_y = min(h, int(max_y + (max_y - min_y) * expand_factor))
                cropped_face_region = img[min_y:max_y, min_x:max_x]
                cropped_face_region = cv2.resize(cropped_face_region, (142, 149), cv2.INTER_LANCZOS4)
            if cropped_face_region.size != 0:
                cropped_face_region
                returnedimgs.append(imagefromcropping(cropped_face_region, namelist[nameindex]))
                #cv2.imwrite(os.path.join(output_folder, f'cropped_region_{count}.png'), cropped_face_region)
                nameindex += 1
    return returnedimgs

