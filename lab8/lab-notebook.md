# Lab Notebook 

## Part 0 - DMM
Put in the black and red banana test leads in the relevant part of the DMM. 
#### 1st measurement (Ines):
    • Picked a 10kohm resistor. 
    • Measured the resistance to be 10.01kohms.
#### 2nd measurement (Arjun): 
    • Picked a 4.7kohm resistor. 
    • Measured the resistance to be 4.684kohms.
![Setup0](lab8/setup0.heic)

## Part 1 - iOLab & DMM
### 1A - Resistors in series/Voltage Divider
#### 1st measurement (Ines):
    • Connected wires to 3.3V, A8, GND, formed the circuit
    • DAC --> Output mode, expert, Output was set to 2.0V.
    • Set up the DAC in the ioLAb app.
    • Started recording the data, but the data did not fluctuate when turning DAC on and off. 
    • Is this a software bug?
    • The DAC was set to 2.5V, and then back to 2.0V. 
    • The data still did not fluctuate. 
    • The breadboard was connected wrong, and was reconnected according to Figure 6 in the lab manual. 
    • New data was recorded. 
    • The data now fluctuates when DAC is turned on and off, which is promising. 
    • However, the A7 reading is 1.8V. 
    • The DAC was accidentally set to 1.8V, and was changed to 2.0V. 
    • A7 now reads 1.8V, even though the DAC was set to 2.0V. 
    • This is a software lag, and the DAC was set to 2.5V then back to 2.0V. 
    • A7 now reads 2.0V, as required. 
    • The data was saved.
#### 2nd measurement (Arjun):
    • Measurement went as expected and the data was saved.
### Using DMM to measure voltage
#### 1st measurement (Ines):
    • The circuit was unplugged and the DMM was connected to iOLab DAC and GRND. 
    • The measured value was 1.802V. 
    • This is a software error, so the ioLab was set to 2.5V then back to 2.0V. 
    • The measured voltage was 2.0225 (fluctation between 2.022 and 2.023).
#### 2nd measurement (Arjun):
    • Measured the DAC across the ioLab was 2.0225 (fluctation between 2.022 and 2.023). 
### 1B - Measuring Current
#### 1st measurement (Ines):
    • Circuit was set up.
    • When data was taken the high G gain sensor reading was above 1mV. 
    • A 1 kohm resistor instead of 1ohm resistor was used. 
    • The resistor was switched out for a 1ohm resistor.
    • Data was recorded and repository.
    • Note to selves: The G+/- data will need to be offset.
#### 2nd measurement (Arjun):
    • Data was recorded and saved to the repository.
#### In class self-check: 
    • I = V/R = 0.142+0.049mV/1ohm = 0.191mA. 
### Using DMM to measure current
#### 1st measurement (Ines):
    • Current was 0.0205mA (fluctuated between 0.02mA and 0.021mA)
#### 2nd measurement (Arjun):
    • Current was 0.20mA.

## Part 2 - Ohmic and Non-Ohmic Behaviour
### 2A - Ohmic Behaviour
#### 1st set of measurements (Ines):
    • The setup was kept the same as in experiment 1B. 
| DAC (V) | Current (mA) |
| :--- | :--- |
| 0.1 | 0.01 |
| 0.4 | 0.04 |
| 0.7 | 0.08 |
| 1.0 | 0.10 |
| 1.3 | 0.13 |
| 1.6 | 0.16 |
| 1.9 | 0.195 |
| 2.2 | 0.22 |
| 2.5 | 0.26 |
| 2.9 | 0.29 |
| 3.3 | 0.33 |
    DAC values were recorded using the iOLab.
#### 2nd set of measurements (Arjun):
