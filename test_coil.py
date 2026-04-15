#!/usr/bin/env python3
import importlib.util
spec = importlib.util.spec_from_file_location("coil_scanner", "/Users/sigbotti/.openclaw/workspace/scripts/coil-scanner.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print('Testing get_coil_data(GME)...')
result = mod.get_coil_data('GME')
print('Result:', result)
print('Type:', type(result))