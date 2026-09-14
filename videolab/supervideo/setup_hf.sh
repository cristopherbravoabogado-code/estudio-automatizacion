#!/bin/bash
# HyperFrames gratis en el sandbox: Node 22 + motor + Chrome headless. ~2 min. Se pierde con el sandbox.
set -e; mkdir -p /tmp/hf && cd /tmp/hf
[ -d node-v22.14.0-linux-x64 ] || { curl -sL https://nodejs.org/dist/v22.14.0/node-v22.14.0-linux-x64.tar.xz -o n.txz && tar xf n.txz; }
export PATH=/tmp/hf/node-v22.14.0-linux-x64/bin:$PATH HYPERFRAMES_SKIP_SKILLS=1
[ -d node_modules/hyperframes ] || npm install hyperframes@0.8.37 >/dev/null 2>&1
npx hyperframes browser ensure >/dev/null 2>&1 || true
pip install --quiet numpy >/dev/null 2>&1 || true
echo HF_SETUP_OK $(node -v)
