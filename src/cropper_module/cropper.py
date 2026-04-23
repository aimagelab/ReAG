import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

from cropper_module.extract_entity import find_visual_entity


class Cropper:
    def __init__(self, args):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.processor = AutoProcessor.from_pretrained(args.cropper_model_name)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(args.cropper_model_name).to(self.device)

        print(f'Model loaded on {self.device}')

    @torch.inference_mode()
    def detect_and_crop(self, image: Image.Image, query: str, box_threshold=0.4, text_threshold=0.3):
        entity: str = "a " + find_visual_entity(query)['root'].lower() + "."
        inputs = self.processor(images=image, text=[entity], return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        results = self.processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=[image.size[::-1]]
        )
        if len(results) == 0:
            return image, entity  # No detections, return original image
        result = results[0] # result["boxes"], result["scores"], result["labels"]

        if len(result["boxes"]) > 0:
            box = result["boxes"][0].tolist()  # Get the first detected box
            cropped_image = image.crop(box)
        else:
            cropped_image = image
        return cropped_image, entity

