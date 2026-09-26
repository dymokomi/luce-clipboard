#!/usr/bin/env python3
"""The X11 clipboard between real processes, on Linux with an X server (a running
display, else Xvfb): text and a PNG copied by one process and pasted by another,
a payload past one INCR step, and xclip on either side when it is installed."""
from pathlib import Path
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time

root = Path(__file__).resolve().parents[3]
compiler = Path(sys.argv[1]).resolve()
if platform.system() != "Linux":
    print("SKIP x11 clipboard: not Linux")
    sys.exit(0)

env = dict(os.environ)
server = None
if not env.get("DISPLAY"):
    xvfb = shutil.which("Xvfb")
    if xvfb is None:
        print("SKIP x11 clipboard: no DISPLAY and no Xvfb")
        sys.exit(0)
    server = subprocess.Popen([xvfb, ":97", "-nolisten", "tcp"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    env["DISPLAY"] = ":97"
    time.sleep(1.0)
env["LUCE_BASE"] = str(compiler)


def serve(program, mode, payload):
    """Start a process owning the clipboard with `payload`; it answers until killed."""
    process = subprocess.Popen([program, mode, payload], env=env, stdout=subprocess.PIPE, text=True)
    line = process.stdout.readline().strip()
    assert line == "ready", f"{mode} did not take the clipboard: {line!r}"
    return process


def stop(process):
    process.kill()
    process.wait()


try:
    with tempfile.TemporaryDirectory(prefix="clipboard-x11-") as temporary:
        work = Path(temporary)
        for flags in (["--native"], ["--native", "--release"], ["--backend=c"]):
            program = str(work / "clip")
            subprocess.run([compiler, "build", root / "tests/programs/x11/main.lucb", *flags, "-o", program], cwd=root, env=env, check=True)
            # Text, including what Latin-1 lacks, through a second process.
            text = "Luce clipboard: é € 日本 ✓"
            source = work / "text.in"
            source.write_bytes(text.encode("utf-8"))
            owner = serve(program, "serve-text", str(source))
            try:
                pasted = work / "text.out"
                subprocess.run([program, "read-text", str(pasted)], env=env, check=True, timeout=30)
                assert pasted.read_bytes().decode("utf-8") == text
                if shutil.which("xclip"):
                    out = subprocess.run(["xclip", "-selection", "clipboard", "-o"], env=env, check=True, capture_output=True, timeout=30).stdout
                    assert out.decode("utf-8") == text, out
            finally:
                stop(owner)
            # A payload past one INCR step (256 KiB) both ways.
            large = ("0123456789abcdef" * 40000)[:600000]
            source.write_bytes(large.encode())
            owner = serve(program, "serve-text", str(source))
            try:
                subprocess.run([program, "read-text", str(pasted)], env=env, check=True, timeout=30)
                assert pasted.read_bytes().decode() == large
            finally:
                stop(owner)
            # An image as image/png, bytes unchanged.
            png = bytes([137, 80, 78, 71, 13, 10, 26, 10]) + os.urandom(300000)
            image = work / "image.png"
            image.write_bytes(png)
            owner = serve(program, "serve-image", str(image))
            try:
                back = work / "image.out"
                subprocess.run([program, "read-image", str(back)], env=env, check=True, timeout=30)
                assert back.read_bytes() == png
            finally:
                stop(owner)
            # Copied in the same process: the answer comes back without X.
            subprocess.run([program, "self", "own words"], env=env, check=True, timeout=30)
            # Another program copies; this one pastes.
            if shutil.which("xclip"):
                writer = subprocess.Popen(["xclip", "-selection", "clipboard", "-i"], env=env, stdin=subprocess.PIPE)
                writer.communicate("from xclip ✓".encode("utf-8"), timeout=30)
                time.sleep(0.3)
                subprocess.run([program, "read-text", str(pasted)], env=env, check=True, timeout=30)
                assert pasted.read_bytes().decode("utf-8") == "from xclip ✓"
            print("PASS x11 clipboard " + " ".join(flags), flush=True)
finally:
    if server is not None:
        server.kill()
        server.wait()
