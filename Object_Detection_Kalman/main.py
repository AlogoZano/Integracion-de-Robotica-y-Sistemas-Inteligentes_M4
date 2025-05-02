"""main: concatenación de YOLO y SORT."""
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import Sort
import os
from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np


class ObjectDetection:
    def __init__(self, capture, result):
        """Constructor de detección"""
        self.capture = capture
        self.result = result
        self.model = self.load_model()
        self.CLASS_NAMES_DICT = self.model.model.names

    def load_model(self):
        model = YOLO("yolov8l.pt")
        model.fuse()

        return model

    def predict(self, img):
        results = self.model(img, stream=True)
        return results

    def plot_boxes(self, results, img, detections):
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                # Classname
                cls = int(box.cls[0])
                currentClass = self.CLASS_NAMES_DICT[cls]

                # Confodence score
                conf = math.ceil(box.conf[0] * 100) / 100

                if conf > 0.5:
                    currentArray = np.array([x1, y1, x2, y2, conf])
                    detections = np.vstack((detections, currentArray))

        return detections, img

    def track_detect(self, detections, tracker, img):
        resultTracker = tracker.update(detections)

        for res in resultTracker:
            x1, y1, x2, y2, id = res
            x1, y1, x2, y2, id = int(x1), int(y1), int(x2), int(y2), int(id)
            w, h = x2 - x1, y2 - y1

            cvzone.putTextRect(
                img, f"ID: {id}", 
                (x1, y1), 
                scale=1, 
                thickness=1, 
                colorR=(0, 0, 255)
            )
            cvzone.cornerRect(img, 
                              (x1, y1, w, h), 
                              l=9, 
                              rt=1, 
                              colorR=(255, 0, 255))

            cx, cy = x1 + w // 2, y1 + h // 2
            # centroid = (cx, cy)
            cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        return img

    def __call__(self):
        cap = cv2.VideoCapture(self.capture)
        ret, frame = cap.read()
        assert cap.isOpened()

        result_path = os.path.join(self.result, "results_caballos_2.avi")

        codec = cv2.VideoWriter_fourcc(*"XVID")
        vid_fps = int(cap.get(cv2.CAP_PROP_FPS))
        vid_width, vid_height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )
        out = cv2.VideoWriter(result_path, 
                              codec, 
                              vid_fps, 
                              (vid_width, vid_height))

        tracker = Sort(max_age=60, min_hits=1, iou_threshold=0.1)

        if not os.path.exists(self.result):
            os.makedirs(self.result)
            print("Result folder created successfully")
        else:
            print("Result folder already exist")

        while ret:
            ret, img = cap.read()
            if not ret:
                break

            detections = np.empty((0, 5))
            results = self.predict(img)
            detections, frames = self.plot_boxes(results, img, detections)
            detect_frame = self.track_detect(detections, tracker, frames)

            out.write(detect_frame)
            cv2.imshow("Image", detect_frame)
            if cv2.waitKey(1) == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


detector = ObjectDetection(capture="caballos_2.mp4", result="result")
detector()
