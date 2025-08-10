# Doorbot

A python IRC bot that runs on a BeagleBone Black and announces the state of the deadbolt (locked/unlocked) to the channel.

## Why

[See here for context](https://0x85.org/door2.html)

## Required Materials

- 1x BeagleBone Black
- 1x 2.2 kOhm resistor
- 1x 100 Ohm resistor (optional)
- 1x 10 uF capacitor
- wires, terminal blocks, protoboard, etc.
- a switch of some sort (cool kids use two springs soldered to a bit of perfboard)


Wire it up as such:

![Circuit diagram](https://raw.githubusercontent.com/nathanvy/doorbot/refs/heads/master/circuit.png "Circuit Diagram")

You can of course implement the circuit in lots of different ways.  A key point to bear in mind is that I used this circuit with these parts because it is what I happened to have on hand.  The goal was to spend zero dollars.
