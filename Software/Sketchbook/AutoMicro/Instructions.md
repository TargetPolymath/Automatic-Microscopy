# CD Driver

1. Disassemble the CD driver chassis until you have a metal frame carrying two parallel rods, a small cylendrical motor and screw, and the rotary table the CD rested on.
1. Solder wires to each of the four leads on the cylendrical motor. This is a somewhat difficult step, so be careful, and don't be afraid to detatch the motor from the rest of the frame. Consider leaving or reusing any pre-existing leads on the cylendrical motor - this may be simpler and pose a lower risk of failure.

# Wiring

1. Each wire will have a medium-resistance connection to exactly one other wire, and no connection to the remaining two wires. Two wires which share this medium-resistance connection are on the same coil.
1. Each coil needs to be able to be energized in either direction. Research the motivation behind using a Double H Bridge to drive a stepper motor.
1. I chose to use two digital pins per direction per coil (due to poor voltage) to provide the positive suppplies, and the stepper driver board to provide 'switched' access to ground - one switch per direction per coil. This could be better achieved with two driver boards, one switching upstream current and the other switching access to ground.
