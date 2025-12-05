# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HeyGem-Linux-Python-Hack is a digital human video generation system that creates lip-synced videos from audio and video inputs. Extracted from HeyGem.ai, it runs directly on Linux without Docker or Windows dependencies.

**Critical Requirements:**
- Python 3.8 only (enforced in run.py:17-19)
- Linux OS only
- CUDA-enabled GPU required for ONNX Runtime acceleration

## Common Commands

### Setup
```bash
# Download required model files
bash download.sh

# Verify ONNX Runtime GPU support
python check_env/check_onnx_cuda.py
```

### Running the Application
```bash
# Run with default example files
python run.py

# Run with custom audio and video (relative paths only)
python run.py --audio_path example/audio.wav --video_path example/video.mp4

# Launch Gradio web interface
python app.py
# Wait for model initialization before submitting tasks
```

## Architecture

### Core Processing Pipeline
1. **Audio Processing** - Audio input processed through WeNet speech model
2. **3DMM Parameter Generation** - Audio converted to 3D face parameters via compiled .so modules
3. **Face Detection & Alignment** - SCRFD (face detection) + PFPLD (landmark detection)
4. **Video Frame Generation** - Landmark-to-face synthesis using DiNet model
5. **Post-processing** - Face parsing, restoration (GFPGAN), and video encoding with FFmpeg

### Entry Points
- `run.py` - Command-line interface, processes single audio-video pair
- `app.py` - Gradio web UI, allows file uploads and interactive processing

Both override `service.trans_dh_service.write_video()` with custom implementations.

### Key Modules

**service/** - Core digital human processing (compiled .so files)
- `trans_dh_service.cpython-38-x86_64-linux-gnu.so` - Main video synthesis pipeline
- `server.cpython-38-x86_64-linux-gnu.so` - HTTP server functionality

**landmark2face_wy/** - Face synthesis from landmarks (compiled .so modules)
- `digitalhuman_interface.cpython-38-x86_64-linux-gnu.so` - Main inference interface
- `audio_handler.cpython-38-x86_64-linux-gnu.so` - Audio feature extraction
- `test_3dmm_multi_exp_wenet.cpython-38-x86_64-linux-gnu.so` - 3DMM parameter generation
- Models: `checkpoints/anylang/dinet_v1_20240131.pth`

**face_lib/** - Face processing utilities
- `face_detect_and_align/` - SCRFD face detection + PFPLD landmarks
- `face_parsing/` - Face segmentation (model: 79999_iter.onnx)
- `face_restore/` - GFPGAN face enhancement (model: GFPGANv1.4.onnx)

**wenet/** - Speech recognition for audio-to-3DMM mapping
- Model: `examples/aishell/aidata/exp/conformer/wenetmodel.pt`

**face_detect_utils/** - Face detection models and utilities
- `scrfd_500m_bnkps_shape640x640.onnx` - Primary face detector
- `pfpld_robust_sim_bs1_8003.onnx` - Facial landmark detector
- `model_float32.onnx` - Additional face processing model

**face_attr_detect/** - Face attribute detection
- `face_attr_epoch_12_220318.onnx`

**xseg/** - Face segmentation model
- `xseg_211104_4790000.onnx`

**Preprocessing**
- `preprocess_audio_and_3dmm.cpython-38-x86_64-linux-gnu.so` - Compiled audio/3DMM preprocessing

**Utilities**
- `y_utils/` - Configuration and logging (GlobalConfig, logger)
- `h_utils/` - Custom error handling (CustomError)
- `config/config.ini` - Application configuration (logging, server, directories, batch size)

### Data Flow
```
Audio + Video Input
    ↓
Face Detection & Alignment (SCRFD + PFPLD)
    ↓
Audio Feature Extraction (WeNet)
    ↓
3DMM Parameter Generation (audio_handler.so + test_3dmm_multi_exp_wenet.so)
    ↓
Face Synthesis (digitalhuman_interface.so using DiNet model)
    ↓
Face Enhancement (GFPGAN, Face Parsing)
    ↓
Video Assembly (FFmpeg with audio merge)
    ↓
Output Video
```

### Configuration
`config/config.ini` controls:
- Log directory and file paths
- HTTP server settings (default: 0.0.0.0:8383)
- Temporary and result directories
- Batch size for processing (default: 4)
- Registration/reporting settings

## Dependencies

### Critical Version Constraints
- Python: 3.8 exactly
- CUDA: Requires compatible CUDA toolkit (11.8.0 verified working)
- onnxruntime-gpu: Must match CUDA version (1.16.0 verified with CUDA 11.8)
- torch: 1.11.0+cu113

### Common Environment Issues

**onnxruntime-gpu compatibility:**
```bash
python check_env/check_onnx_cuda.py
# Should output "successfully" if GPU support is working
```

If CUDA provider fails:
1. Uninstall both `onnxruntime` and `onnxruntime-gpu`
2. Install CUDA toolkit via conda: `conda install cudatoolkit=11.8.0`
3. Reinstall `onnxruntime-gpu==1.16.0`

**Missing library.so files:**
```bash
# Find CUDA library location
sudo find /usr -name "libcublasLt.so.11"
# Add to environment
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

**Multiple face detection errors:**
Alternative face detection model available:
```bash
wget https://github.com/Holasyb918/HeyGem-Linux-Python-Hack/releases/download/ckpts_and_onnx/scrfd_10g_kps.onnx
mv face_detect_utils/resources/scrfd_500m_bnkps_shape640x640.onnx face_detect_utils/resources/scrfd_500m_bnkps_shape640x640.onnx.bak
mv scrfd_10g_kps.onnx face_detect_utils/resources/scrfd_500m_bnkps_shape640x640.onnx
```

## Model Files

All models downloaded via `download.sh` from GitHub releases. Key models:
- Face detection: SCRFD (500m/10g variants)
- Landmarks: PFPLD
- Face synthesis: DiNet v1
- Face parsing: BiSeNet-based (79999_iter)
- Face restoration: GFPGAN v1.4
- Speech features: WeNet conformer
- Face segmentation: XSeg

## Important Notes

- **Path handling:** Only relative paths supported for audio/video inputs
- **Initialization delay:** `run.py` includes 10-second sleep for model loading (line 185)
- **Compiled modules:** Core functionality in .so files (not modifiable without recompilation)
- **Output location:** Results saved to `./result/{work_id}/` by default
- **FFmpeg dependency:** Required for final video assembly with audio
- **Memory management:** Uses batch processing (default batch_size=4) for efficiency
