# 必要モジュールをインポートする
import sqlite3

# 定数定義
# ファイル名：カード名対応表
FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE = 'BUOD_EN_to_JP.txt'
FILE_NAME_EN_CARD_DB = 'cards.delta.cdb'
FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE_WITH_ID = 'BUOD_EN_to_JP_WITH_ID.txt'

# 関数定義


def createCardNameCorTables(fileName):
    # 英語->日本語の対応表(.txt)を読み込み
    # 例
    #   EnCardName, JpCardName\n
    f = open(FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE, 'r', encoding='UTF-8')

    # 英語->日本語の対応表を1行ずつ読み込み
    list = f.readlines()

    # 英語->日本語の対応表の定義
    # 例
    #   cardNameCorTables = [enCardName, jpCardName]
    cardNameCorTables = [
        [0 for i in range(2)] for j in range(len(list))]

    index = 0

    for data in list:
        enCardName = data.split(",")[0]
        # 末尾の改行コードを削除して登録
        jpCardName = data.split(",")[1].rsplit("\n")[0]

        cardNameCorTables[index][0] = enCardName
        cardNameCorTables[index][1] = jpCardName

        index += 1

    f.close

    return cardNameCorTables


def convertCardNameCorTableWithId(cardId, enCardName, jpCardName):
    cardNameCorTable = list(range(3))
    cardNameCorTable[0] = cardId
    cardNameCorTable[1] = enCardName
    cardNameCorTable[2] = jpCardName

    return cardNameCorTable


def createCardNameCorTablesWithId(fileName, dbName):
    # 英語版のカードデータベースに接続する
    conn = sqlite3.connect(dbName)
    c = conn.cursor()

    # 英語->日本語対応表を作成
    cardNameCorTables = createCardNameCorTables(
        FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE)

    # ID付き英語->日本語対応表の定義
    # cardNameCorTablesWithId = [[id , EN Card Name , JP Card Name]]
    cardNameCorTablesWithId = []

    index = 0

    for cardNameCorTable in cardNameCorTables:
        # 英語->日本語対応表から英語、日本語のカード名を読み込む
        enCardName = cardNameCorTable[0]
        jpCardName = cardNameCorTable[1]

        # カード名からカードIDを検索するSQLの作成
        sql = 'SELECT id FROM texts WHERE name = "' + enCardName + '"'

        # SQLの実行(実行結果はカードIDとして扱う)
        for row in c.execute(sql):
            cardId = row[0]

            # ID付き英語->日本語対応表に要素を追加する
            cardNameCorTablesWithId.append(convertCardNameCorTableWithId(
                cardId, enCardName, jpCardName))

        index += 1

    # データベースへのアクセスが終わったら close する
    conn.close()

    return cardNameCorTablesWithId


def createCardNameCorTablesWithIdFile(cardNameCorTablesWithId):
    f = open(FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE_WITH_ID,
             'w', encoding='UTF-8')

    for data in cardNameCorTablesWithId:
        f.write(str(data[0]) + ',' + data[1] + ',' + data[2] + '\n')

    f.close


createCardNameCorTablesWithIdFile(
    createCardNameCorTablesWithId(
        FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE, FILE_NAME_EN_CARD_DB)
)
