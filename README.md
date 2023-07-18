# deterministic-sand

## What is this?

This is a simple prototype of deterministic sand simulation. It allows to map a texture to a end state of a sand simulation. The simulation is deterministic, so the next time we run the simulation with the same parameters, falling sand will eventualy form the same image.

## How do I use it?

You can just run `main.py` and watch the simulation capture I prepared for you or you can change `mapping_mode` to `True` inside `main.py`, run the code, draw sand with your mouse, change it back to `False` and run the code again to see the simulation reproduce the image with your previous mouse movements.

## License

All code is licensed under MIT license. See CODE_LICENSE file for more information.

All images and values inside .npy numpy array files with `_texture` in their names are copyright Looki2000 and cannot be used for anything outside this project without my permission except in forks of this repository.
