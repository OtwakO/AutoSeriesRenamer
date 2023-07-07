## AutoSeriesRenamer
影劇的自動改名和整理

只需要將影劇的資料夾放到偵測的主資料夾下就會自動偵測所有媒體的劇名並改名為 "劇名 SXXEXX" 再移動到相對應的資料夾，如下:
```bash
主資料夾 Main folder
├─ 影劇A
│  └─ Season 1
│     ├─ 影劇A S01E01
│     ├─ 影劇A S01E02
│     ├─ 影劇A S01E03
│     └── ...
├──── Season 2
│     ├─ 影劇A S02E01
│     └─ 影劇A S02E02
└─ 影劇B
   └─ Season 1
      ├─ 影劇B S01E01
      └─ 影劇A S01E02
```

## Docker Compose 安裝

`git clone https://github.com/tom28055101/AutoSeriesRenamer.git`

修改 docker-compose.yaml
```yml
services:
    series-renamer:
        build: .
        container_name: series-renamer
        volumes:
            - /path/to/directory:/app/rename # 設定媒體資料夾
            - ./logs:/app/logs
        restart: always
        stdin_open: true
        environment:
            - TZ=Asia/Taipei
```

部屬 Container

`docker compose up -d`

## 直接Python使用
下載 https://github.com/tom28055101/AutoSeriesRenamer/releases/tag/release

`pip install -r requirements.txt`

`python series_renamer.py scan-directory -s 路徑`

## CLI指令

可以先以 `docker exec -it series-renamer /bin/bash` 進入Container後再使用指令

或

直接 `docker exec series-renamer python3 series_renamer.py scan-directory -s /app/rename`

--------------------------------------------------------------------------------------------

__**推薦**__

偵測docker-compose.yaml裡設定的主資料夾路徑    

`python3 series_renamer.py scan-directory -s /app/rename`

--------------------------------------------------------------------------------------------

僅改名單獨資料夾底下媒體

`python3 series_renamer.py single-directory -d 路徑`

--------------------------------------------------------------------------------------------


## 定時自動啟用方法

在Host上使用`crontab -e` 並在底部加上

`*/5 * * * * docker exec series-renamer python3 series_renamer.py scan-directory -s /app/rename`

`*/5 * * * *` 可替換為其他頻率

## 其他參數
可以修改目錄下的 `.env` 檔案
```
PROXY = ""
FILE_FORMAT_FILTER = [".mp4", ".srt", ".mkv", ".ass"] 
REGEX_FILTER = " S\d+E\d+"
```
- PROXY = "http://user:passwd@domain:port" 或類似格式

- FILE_FORMAT_FILTER 可以新增其他需要偵測的副檔名

- REGEX_FILTER 不要改

## TODO
```

```
## 感谢
- 項目使用了 [acheong08/EdgeGPT](https://github.com/acheong08/EdgeGPT)
