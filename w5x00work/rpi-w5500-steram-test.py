#!/usr/bin/python3

import io
import logging
import socketserver
from http import server
from threading import Condition
import argparse
import sys

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.output = kwargs.pop('output')  # output 객체를 인자로 받아 초기화
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with self.output.condition:
                        self.output.condition.wait()
                        frame = self.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def main():
    parser = argparse.ArgumentParser(description="Picamera2 MJPEG streaming with adjustable parameters.")
    parser.add_argument('--resolution', type=str, default="640x480", help="Resolution of the camera feed (e.g., 640x480)")
    parser.add_argument('--fps', type=int, default=24, help="Frames per second")
    parser.add_argument('--port', type=int, default=8000, help="Port to run the server on")

    # 파라미터 없이 실행될 경우 도움말 출력
    if len(sys.argv) == 1:
        parser.print_help()
        print(f"(Ex) ")
        print(f"   python3 {sys.argv[0]} --resolution 800x600 --fps 30 --port 8000")
        print(f"   python3 {sys.argv[0]} --resolution 1024x720 --fps 30 --port 8000")
        print(f"   python3 {sys.argv[0]} --resolution 1920x1080 --fps 30 --port 8000")
        print(f"   python3 {sys.argv[0]} --resolution 1920x1080 --fps 60 --port 8000")
        print(f"   python3 {sys.argv[0]} --resolution 1920x1080 --fps 10 --port 8000")
        sys.exit(1)


    args = parser.parse_args()

    # Parse resolution
    width, height = map(int, args.resolution.split('x'))

    # Initialize camera
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(main={"size": (width, height), "format": "RGB888"})
    picam2.configure(video_config)
    picam2.framerate = args.fps

    # Set up output and start recording
    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output))

    try:
        address = ('', args.port)
        server = StreamingServer(address, lambda *args, **kwargs: StreamingHandler(*args, output=output, **kwargs))
        print(f"Starting server on port {args.port} with resolution {width}x{height} at {args.fps} FPS.")
        server.serve_forever()
    finally:
        picam2.stop_recording()

if __name__ == '__main__':
    main()
