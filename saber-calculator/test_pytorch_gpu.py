import torch

def test_gpu():
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("Number of GPUs:", torch.cuda.device_count())
        print("Current device:", torch.cuda.current_device())
        print("Device name:", torch.cuda.get_device_name(torch.cuda.current_device()))
        # Simple tensor operation on GPU
        x = torch.rand(5, 5).cuda()
        y = torch.rand(5, 5).cuda()
        z = x + y
        print("Tensor operation successful on GPU:", z)
    else:
        print("No CUDA GPU detected.")

if __name__ == "__main__":
    test_gpu()
