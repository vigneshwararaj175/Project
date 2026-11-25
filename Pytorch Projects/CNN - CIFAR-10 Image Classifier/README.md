# CIFAR-10 Image Classifier with PyTorch CNN

A clean, beginner-friendly implementation of a Convolutional Neural Network (CNN) in PyTorch for classifying color images from the CIFAR-10 dataset. This project is designed as a stepping stone from MNIST to real-world computer vision, covering convolutional layers, batch normalization, data augmentation, and learning rate scheduling.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)
![Accuracy](https://img.shields.io/badge/Test%20Accuracy-85--88%25-brightgreen)


---


## Overview

This project trains a CNN from scratch to classify **32×32 color images** into one of 10 CIFAR-10 categories:

> ✈️ Airplane · 🚗 Automobile · 🐦 Bird · 🐱 Cat · 🦌 Deer · 🐶 Dog · 🐸 Frog · 🐴 Horse · 🚢 Ship · 🚚 Truck

Unlike the grayscale MNIST digits, CIFAR-10 forces a model to learn **color, texture, and complex spatial patterns** — making it the standard benchmark for validating a CNN pipeline.

**Key features:**

- Custom CNN with 3 convolutional blocks (32 → 64 → 128 filters)
- Batch normalization and dropout for stable training
- Data augmentation (random horizontal flip + random crop)
- Learning rate scheduling with `StepLR`
- Training curve and prediction grid visualization
- Fully reproducible, single-script workflow

---


## Requirements

- Python 3.8+
- PyTorch 2.0+
- torchvision
- matplotlib
- numpy

Install with:


```bash
pip install torch torchvision matplotlib numpy
```

> A CUDA-capable GPU is **strongly recommended** (training drops from ~25 min on CPU to ~3 min on GPU).

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/vigneshwararaj175/cifar10-cnn.git
cd cifar10-cnn
```

### 2. Install dependencies

```bash
pip install torch torchvision matplotlib numpy
```

### 3. Train the model

```bash
python train_cifar.py
```

The script will:

1. Download CIFAR-10 to `./data/` (once)
2. Train the CNN for 15 epochs
3. Print train/validation loss and accuracy per epoch
4. Save `training_curves.png` and `predictions.png`
5. Save the trained weights to `cifar10_cnn.pt`

### 4. Expected output

```
Using device: cuda
Epoch 1/15  | Train Loss 1.6234 Acc 0.4012 | Val Loss 1.2451 Acc 0.5618
Epoch 2/15  | Train Loss 1.2034 Acc 0.5748 | Val Loss 0.9812 Acc 0.6584
...
Epoch 15/15 | Train Loss 0.3741 Acc 0.8723 | Val Loss 0.4523 Acc 0.8641
Model saved to cifar10_cnn.pt
```

---

## Model Architecture

The network is intentionally simple — three convolutional blocks, followed by a small classifier head.

```
Input: (3, 32, 32)
  ↓ Conv2d(3 → 32, 3×3) → BatchNorm → ReLU → MaxPool(2)
  (32, 16, 16)
  ↓ Conv2d(32 → 64, 3×3) → BatchNorm → ReLU → MaxPool(2)
  (64, 8, 8)
  ↓ Conv2d(64 → 128, 3×3) → BatchNorm → ReLU → MaxPool(2)
  (128, 4, 4)
  ↓ Flatten → Linear(2048 → 256) → ReLU → Dropout(0.4) → Linear(256 → 10)
Output: 10 class logits
```

| Layer | Purpose |
|---|---|
| `Conv2d` | Learns spatial features (edges → textures → shapes) |
| `BatchNorm2d` | Stabilizes and accelerates training |
| `MaxPool2d` | Downsamples feature maps; adds translation invariance |
| `Dropout(0.4)` | Prevents overfitting in the classifier head |
| `CrossEntropyLoss` | Combines `LogSoftmax` + `NLLLoss` |

> ⚠️ **Important:** PyTorch uses **channels-first** `(N, C, H, W)`. After the final pooling layer, the feature map is `128 × 4 × 4`, so the `Linear` input size is `128 × 4 × 4 = 2048`. Changing any conv block requires recalculating this.

---

## Training Pipeline

**Data augmentation** (train only):

```python
transforms.RandomHorizontalFlip()
transforms.RandomCrop(32, padding=4)
transforms.ToTensor()
transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
```

**Optimization:**

| Setting | Value |
|---|---|
| Optimizer | Adam |
| Learning rate | 1e-3 |
| LR scheduler | `StepLR(step_size=10, gamma=0.5)` |
| Batch size | 64 |
| Epochs | 15 |

**The five-line training step** (PyTorch idiom):

```python
optimizer.zero_grad()              # clear old gradients
outputs = model(images)            # forward pass
loss = criterion(outputs, labels)  # compute loss
loss.backward()                    # backpropagation
optimizer.step()                   # update weights
```

---

## Results

| Model | Data Augmentation | Test Accuracy |
|---|---|---|
| MLP (flatten + dense) | ❌ | ~55–60% |
| **This CNN (15 epochs)** | ✅ | **~85–88%** |
| CNN + 30 epochs | ✅ | ~90–92% |
| Pretrained ResNet-18 (transfer learning) | ✅ | ~94–95% |

Results vary slightly due to random seeds and hardware. The test set is the official CIFAR-10 test split (10,000 images).

---

## Customization

**Change the number of epochs:**
```python
epochs = 30  # in train_cifar.py
```

**Adjust hyperparameters:**
```python
batch_size = 128
learning_rate = 3e-4
```

**Disable augmentation** (to compare performance):
```python
train_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean, std),
])
```

**Try a different optimizer:**
```python
optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9, weight_decay=5e-4)
```

---

## Saving and Loading

The script auto-saves weights to `cifar10_cnn.pt`:

```python
torch.save(model.state_dict(), 'cifar10_cnn.pt')
```

To load for inference:

```python
from train_cifar import CNN, class_names

model = CNN()
model.load_state_dict(torch.load('cifar10_cnn.pt'))
model.eval()

# predictions = model(image_tensor).argmax(1)
```




## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `mat1 and mat2 shapes cannot be multiplied` | Wrong `Linear` input size | Print `x.shape` after `features` in `forward()` |
| Test accuracy stuck at ~10% | Broken training loop or LR | Check `optimizer.zero_grad()`, try LR `3e-4` |
| Test accuracy stuck at ~50% | Overfitting, or missing augmentation | Ensure `train_transform` has flip/crop |
| Val accuracy decreases over epochs | Overfitting | Increase dropout, add early stopping |
| Training is very slow | `num_workers=0` on Linux/Mac | Set `num_workers=2` |
| Image colors look wrong when visualized | Forgot to un-normalize | Multiply by `std`, add `mean` before `imshow` |
| `CUDA out of memory` | Batch size too large | Reduce `batch_size` to 32 |

---

## References

- [CIFAR-10 Dataset (Krizhevsky, 2009)](https://www.cs.toronto.edu/~kriz/cifar.html)
- [PyTorch Official Tutorials](https://pytorch.org/tutorials/)
- [Deep Learning with PyTorch (free book)](https://pytorch.org/deep-learning-with-pytorch)
- [CS231n: Convolutional Neural Networks for Visual Recognition](https://cs231n.stanford.edu/)

---
