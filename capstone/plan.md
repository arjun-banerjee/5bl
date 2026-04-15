# Quantifying Wi-Fi attenuation across variable FExperimental Materials
Arjun Banerjee, Ines Pajot

## Experimental Materials
WiFi router, aluminium foil, copper window screen, steel wool, aluminium mesh, chicken wire, wood strips, cable cutters, staple gun, multimetre, alligator clip cable.

## Experimental Procedure
Build the frame of the box out of the wooden dowels + wrap them in aluminium foil. 
Place the wifi router inside the box (unsure how we are going to control it logistically). 
Place the aluminum foil, chicken wire, and steel wool around the box. 
Set the multimeter to the continuity setting and ensure that the resistance → 0Ω to ensure that the cage is conductive.
Measure the signal strength from our phones.
Repeat this for 2.4 GHz, 5 GHz with different geometries.

This yield the following set of (8) RSSI measurements:
Geometry | 2.4GHz | 5GHz
Aluminium foil
Copper window screen (fine mesh)
Steel wool
Chicken wire

## How to quantify the uncertainties: 
Statistical uncertainty: For every measurement, record the RSSI once per second every 30s. Use the average of these readings as the reading, and the standard error of these readings as the uncertainty.
Spatial uncertainty: Move the phone 1-2cm in different directions + record the change.
Resolution: App only shows whole numbers. 
Combine the uncertainties via the root sum of squares.

## Core Theory 
Shielding effectiveness