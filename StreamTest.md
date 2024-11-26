
# Raspberry Pi Video Streaming Test

## Overview
I tested video streaming on the Raspberry Pi 5, using both its built-in Ethernet and the W5500 module simultaneously.

## Test Environment
- **Target Device**: [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
- **Ethernet Module**: [WIZnet WIZ850io](https://docs.wiznet.io/Product/ioModule/wiz850io)
- **Camera**: [R-Pi Camera](https://www.raspberrypi.com/products/)
- **Built-in Ethernet** : (eth0) 192.168.10.17  
- **W5500 Ethernet** : (eth1) 192.168.11.17  
  
![image](https://github.com/user-attachments/assets/e2275bee-4a47-4de8-b33c-f429b14df375)

Refer to the image below for an example of the wiring:  
![{778C1876-A01F-4941-9B26-184E76070C50}](https://github.com/user-attachments/assets/dc2f8a86-a709-44a8-aee5-91bed60f94d0)

## Streaming server
On the Raspberry Pi, After I verified basic camera functionality and then run a Python script([rpi-w5500-steram-test.py](w5x00work/rpi-w5500-steram-test.py])) for the streaming server.   
Below is the screenshot of the test in action:
![{56604D76-32C1-45DA-9B98-B0D1EA7CCEED}](https://github.com/user-attachments/assets/ba6f885d-4846-4edf-ad2d-c39c98707a99)

And, I use the vnstat command to monitor network usage in real time while streaming.
```bash
vnstat -l -i eth0
vnstat -l -i eth1
```

## Stream Test A - 800 X 600, 30 FPS
The first test streams video at 30FPS with a resolution of 800 X 600. 
![image](https://github.com/user-attachments/assets/38b50c1d-2c8a-4087-a3a3-9bc5b0b82ca2)

The left side of the screen is a test of built-in ethernet, and the right side is a test of W5500.  
Both the Raspberry Pi’s built-in Ethernet and the W5500 performed similarly, with network traffic around 6Mbps.
![image](w5x00work/stream-1.gif)  

## Stream Test B - 1920 x 1080, 30 FPS
The second test streams video at 30FPS with a resolution of 1920 x 1080. 
![image](https://github.com/user-attachments/assets/4d8e8f9a-3955-4a6b-a729-98b64478687d)

The left side of the screen is a test of built-in ethernet, and the right side is a test of W5500.  
Compared to the built-in Ethernet, the W5500 showed a slight delay with network traffic of about 12 ~ 20Mbps.
![image](w5x00work/stream-2.gif)  

## Conclusion
If the MCU/MPU has sufficient performance, it seems possible to stream video at HD or FHD resolutions with the W5500. I plan to test it again with W6300 chip.

