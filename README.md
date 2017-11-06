# ECE_4564_A2
Net Apps assignment 2; Wishing Well

Blue tooth python tutorial:
http://blog.kevindoran.co/bluetooth-programming-with-python-3/

Another tutorial:
https://github.com/EnableTech/raspberry-bluetooth-demo

^ For installing pybluez
1) sudo apt-get install libbluetooth-dev
2) sudo pip3 install pybluez
3) sudo apt-get install bluetooth bluez
4) sudo apt-get install bluez python-bluez

^ For setting up bluetooth on the pi: (From the second tutorial)
1) sudo rfkill unblock all
2) sudo hciconfig hci0 up
3) sudo hciconfig hci0 piscan
4) (Give it a name) sudo hciconfig hci0 name 'new name (dont use any single quotes/apostrophes in the name)'

LED Color Meaning
Green = Connected to Bluetooth Device
Purple = Consuming a message
Red = Publishing a message

SPECIAL NOTE FOR ADAM:
To get your damned rabbitmq working
1) cd /usr/sbin
2) sudo ./rabbitmqctl stop
3) sudo ./rabbitmq-server start

