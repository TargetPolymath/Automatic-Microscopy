# Game Plan
This is a very (very) simple timed driving and capture system using gphoto2 and an Arduino-based G-Code driver system (AutoMicro).

# Needs

1. Orchestration
1. Timing
1. Image Capture
1. Arduino Instruction


# Core Loop

1. Capture an image
1. Wait for capture to complete
1. Move a specified step and direction
1. Wait until the camera is ready
1. Potentially wait longer if this is a time lapse
1. Repeat

# Options

gphoto2 has multi-image timing features and post-capture callbacks. This is promising for the simplest applications, but requires additional features to be baked into the callback, rather than more complex operations driving both the image capture and motion. This route will be discarded.

Assuming the orchestration isn't running on the arduino, that leaves some other piece of software. I'll choose to use Python.