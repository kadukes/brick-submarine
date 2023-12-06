# Brick Submarine

This project contains a collection of circuit python scripts 
used in a raspberry pi in order to run a small autonomous 
underwater vehicle. This project is currently work in progress 
and not finished by far. Main parts of the project were 
inspired by a series of blog entries from a finnish creator 
called "Brick Experiment Channel" which can be found here: 
https://brickexperimentchannel.wordpress.com/. I will refer 
to this blog along the explanations in this readme.

My goal is to adapt the ideas in that blog and to overcome 
the limits it has by its current design. 

## Part 1: Building the hull

The hull of the submarine basically requires 
the same parts as those in the blog i.e. we also use an 
acrylic cylinder for the basic shape. 

However, the end caps are not assembled from acrylic parts, 
but printed using a 3D printer. The mesh-files for this can be 
found in the `resources` directory.

* `cap_head.stl`: This is the model of the front cap. It is 
    open at the front so that an acrylic glass pane can be 
    glued into the front. I used silicone for this. The cap 
    also has two grooves in which you can insert two sealing 
    rings. I took this idea from this Thingiverse project: 
    https://www.thingiverse.com/thing:4638848

    _Note_: We recommend the purchase of sealing rings. A 
    rubber seal is used in the blog, which is then glued 
    together to form a ring. However, this can mean that the 
    sealing function is not maintained satisfactorily.
* `cap_tail.stl`: This is the model of the rear cap. Unlike 
    the front cap, it is closed and contains three holes: two 
    plug connections for hoses and a central hole for cables.
* `sonar_admission.stl`: This part ensures that the sonar 
    sensor has a flat mount for the round surface of the 
    cylinder. 

For the remaining construction steps, please refer to the 
individual blog entries. These are explained there simply and 
clearly. 

Here is a (non-exhaustive) list of the additional materials 
required:
* Weights (we recommend tungsten, even if it is expensive. 
    Alternatively, you can use lead weights and strap them 
    around the cylinder)
* A syringe (it should hold approx. 50 to 60 ml)
* A drone propeller
* Neodymium magnets (suitable for the holes of LEGO® 3649 and 
    3648 gear wheels or similar)
* UHMW PE film tape

## Part 2: Building the mechanics

The mechanics of the submarine are made entirely of LEGO®. We 
do not provide detailed building instructions here. 
Interested readers can draw inspiration from the blog entries 
and videos. The blog also contains a complete parts list. 

## Part 3: Electronics

The picture below shows the circuit between the Raspberry Pi 
Zero 2 W and the rest of the electronics

![circuit diagram](./resources/circuit_diagram.png?raw=true)

Here is a (non-exhaustive) list of the electronic components 
required:
* Battery source (e.g. LEGO® 8878 Rechargeable
    Battery Box)
* Voltage regulator (e.g. Pololu 2123 S7V8F5 5V)
* 2x Motor driver (e.g. Pololu 2130 DRV8833 Dual H-bridge)
* Sonar sensor (should be waterproof, e.g. A02YYUW)
* Pressure sensor (e.g. Honeywell SSCMANV030PA2A3 2 bar)
* 9-Axis Digital motion processor (e.g. ICM-20948)
* Analog digital converter (e.g. COM-KY053ADC)

## Part 4: Software

The software is located in the src directory. It is currently 
in an unusable state. We are continuously developing the code. 
If you would like to contribute, please open an issue for this 
project. 
