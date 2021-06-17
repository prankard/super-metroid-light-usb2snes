# Super Metroid Light



### Setup

- Use a compatible light (preferably YeeLight)
- Download the latest [release](./releases)
- Copy config-sample-bulbtype.json to config.json and fill in values
- Run QUsb2Snes and have Snes Running
- Run SuperMetroidLight.exe



### Compatible Lights

##### YeeLight Wifi RGB Bulb

- The preferred light to test with due to ease setup, local ip and brighter colors
- Needs IP address added to the config.json
- Tested with **Smart LED Bulb 1SE**

##### Tuya Compatible Wifi RGB Smart Bulb 

- Official API with the developer program. Not Tuya Convert :( 
- You'll need to register as a developer and get a ClientID, SecretKey and Device ID and know the server region you are connecting to, takes at least 2 days to register and prove you are not from mainland China
- More details on setup/getting details here: https://github.com/Octoober/tuya-bulb-control
- Tested with Energizer A40