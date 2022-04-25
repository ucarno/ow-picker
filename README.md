# Overwatch Hero Picker
Overwatch Hero Picker is an application that tries to automatically pick selected hero. 
Only 1920x1080 screens are supported.

![demo](https://i.ibb.co/p4JnWCQ/image.png)

## Installation
1. Download zip archive from [releases page](https://github.com/ucarno/ow-picker/releases).
2. Extract `Picker` directory wherever you want.
3. Done! Open `Picker.exe` found in Picker directory.
4. Optionally create desktop link to executable.

## Usage
1. Select desired hero.
2. When game is found, set app state to active by pressing button or using shortcut `Ctrl + W`.
3. Wait for the hero selection screen.
4. When hero is selected, app state is automatically set to inactive,
so you can freely change your hero whenever you want.

### Changing hotkey
Currently, you can change hotkey only by modifying `config.json` file which you can find in
application directory after opening and closing program first time.

## Supported languages
Currently, only English and Russian languages are supported.

## Building executable from source
* Create virtual environment and install necessary libs from `requirements.txt`.
* Build to directory
  * Either using `.scripts/build-directory.cmd` script
  * Or using `pyinstaller --noconfirm src/Picker.spec` command
