# AffineExtractor

This repository provides Python tools to extract and refine local affine transformations between image pairs based on feature matching.

Unlike standard matching pipelines that only output $(x, y)$ point correspondences, this toolbox leverages the scale and orientation properties of local descriptors (like OpenCV's SIFT) to compute the **local affine frame** for each individual match.

## Features

* **OpenCV SIFT Affine Matcher (`OpenCVAffineMatcher.py`)**: Computes initial local affine transformations directly from OpenCV's `cv2.SIFT` keypoint properties (`size` and `angle`) after matching.
* **Affine Refinement Tools**: The extracted initial affine frames can be further optimized using the provided refinement scripts:
  * `LucasKanadeAffineRefinement.py`: Gradient-based refinement.
  * `BruteForceAffineRefinement.py`: Search-based refinement.
* **Affine Helper (`AffineHelper.py`)**: Utility functions for manipulating and visualizing affine matrices.

## Setup & Dependencies

The code is written in Python and relies on standard computer vision libraries.

```bash
pip install numpy opencv-python matplotlib scipy
