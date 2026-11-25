
# PyTorch MNIST Digit Classifier

A beginner-friendly computer vision project that trains a neural network to recognize handwritten digits (0–9) using PyTorch. This project is designed as a first step into deep learning and computer vision, with clean, readable code and clear explanations.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)


---

## Overview

This project implements a simple fully connected neural network (and an optional CNN variant) to classify images from the **MNIST** dataset. It covers the complete deep learning workflow:

- Loading and preprocessing data
- Defining a model in PyTorch
- Writing a training loop from scratch
- Evaluating on a test set
- Visualizing predictions

**Expected results:** ~97–98% test accuracy with the simple MLP, and ~99% with the CNN variant.


---

## Requirements

- Python 3.8 or higher
- PyTorch 2.0+
- torchvision
- matplotlib

Install all dependencies with:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install torch torchvision matplotlib
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/vigneshwararaj175/pytorch-mnist-beginner.git
cd pytorch-mnist-beginner
```

### 2. Run the training script

```bash
python train.py
```

The script will:

1. Automatically download the MNIST dataset (if not already present)
2. Train the model for 5 epochs
3. Print training and validation loss/accuracy per epoch
4. Display a sample prediction with matplotlib

### 3. Expected output

```
Using device: cuda
Epoch 1/5 | Train Loss: 0.3124 Acc: 0.9102 | Val Loss: 0.1456 Acc: 0.9581
Epoch 2/5 | Train Loss: 0.1421 Acc: 0.9587 | Val Loss: 0.1012 Acc: 0.9694
Epoch 3/5 | Train Loss: 0.1043 Acc: 0.9689 | Val Loss: 0.0854 Acc: 0.9731
Epoch 4/5 | Train Loss: 0.0856 Acc: 0.9734 | Val Loss: 0.0791 Acc: 0.9762
Epoch 5/5 | Train Loss: 0.0732 Acc: 0.9772 | Val Loss: 0.0712 Acc: 0.9785
Test accuracy: 0.9785
```

---

## How It Works

### The Model

A simple multi-layer perceptron (MLP):

```
Input (28×28 image)
   ↓ Flatten → 784 vector
   ↓ Linear (784 → 128)
   ↓ ReLU
   ↓ Dropout (0.2)
   ↓ Linear (128 → 10)
Output (10 class scores)
```

A convolutional variant (`CNN`) is also included in `model.py` for better accuracy.

### The Training Loop

Every PyTorch training step follows these five lines:

```python
optimizer.zero_grad()              # clear old gradients
outputs = model(images)            # forward pass
loss = criterion(outputs, labels)  # compute loss
loss.backward()                    # backpropagation
optimizer.step()                   # update weights
```

### Key Concepts Covered

| Concept | Where it appears |
|---|---|
| Data loading | `DataLoader`, `transforms` |
| Model definition | `nn.Module`, `forward()` |
| Loss function | `nn.CrossEntropyLoss` |
| Optimizer | `optim.Adam` |
| Device management | `.to(device)` |
| Evaluation mode | `model.eval()`, `torch.no_grad()` |

---

## Customization

### Change the number of epochs

```python
epochs = 10  # in train.py
```

### Switch to the CNN model

In `train.py`, replace:

```python
model = SimpleNN().to(device)
```

with:

```python
from model import CNN
model = CNN().to(device)
```

### Adjust hyperparameters

```python
batch_size = 64
learning_rate = 1e-3
```

---

## Saving and Loading the Model

To save a trained model:

```python
torch.save(model.state_dict(), 'mnist_model.pt')
```

To load it later:

```python
model = SimpleNN()
model.load_state_dict(torch.load('mnist_model.pt'))
model.eval()
```

> **Note:** Model files (`.pt`, `.pth`) are excluded via `.gitignore`. To share a trained model, upload it to a cloud drive (Google Drive, Hugging Face Hub) and link it in this README.

---

## Roadmap / Next Steps

- [ ] Add training curve plots (loss/accuracy vs. epoch)
- [ ] Implement a CNN for higher accuracy (~99%)
- [ ] Add CIFAR-10 support (color images, 10 classes)
- [ ] Build a webcam-based live digit recognizer with OpenCV
- [ ] Add data augmentation for robustness

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Expected 4D input` error | Use `nn.Flatten()` or `unsqueeze(1)` before `Conv2d` |
| `size mismatch` in `Linear` | Print `x.shape` inside `forward()` |
| `CUDA out of memory` | Reduce `batch_size` |
| Accuracy stuck at 10% | Check `optimizer.zero_grad()`, learning rate, and labels |
| Model predicts badly at test time | Forget `model.eval()`? Dropout stays active |

---

## References

- [MNIST Dataset](http://yann.lecun.com/exdb/mnist/)
- [PyTorch Official Tutorials](https://pytorch.org/tutorials/)
- [Deep Learning with PyTorch (free book)](https://pytorch.org/deep-learning-with-pytorch)

---
