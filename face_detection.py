import cv2
import mediapipe as mp

def detect_face(image):
    """
    Detects faces in the provided image and returns the original image with bounding boxes around the faces
    and the cropped faces.

    Args:
        image (numpy.ndarray): The input image in BGR format.

    Returns:
        Tuple[numpy.ndarray, numpy.ndarray]: A tuple containing the original image with bounding boxes around
        the faces and the cropped faces.
    """
    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    # Convert the image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform face detection
    results = face_detection.process(image_rgb)

    # If faces are detected
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = image.shape
            x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

            # Draw bounding box
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Crop the detected face
            cropped_face = image[y:y+h, x:x+w]

            # Convert the cropped face to RGB for facial landmark detection
            cropped_face_rgb = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)

            # Initialize MediaPipe Face Mesh for facial landmark detection
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

            # Perform facial landmark detection on the cropped face
            landmarks = face_mesh.process(cropped_face_rgb)
            if landmarks.multi_face_landmarks:
                for face_landmarks in landmarks.multi_face_landmarks:
                    for landmark in face_landmarks.landmark:
                        x_lm, y_lm = int(landmark.x * w), int(landmark.y * h)
                        cv2.circle(cropped_face, (x_lm, y_lm), 2, (255, 0, 0), -1)
    
    return image, cropped_face




