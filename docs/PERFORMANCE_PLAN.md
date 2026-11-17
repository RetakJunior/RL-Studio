# Performance plan

## Existing capability

The source has input, freehand stroke, canvas rendering, OpenGL texture, and benchmark/test code. `libs/ui/tests/FreehandStrokeBenchmark.*` is a candidate baseline, but its CMake registration is marked as a broken test; execution status is unverified. Source presence is not a measurement.

## Measurement protocol

1. Configure a supported build; record compiler, Qt, GPU/driver, display refresh, tablet, and build type.
2. Fix canvas sizes, color spaces, layer counts, brush presets, stroke paths, and warm-up duration.
3. Capture repeated software input-to-render timings and report median/tail percentiles, CPU/GPU use, and memory.
4. Use external high-speed capture if claiming display/input-to-photon latency.
5. Run identical workloads before/after; retain raw data, commands, and run variance.
6. Measure instrumentation overhead on/off.

Profile before optimizing. Preserve pressure, tilt, spacing, interpolation, smoothing, and undo behavior. Any added benchmark must be repeatable and registered as a runnable target.

## Current result

No source build, benchmark run, or RL Studio-versus-Krita comparison has been completed. No performance gain is claimed.
