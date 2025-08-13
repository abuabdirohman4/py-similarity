# Image Similarity Selector

## Overview

This application is designed to automatically select the best image from sets of visually similar images within a structured directory (such as educational video frames or slides). It is particularly useful for scenarios where multiple versions of the same image exist (e.g., with suffixes like \_2, \_3, \_4), and you want to programmatically determine the highest quality or most representative image from each set.

The tool leverages advanced image similarity metrics to compare images and outputs a list of the best images, sorted by their creation or modification time.

## Features

- **Automatic Grouping:** Groups images by their base filename, ignoring suffixes like \_2, \_3, \_4.
- **Similarity Comparison:** Uses the Structural Similarity Index (SSIM) for accurate visual comparison.
- **Batch Processing:** Processes all subfolders or specific chapters (e.g., ch6, ch7, ch8, ch9) as needed.
- **Customizable Output:** Outputs the best image names (without extension) for each group, sorted by file creation/modification time.

## Technologies Used

- **Python 3.7+**
- **OpenCV (cv2):** For image loading and resizing
- **scikit-image:** For SSIM calculation
- **NumPy:** For array manipulation 
- **tqdm:** For progress bars

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Install dependencies:**
   It is recommended to use a virtual environment.
   ```bash
   python -m venv venv
   On Mac/Linux: source venv/bin/activate  
   On Windows: source venv/Scripts/activate
   pip install -r requirements.txt
   ```

## Directory Structure

```
project-root/
├── video10/
│   ├── ch6/
│   ├── ch7/
│   ├── ch8/
│   └── ch9/
│       └── ... (image files)
├── output/
│   └── ch6_best_images.txt
│   └── ch7_best_images.txt
│   └── ch8_best_images.txt
│   └── ch9_best_images.txt
├── similarity.py
├── requirements.txt
└── README.md
```

## Usage

1. **Prepare your images:**

   - Place your images in the appropriate chapter folders under `video10/` (e.g., `video10/ch6/`).
   - Ensure each set of similar images shares a base filename, differing only by suffixes (e.g., `image.jpg`, `image_2.jpg`, `image_3.jpg`, `image_4.jpg`).

2. **Run the script:**

   ```bash
   python similarity.py
   ```

   - By default, the script will process all images in the specified folder(s) and output the best image names to the `output/` directory.
   - You can modify the script to process specific chapters or the entire `video10` directory as needed.

3. **Check the results:**
   - The output files (e.g., `ch6_best_images.txt`) will contain the best image name (without extension) for each group, sorted by file creation/modification time (oldest first).

## Customization

- To process specific chapters, adjust the `process_chapter` function call in `similarity.py`.
- To change the similarity metric, you can modify the `calculate_similarity` function.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [OpenCV](https://opencv.org/)
- [scikit-image](https://scikit-image.org/)
- [NumPy](https://numpy.org/)
- [tqdm](https://tqdm.github.io/)

---

For questions or contributions, please open an issue or submit a pull request.
