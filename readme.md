## About the project
At first I was just willing to switch on/off the DHW relying on Home Assistant as I hacked previously with my gas boiler.
After a few thinking, I wanted to ditch the wire for remote controller, to allow for free placement of the temperature sensors (i.e. samsung wireless nasa).
In the end, I ended up rewriting a NASA-MQTT bridge in python, allowing all the previous, and many more.

## Hardware parts
The project has been tested in 2 different configurations:

### Through F3/F4 pair
I'm connecting using the F3/F4 pair, and a wireless raspberry pi zero w.

The tricky part was to find how to communicate with the F3/F4 bus, using a THVD8000 proved useful and efficient.

I've designed a PCB to allow for USB<->F3/F4 to allow for more people to play with this, see it there [https://github.com/70p4z/samsung-f3-f4-usb-adapter](https://github.com/70p4z/samsung-f3-f4-usb-adapter).

### Through F1/F2 pair
It allows extracting many information from the AHSP. Also it's not yet suited to fully control it through that link.

## Communication Setup

The application supports two communication methods:

### Method 1: Serial via socat bridge (default)
This method uses a USB-to-RS485 adapter connected to your device, with `socat` creating a TCP bridge.

**Setup:**
1. Connect your USB-to-RS485 adapter (e.g., F3/F4 USB adapter)
2. Run the provided script which starts `socat` to bridge serial to TCP:
   ```bash
   ./run.sh
   ```
3. Or manually:
   ```bash
   socat /dev/ttyUSB0,raw,echo=0,nonblock,min=0,b9600,parenb tcp-listen:7001,reuseaddr &
   python3 samsung_mqtt_home_assistant.py --serial-host 127.0.0.1 --serial-port 7001
   ```

### Method 2: Direct TCP connection
This method connects directly to an Ethernet-to-RS485 converter without needing `socat`.

**Setup:**
1. Configure your Ethernet-to-RS485 converter with:
   - IP address (e.g., 192.168.1.100)
   - TCP port (e.g., 8080)
   - Serial settings: 9600 baud, even parity
2. Run the application pointing to your converter:
   ```bash
   python3 samsung_mqtt_home_assistant.py --serial-host 192.168.1.100 --serial-port 8080
   ```

**Note:** Despite the parameter names (`--serial-host` and `--serial-port`), the application always uses TCP sockets for communication. The names are kept for backward compatibility.

## How to manual run
Just execute the samsung_mqtt_home_assistant.py script after tweaking its values (extended configuration means to come)

## How to integration in HaOS (not an addons yet)

* Connect the F3/F4 adapter onto a USB port of the running Home Assistant Operating System. [https://github.com/70p4z/samsung-f3-f4-usb-adapter](https://github.com/70p4z/samsung-f3-f4-usb-adapter).

* Install the Enable 22222 SSH addons from [https://github.com/adamoutler/HassOSConfigurator/](https://github.com/adamoutler/HassOSConfigurator/) (follow instructions there), configure everything to open an SSH connection using keypairs on the HAOS supervisor (using PuTTY if you're not running a Linux box).

* Install the MQTT Mosquitto Broker addons (from official HA builtin repository)

* Run the following commands once connected to the HAOS supervisor in the SSH shell (login as root is required):
``` r
cd /tmp
curl -o samsung_nasa.tar.gz -OL https://github.com/70p4z/samsung-nasa-mqtt/archive/refs/heads/main.tar.gz
tar zxvf samsung_nasa.tar.gz 
cd samsung-nasa-mqtt-main
```
* Tweak the /tmp/samsung-nasa-mqtt-main/startup_docker.sh to modify the mqtt username and password fields to match your mosquitto configuration (either HA user/pass or another explicitely setup in the mosquitto configuration tab).

* Lastly run the initialization command, which will register and run the docker container and should create samsung's related entities once the code runs correctly
``` r
bash haos_ssh_22222_manual_setup.sh
```



## Demo
Here is a screenshot of the available items for my Samsung Mono R290 5kW (AE050CXYBEK/EU)
![alt Home Assistant screenshot](https://github.com/70p4z/samsung-nasa-mqtt/blob/main/home_assistant_list.png?raw=true)

## Future evolutions

Many things are under construction:
  - A PCB for remote controller to go wireless (still using a plug adapter, but wirelessing the F3/F4 bus)
  - Home Assistant scripts to allow for aggregating multiple temperature sensor and set the zone 1/2 current temp according to user rules (min of, max of ...)
  - more testing and control through F1/F2, there is a MITM I'd like to conduct to better heat the DHW, this is to reduce the water flow temperature to what is known to work but not too hot to avoid killing the CoP.

## Credits

- Super project to get started on protocol stuff [https://wiki.myehs.eu/wiki/NASA_Protocol]
- Another bridging device [https://github.com/lanwin/esphome_samsung_ac]
- For some ideas [https://github.com/Foxhill67/nasa2mqtt]
