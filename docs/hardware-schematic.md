# Representative Hardware Schematic

This project currently uses a software simulator, but the hardware model maps cleanly to an ESP32, Arduino, or Raspberry Pi Pico W prototype.

## One-Room Circuit Concept

```text
5V / 3.3V rail
  |
  +-- ESP32 / Pico W
      |
      +-- GPIO 18 -> relay / transistor driver -> Fan 1 load sensor
      +-- GPIO 19 -> relay / transistor driver -> Fan 2 load sensor
      +-- GPIO 21 -> relay / transistor driver -> Light 1 load sensor
      +-- GPIO 22 -> relay / transistor driver -> Light 2 load sensor
      +-- GPIO 23 -> relay / transistor driver -> Light 3 load sensor
      |
      +-- ADC 34 <- current sensor for fan rail
      +-- ADC 35 <- current sensor for light rail
      |
      +-- Wi-Fi -> Backend API
```

## Suggested Wokwi or Tinkercad Build

- Use one ESP32 or Pico W.
- Add five LEDs or relay modules to represent two fans and three lights.
- Add switches to simulate each device being manually turned on or off.
- Add current sensor placeholders or potentiometers to represent power draw.
- Send JSON to the backend with device id, status, watts, and timestamp.

## Example Payload

```json
{
  "device_id": "work1-fan-1",
  "status": true,
  "power_watts": 60,
  "timestamp": "2026-07-04T16:30:00"
}
```
