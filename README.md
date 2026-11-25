# Gaussian Elimination — M3 Animation

## Project Overview

A complete educational animation and demonstration showing how Gaussian elimination solves a three-variable system of linear equations. It introduces equivalent systems and augmented matrices, demonstrates elementary row operations, and uses forward elimination and back substitution to find and verify the solution. It also thoroughly classifies solution sets and illustrates relevant 2D line and 3D plane geometric cases.

- **Final Video with Voiceover:** `GaussianElimination_Final_With_Voiceover.mp4` (Full 1080p 30fps video with student voiceover narration synchronized across all 24 scenes)

## Student Information

- **Name:** Unnati Mehatkar
- **URN:** E25B070765
- **Batch:** Neumann
- **Lab:** Architecture

## Concepts Covered

- Systems of linear equations and equivalent systems
- Augmented matrices and the three elementary row operations:
  - Row swapping ($R_i \leftrightarrow R_j$)
  - Scalar row multiplication ($R_i \leftarrow k R_i$)
  - Adding a multiple of one row to another ($R_i \leftarrow R_i + k R_j$)
- Pivot positions, forward elimination, and upper-triangular row-echelon form
- Back substitution and multi-equation verification
- Complete solution set classification:
  - Unique solution (consistent with full pivot rank)
  - Infinitely many solutions (consistent with free variables)
  - No solution (inconsistent system with contradiction row $[0 \ 0 \ 0 \ | \ c]$)
- Geometric interpretations:
  - 2D lines: intersecting at a unique point, parallel distinct lines, and coincident lines
  - 3D planes: intersecting at a single point, intersecting in a line, parallel planes, and triangular prism configuration

### Worked Example
$$\begin{aligned}
x + y + z &= 6 \\
2x + y + 3z &= 13 \\
x + 2y + z &= 8
\end{aligned}$$
Unique solution: $(x, y, z) = (1, 2, 3)$.

## Technologies Used

- **Python 3**
- **Manim Community Edition 0.22.1**
- **FFmpeg** (lossless video stream copying & high-fidelity AAC audio muxing)
- **LaTeX** (rendering mathematical formulas and matrix notation)

## Repository Structure

```text
Gaussian-Elimination-M3-Animation/
├── GaussianElimination_Final_With_Voiceover.mp4  # Final exported video with synchronized voiceover (1080p30)
├── gaussian_elimination_final.py                 # Complete Manim animation source code (all 24 scenes)
├── verify_math.py                                # Automated mathematical verification script
├── requirements.txt                              # Python package dependencies
├── Storyboard.pdf                                # Project storyboard and visual planning
├── GaussianElimination_Scene_Timestamps.txt      # Exact render scene timestamps (S01–S24)
├── GaussianElimination_Voiceover_Script.txt      # Full narration voiceover script
├── .gitignore                                    # Git ignore rules for caches & virtual environments
└── README.md                                     # Project documentation
```

## Setup & Verification

1. **Clone the repository:**
   ```sh
   git clone https://github.com/unnati-09m/Gaussian-Elimination-M3-Animation.git
   cd Gaussian-Elimination-M3-Animation
   ```

2. **Verify mathematical correctness:**
   Run the exact-arithmetic and rank checks across all system matrices and geometric cases:
   ```sh
   python3 verify_math.py
   ```

3. **Re-rendering the animation (optional):**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   manim render -r 1920,1080 --fps 30 -o GaussianElimination.mp4 gaussian_elimination_final.py GaussianElimination
   ```

## Voiceover Narration & Synchronization

The animation features student voiceover narration synchronized across all 24 scenes:
- **Part 1 (Scenes S01–S11):** Covers Foundations, Elementary Row Operations, Augmented Matrices, Forward Elimination, Back-substitution, and Verification (0.00s – 188.13s).
- **Part 2 (Scenes S12–S24):** Covers Matrix Interpretation, Row-echelon form, Geometry of 2D lines and 3D planes, Zero & Contradictory rows, and Conclusion (188.13s – 408.89s).

Narration audio was aligned to match the exact scene transition timestamps of the animation while preserving natural pauses and conversational pacing without cutting any spoken words.
