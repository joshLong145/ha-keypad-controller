# Home Assistant NumPad interface

### Allows for custom actions against an async messaging api


### Define your own behavior functions to map to device interrupts

## Dependencies
    - evdev
    - websocket

## Installing
    - After cloning run `pip install --requirments.txt`
## Global Variables
    - DEV_PATH path to device, ex: /dev/input/event1
    - AUTH_TOKEN: Home Assistant Love Lace authentication token

## Device Actions
    For actions performed by a keypress, the first paramaters must be a `future`

## TODO
    - Create statemanagement that does not rely on global variables
    - Allow for better thread exiting when a interupt comes through
    - Support connection repair for long lived sessions
    - Possibly support asyncio future api for custom tasks

