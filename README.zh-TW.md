# 香蕉分配器

忠實地分配訂購的商品

這個程式的功能是根據提供的訂購清單，快速的登記領取訂購的物品。

![Screenshot](README.assets/Screenshot.png)

## 入門指南

### 安裝

您可以按照以下說明從源代碼構建，或者直接從 repo 的發布頁面下載二進制文件。

### 創建列表

按照 `tests/data` 中的示例創建 people_list 和 object_list。

### 啟動程序

執行 banana_dispenser 二進制文件，然後在設置頁面中設置您的列表路徑。

切換回掃描頁面後，您可以通過輸入人員 ID 開始拾取物品。如果您的人員 ID 與 RFID 相同，則可以通過 USB RFID 讀取器 輸入人員 ID。

## 構建

執行程式

```bash
poetry run program
```

注意 `rc_banana_dispenser.py` 是通過以下命令生成的：`poetry run pyside6-rcc banana_dispenser/banana_dispenser.qrc -o banana_dispenser/rc_banana_dispenser.py`。

執行測試

```bash
poetry run pytest -rP
```

如要[部署](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html)程式

```bash
poetry run pyside6-deploy banana_dispen
```
