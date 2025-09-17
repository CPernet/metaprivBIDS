# Adaptive Qt Platform Setup - Implementation Summary

## Overview

The metaprivBIDS GUI now uses an adaptive Qt platform selection system that automatically detects the user's environment and chooses the most appropriate Qt platform. This ensures compatibility across different setups including local desktops, SSH X11 forwarding, VNC sessions, Wayland, and headless servers.

## Key Features

### 1. **Environment Auto-Detection**
The system automatically detects:
- **Headless environments** (no DISPLAY variable)
- **SSH X11 forwarding** (SSH_CONNECTION + DISPLAY set)
- **VNC sessions** (ThinLinc, TigerVNC, etc.)
- **Wayland desktops** (WAYLAND_DISPLAY or XDG_SESSION_TYPE)
- **Local X11 desktops**
- **Testing environments** (pytest presence)

### 2. **Platform Selection Logic**

#### For Different Environments:
- **Wayland**: `wayland` → `xcb` → `vnc` → `offscreen`
- **VNC/SSH X11**: `xcb` → `vnc` → `offscreen`
- **Local X11**: `xcb` → `wayland` → `vnc` → `offscreen`
- **Headless**: `offscreen`

#### Platform Testing:
- Each platform is tested before use to ensure it works
- Automatic fallback to the next option if a platform fails
- 10-second timeout for platform testing to prevent hanging

### 3. **User Override Support**
- Users can explicitly set `QT_QPA_PLATFORM` environment variable
- System respects user preferences and skips auto-detection
- Useful for forcing specific platforms or debugging

## Usage Examples

### Automatic Detection (Recommended)
```bash
# Let the system choose the best platform
conda run -p /path/to/env python run_metaprivBIDS_safe.py
```

### Manual Platform Selection
```bash
# Force specific platform
export QT_QPA_PLATFORM=xcb
conda run -p /path/to/env python run_metaprivBIDS_safe.py

# Or for VNC
export QT_QPA_PLATFORM=vnc
export QT_QPA_VNC_PORT=5901
conda run -p /path/to/env python run_metaprivBIDS_safe.py
```

### Different Environment Scenarios

#### 1. ThinLinc/VNC Desktop User
```bash
# System detects VNC environment and uses xcb
# GUI appears directly in your current session
python run_metaprivBIDS_safe.py
```
**Output**: `🖥️  Using X11 forwarding (xcb platform) - Display: :15.0`

#### 2. SSH X11 Forwarding
```bash
# System detects SSH X11 and uses xcb
ssh -X user@server
python run_metaprivBIDS_safe.py
```
**Output**: `🖥️  Using X11 forwarding (xcb platform) - Display: localhost:10.0`

#### 3. Headless Server
```bash
# System detects no display and uses offscreen
python run_metaprivBIDS_safe.py
```
**Output**: `🖥️  Running in headless mode (offscreen platform)`

#### 4. Local Wayland Desktop
```bash
# System detects Wayland and tries wayland first
python run_metaprivBIDS_safe.py
```
**Output**: `🖥️  Using Wayland platform - Display: wayland-0`

#### 5. Force Qt VNC Server
```bash
# Create separate VNC server for GUI
export QT_QPA_PLATFORM=vnc
export QT_QPA_VNC_PORT=5900
python run_metaprivBIDS_safe.py
```
**Output**: 
```
🖥️  Using Qt VNC server on port 5900
   Connect with: vncviewer localhost:5900
```

## Technical Implementation

### Core Functions

#### `setup_qt_environment()`
- Main function that orchestrates platform detection and selection
- Called automatically when importing metaprivBIDS
- Respects existing QT_QPA_PLATFORM settings

#### `_test_qt_platform(platform)`
- Tests if a specific Qt platform works
- Creates temporary test script to avoid hanging
- Returns True if platform is functional

### Environment Detection Logic
```python
# Display availability
has_display = bool(os.environ.get('DISPLAY'))

# Environment type detection
is_ssh_x11 = bool(os.environ.get('SSH_CONNECTION')) and has_display
is_vnc_session = ':' in display and any(proc in str(os.environ) for proc in ['vnc', 'thinlinc', 'tigervnc'])
is_wayland = os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland'
```

## Testing

### Comprehensive Test Suite
Run `test_qt_platform_comprehensive.py` to test:
- Environment detection accuracy
- Platform availability in your system
- Actual GUI launching capability

```bash
conda run -p /path/to/env python test_qt_platform_comprehensive.py
```

### Manual Testing
Test specific platforms manually:
```bash
# Test xcb platform
export QT_QPA_PLATFORM=xcb
python -c "from PySide6.QtWidgets import QApplication; app = QApplication([]); print('xcb works')"

# Test vnc platform
export QT_QPA_PLATFORM=vnc
export QT_QPA_VNC_PORT=5901
python -c "from PySide6.QtWidgets import QApplication; app = QApplication([]); print('vnc works')"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. **GUI doesn't appear in VNC session**
```bash
# Check your display
echo $DISPLAY

# Force xcb platform
export QT_QPA_PLATFORM=xcb
python run_metaprivBIDS_safe.py
```

#### 2. **Platform test hanging**
```bash
# Check available Qt plugins
find $CONDA_PREFIX -name "*platform*" | grep -i qt

# Try minimal platform for testing
export QT_QPA_PLATFORM=minimal
python run_metaprivBIDS_safe.py
```

#### 3. **VNC server port conflicts**
```bash
# Use different port
export QT_QPA_PLATFORM=vnc
export QT_QPA_VNC_PORT=5901
python run_metaprivBIDS_safe.py
```

#### 4. **Wayland issues**
```bash
# Fallback to X11
export QT_QPA_PLATFORM=xcb
python run_metaprivBIDS_safe.py
```

### Debug Information
Enable debug output:
```bash
export QT_LOGGING_RULES="qt.qpa.*=true"
python run_metaprivBIDS_safe.py
```

## Benefits

1. **Universal Compatibility**: Works across different environments without manual configuration
2. **Intelligent Fallback**: Automatically tries alternative platforms if preferred ones fail
3. **User Control**: Allows manual override when needed
4. **Robust Testing**: Platform functionality is validated before use
5. **Clear Feedback**: Informative messages about selected platform and connection methods
6. **Performance**: Quick platform testing prevents hanging or long waits

## Migration Notes

### From Previous Version
- Old hardcoded VNC approach replaced with adaptive selection
- No changes needed for most users - system auto-detects best option
- Manual platform selection still supported via environment variables
- More reliable GUI launching across different environments

### Backward Compatibility
- All existing launch methods continue to work
- Environment variable overrides still respected
- No changes needed to existing scripts or workflows
