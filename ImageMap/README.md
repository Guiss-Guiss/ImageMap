# 🎨 ImageMap

A Python application for image processing that preserves visual vibrancy by avoiding color averaging, featuring a graphical interface and multilingual support.

![Languages](https://img.shields.io/badge/Languages-FR%20|%20EN%20|%20DE%20|%20ES-blue)
![Python](https://img.shields.io/badge/Python-3.11.8-green)
![GPU](https://img.shields.io/badge/GPU-Compatible-brightgreen)
![No Color Averaging](https://img.shields.io/badge/No%20Color%20Averaging-✓-orange)

## 🎯 Core Innovation

ImageMap revolutionizes image resizing by eliminating the common problem of color averaging. Traditional resizing algorithms create new, averaged colors that tend toward grey, resulting in flat, lifeless images. ImageMap instead:

- ✅ Never averages colors, preventing the "washed-out" effect
- ✅ Maintains the original image's vibrant contrasts
- ✅ Preserves the crispness of color transitions
- ✅ Keeps small details sharp and visible

## 🔍 The Problem with Traditional Resizing

Traditional resizing methods:
- Create new, averaged colors that didn't exist in the original
- Tend toward grey due to mathematical averaging
- Lose subtle contrasts and details
- Result in flatter, less vibrant images

## ✨ The Solution

ImageMap's approach:
- Uses only original colors from the source image
- Prevents the grey-shift effect of color averaging
- Maintains the original color dynamics
- Preserves the visual punch of the original image

## 🛠️ Technical Advantages

- **Smart Color Selection**: Instead of averaging, selects the most appropriate original color
- **Contrast Preservation**: Maintains the visual separation between different colored areas
- **Detail Retention**: Keeps small elements visually distinct
- **Anti-Greying**: Prevents the dulling effect common in traditional resizing

## 🚀 Features

- 🎨 Zero color averaging during resizing
- 📐 Sharp, clear results at any scale
- 🎯 Preservation of original color vibrancy
- ⚡ GPU-accelerated processing
- 🌍 Interface in English, French, German, and Spanish
- 💻 Modern GUI with ttkbootstrap
- 📊 Real-time processing feedback

## 📋 Prerequisites

- Python 3.11.8
- CUDA Toolkit (for GPU acceleration)  https://developer.nvidia.com/cuda-downloads?
- Python dependencies listed in `requirements.txt`

## ⚙️ Installation

```bash
# Clone the repository
git clone https://github.com/Guiss-Guiss/ImageMap.git

# Navigate to directory
cd ImageMap

# Install dependencies
pip install -r requirements.txt

# Launch the application
python main.py
```

## 💡 Visual Quality Comparison

####Traditional Resizing:
- ❌ Creates averaged colors
- ❌ Tends toward grey
- ❌ Loses contrast
- ❌ Blurs details

####ImageMap:
- ✅ Uses only original colors
- ✅ Maintains color vibrancy
- ✅ Preserves contrasts
- ✅ Keeps details sharp

## 🔧 How It Works

1. **Analysis**
   - Identifies all original colors in the image
   - Maps color relationships and transitions

2. **Smart Resizing**
   - Selects appropriate original colors for each pixel
   - Avoids creation of averaged, greyed-out colors

3. **Detail Preservation**
   - Maintains sharp transitions between colors
   - Preserves the visual impact of small details

## 📝 Technical Details

- Native RGB processing
- Supports PNG, JPG, JPEG, BMP
- GPU-optimized algorithms
- Zero color interpolation

## 💻 Usage

1. Launch via `python main.py`
2. Load your image
3. Set scale factor
4. Watch as ImageMap resizes while maintaining original color vibrancy
5. Save your crisp, vibrant result

## 🎯 Key Advantage

Unlike traditional resizing tools that average colors and create a duller image, ImageMap maintains the original image's visual impact by completely avoiding color averaging, resulting in sharper, more vibrant output at any size.

## 🤝 Contributing

This is a proprietary project. For suggestions or bug reports, please contact me.

## 📜 License

© 2024 Guillaume Ste-Marie. All rights reserved.

---
*Dedicated to preserving image vibrancy through intelligent color processing*
