python3 tools/predict_openvino.py --model_path ./onnx-xml/model_best.pth \
     --input_folder ./input --output_folder ./output  \
     --thre 0.7 \
     --onnx True \
     --inference openvino #pytorch #onnxrt #openvino