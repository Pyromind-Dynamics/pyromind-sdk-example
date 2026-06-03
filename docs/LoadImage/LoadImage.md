# LoadImage Node

![alt text](imgs/LoadImage/LoadImage.png) 

## 2.2.1 Overview

Reads a selected image from `/workspace/image_cache/` and outputs its path.

Supported formats: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`

## 2.2.2 Input

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| image     | STRING (enum) | Image file selected from the dynamic list of `/workspace/image_cache/`. Supports `image_upload` extension (allows users to upload new images). Default: first image path in the list. |

## 2.2.3 Output

| Parameter      | Data Type | Description |
|----------------|-----------|-------------|
| image_file_path | STRING    | Full path of the image in workspace, formatted as `/workspace/{selected_image_path}`. Passed to downstream nodes (e.g., RL training, Rollout) for image content reading. No path existence validation is performed. |
