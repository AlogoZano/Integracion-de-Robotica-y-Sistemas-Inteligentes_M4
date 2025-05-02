from ultralytics import YOLO
import cv2
import cvzone
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort


class ObjectDetectionDeepSORT:
    def __init__(self, video_path, result_dir):
        self.cap = cv2.VideoCapture(video_path)
        self.model = YOLO("yolov8l.pt")
        self.model.fuse()
        self.class_names = self.model.model.names

        self.tracker = DeepSort(
            max_age=60,
            n_init=5,
            nms_max_overlap=0.6,
            max_cosine_distance=0.3,
            nn_budget=100,
        )

        self.result_path = result_dir + "/results_caballos_2_2.avi"
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.writer = cv2.VideoWriter(
            self.result_path, cv2.VideoWriter_fourcc(*"XVID"), fps, (width, height)
        )

    def process(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            results = self.model(frame, conf=0.5, iou=0.7)[0]
            detections = []

            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if conf < 0.5 or self.class_names[cls_id] != "horse":
                    continue

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, cls_id))

            tracks = self.tracker.update_tracks(detections, frame=frame)

            for track in tracks:
                if not track.is_confirmed():
                    continue

                track_id = track.track_id
                ltrb = track.to_ltrb()
                x1, y1, x2, y2 = map(int, ltrb)
                w, h = x2 - x1, y2 - y1

                cvzone.putTextRect(
                    frame,
                    f"ID: {track_id}",
                    (x1, y1),
                    scale=1,
                    thickness=1,
                    colorR=(0, 255, 0),
                )
                cvzone.cornerRect(
                    frame, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255)
                )
                cv2.circle(frame, (x1 + w // 2, y1 + h // 2), 5, (0, 255, 0), -1)

            self.writer.write(frame)
            cv2.imshow("DeepSORT Tracking", frame)
            if cv2.waitKey(1) == ord("q"):
                break

        self.cap.release()
        self.writer.release()
        cv2.destroyAllWindows()


# Uso
tracker = ObjectDetectionDeepSORT("caballos_2.mp4", "result")
tracker.process()
