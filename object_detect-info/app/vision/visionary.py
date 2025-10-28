# from ultralytics import YOLO
# from app.settings import settings

# class Visionary:
#     def __init__(self):
#         self.device = settings.device
#         print(f"Running on {self.device}")
#         self.model = YOLO(settings.model_path)

#     def detect(self, image):
#         results = self.model(image, device=self.device)
#         print(f"Detection results: {results}")
#         # get detected class names
#         if results:
#             return [results[0].names[int(cls)] for cls in results[0].boxes.cls]
#         return []
#     def get_object_details(detected_classes, object_map):
#         """
#         detected_classes: list of class names from YOLO
#         object_map: your predefined JSON mapping (optional)
#         """
#         details = []
#         for cls in detected_classes:
#             if cls in object_map:
#                 details.append(object_map[cls])
#             else:
#                 # dynamic fallback for unknown objects
#                 details.append({
#                     "name": cls,
#                     "description": f"{cls} detected. No predefined description available.",
#                     "question": f"Tell us more about this {cls}."
#                 })
#         return details
from ultralytics import YOLO
from app.settings import settings

class Visionary:
    def __init__(self):
        self.device = settings.device
        print(f"Running on {self.device}")
        self.model = YOLO(settings.model_path)

    def detect(self, image):
        """
        Returns list of class names detected in the image
        """
        results = self.model(image, device=self.device)
        print(f"Detection results: {results}")
        if results:
            return [results[0].names[int(cls)] for cls in results[0].boxes.cls]
        return []

    def detect_with_coordinates(self, image):
        """
        Returns list of dicts with bounding box coordinates and class names
        Format: [{"name": "person", "x1":.., "y1":.., "x2":.., "y2":..}, ...]
        """
        results = self.model(image, device=self.device)
        detections = []
        if results and results[0].boxes is not None:
            for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
                x1, y1, x2, y2 = map(int, box)
                label = results[0].names[int(cls)]
                detections.append({
                    "name": label,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                })
        return detections

    @staticmethod
    def get_object_details(detected_classes, object_map):
        """
        detected_classes: list of class names from YOLO
        object_map: your predefined JSON mapping
        """
        details = []
        for cls in detected_classes:
            if cls in object_map:
                details.append(object_map[cls])
            else:
                details.append({
                    "name": cls,
                    "description": f"{cls} detected. No predefined description available.",
                    "question": f"Tell us more about this {cls}."
                })
        return details

