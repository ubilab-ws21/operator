# Camera Firmware

This is based on [https://github.com/m5stack/m5stack-cam-psram.git](https://github.com/m5stack/m5stack-cam-psram).
Use esp-idf 3.3.1 to build. In particular, we have copied 2 header files (`osal.h` and `esp_httpd_priv.h`) into this source tree to disable Nagle's algorithm. If you use a newer esp-idf, you may have to replace those headers with the new version.

# Build/Flash

- `/opt/esp-idf/tools/idf.py build`
- `/opt/esp-idf/tools/idf.py flash`
