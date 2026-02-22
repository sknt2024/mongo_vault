#!/bin/bash

INPUT="$1"

if [ -z "$INPUT" ]; then
  echo "Usage: ./png-to-icns.sh icon.png"
  exit 1
fi

NAME=$(basename "$INPUT" .png)

mkdir "$NAME.iconset"

# Generate required sizes
sips -z 16 16     "$INPUT" --out "$NAME.iconset/icon_16x16.png"
sips -z 32 32     "$INPUT" --out "$NAME.iconset/icon_16x16@2x.png"

sips -z 32 32     "$INPUT" --out "$NAME.iconset/icon_32x32.png"
sips -z 64 64     "$INPUT" --out "$NAME.iconset/icon_32x32@2x.png"

sips -z 128 128   "$INPUT" --out "$NAME.iconset/icon_128x128.png"
sips -z 256 256   "$INPUT" --out "$NAME.iconset/icon_128x128@2x.png"

sips -z 256 256   "$INPUT" --out "$NAME.iconset/icon_256x256.png"
sips -z 512 512   "$INPUT" --out "$NAME.iconset/icon_256x256@2x.png"

sips -z 512 512   "$INPUT" --out "$NAME.iconset/icon_512x512.png"
sips -z 1024 1024 "$INPUT" --out "$NAME.iconset/icon_512x512@2x.png"

# Convert to icns
iconutil -c icns "$NAME.iconset"

# Cleanup
rm -rf "$NAME.iconset"

echo "✅ Created $NAME.icns"