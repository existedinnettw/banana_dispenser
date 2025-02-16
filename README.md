# banana_dispenser

Obediently receive the ordered supplies

The function of this program is to quickly register and pick up the ordered items based on the provided order list.

![Screenshot](README.assets/Screenshot.png)

## Getting Started

### Install

You can building from source with following instruction. Or directly download binary from repo release page.

### Create lists

Create `people_list` and `object_list` follow example in `tests/data`.

### Start program

Execute `banana_dispenser` binary, then setup your lists path in setting page.

After switching back to scan page, you can start pick up objects by input people id. If your people id is same as RFID, then you can input people id by USB RFID reader.

## Building

To run program

```bash
poetry run program
```

aware that `rc_banana_dispenser.py` is generate through `poetry run pyside6-rcc banana_dispenser/banana_dispenser.qrc -o banana_dispenser/rc_banana_dispenser.py`.

To run test

```bash
poetry run pytest -rP
```

To [deploy](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html) program

```bash
poetry run pyside6-deploy banana_dispenser/banana_dispenser.py
```
