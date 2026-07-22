# This project is still on development

## Status (latest - 21/07/2026)
Developing the **core** concepts, so the capabilities are going to be running properly on a **simulated environment**.

- Simulated environment prerequisites:
    - Realsense D415 camera
    - Ubuntu 24.04 LTS on host machine

<br>

### Suggestions
_To enable **type hinting**, please execute the following command_:
> pybind11-stubgen pyrealsense2 -o typings

Then add the field below to the `.vscode/settings.json`:
> "python.analysis.stubPath": "./typings"