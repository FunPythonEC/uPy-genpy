# uPy-genpy

This is a little similar implementation of `genpy` for uPy. In order to use rosserial with it, having messages classes. For that and automation purposes, this package has been done so that this classes can be done easily. This has been done to be used with [uPy rosserial](https://github.com/FunPythonEC/uPy-rosserial).

## Features

- [x] uPy files gen with publish availability
- [x] uPy files gen with subscribe availability
- [ ] Services

## Installation
In order to use this package the folder `ugenpy` from `src` must be copied to the flash memory. I strongly recommend using [rshell](https://github.com/dhylands/rshell) for this task. 

There is also a folder called `std_msgs` which has all default `*.msg` files, this folder can also be copied or any other folder with the wanted message types. For memory purposes not all the `msg` files in that folder must be copied, only the ones that are going to be used.

You can also install it with:
``` python
import upip
upip.install('micropython-genpy')
```
>Note: To use upip you must be connected to WiFi and the files with std_msgs dir must be included manually.

## Usage

Suppose there is already the dir `std_msgs/ColorRGB.msg` and we want to create the uPy file for it, then a script like below can be run:

``` python
from ugenpy.message import MessageGenerator
msg=MessageGenerator('std_msgs/ColorRGBA.msg')
msg.create_message()
```

You could verify it has been created with the following:
``` python
import os
os.listdir('std_msgs')
```

