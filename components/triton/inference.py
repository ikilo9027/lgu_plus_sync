import sys
import cv2

import tritonclient.grpc as grpcclient

from components.triton.utils import preprocess, postprocess


class ModelInferencer:
    def __init__(self, url: str = "localhost:8001"):
        try:
            self.triton_client = grpcclient.InferenceServerClient(url)
        except Exception as e:
            print("channel creation failed: " + str(e))
            sys.exit()

    def infer(self, input_data):
        input0_data = preprocess(input_data)

        h, w = input0_data.shape[-2:]

        inputs = []
        outputs = []

        inputs.append(grpcclient.InferInput("input", input0_data.shape, "FP32"))
        inputs[0].set_data_from_numpy(input0_data)

        outputs.append(grpcclient.InferRequestedOutput("output"))

        # Inference
        results = self.triton_client.infer(
            model_name="SR_e", inputs=inputs, outputs=outputs
        )

        # Get the output arrays from the results
        output0_data = results.as_numpy("output")
        output0_data = postprocess(output0_data, h, w)

        return output0_data
