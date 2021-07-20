# 必要モジュールをインポートする
import sqlite3

FILE_NAME_JP_CARD_DB = '0_20210717_BUOD.cdb'
FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE_WITH_ID = 'BUOD_EN_to_JP_WITH_ID.txt'
FILE_NAME_NOT_EXIST_BUOD_cdb = 'NOT_EXIST_BUOD_cdb.txt'

# 関数定義


def transrateDbCorCardName(cardName):
    jpDbCardName = ''

    jpHarfCardName = cardName.translate(
        str.maketrans({chr(0xFF01 + i): chr(0x0021 + i) for i in range(94)}))

    index = 0
    while index < len(jpHarfCardName):
        if '-' != jpHarfCardName[index]:
            jpDbCardName += jpHarfCardName[index]
        else:
            jpDbCardName += '－'
        index += 1

#    print(jpDbCardName)

    return jpDbCardName


def createCardIdTables(cardIdTableFileName):
    # 英語->日本語の対応表(.txt)を読み込み
    # 例
    #   EnCardName, JpCardName\n
    f = open(cardIdTableFileName,
             'r', encoding='UTF-8')

    # 英語->日本語の対応表を1行ずつ読み込み
    list = f.readlines()

    # 英語->日本語の対応表の定義
    # 例
    #   cardNameCorTablesWithId = [enCardName, jpCardName]
    idCardNameTables = [
        [0 for i in range(2)] for j in range(len(list))]

    index = 0

    for data in list:
        cardId = data.split(",")[0]
#        enCardName = data.split(",")[1]
        # 末尾の改行コードを削除して登録
        jpFullCardName = data.split(",")[2].rsplit("\n")[0]

        idCardNameTables[index][0] = cardId
        idCardNameTables[index][1] = str(
            transrateDbCorCardName(jpFullCardName))

        index += 1

    f.close

#    print(idCardNameTables)

    return idCardNameTables


def createOldIdTables(dbFileName, idCardNameTables):
    conn = sqlite3.connect(FILE_NAME_JP_CARD_DB)
    c = conn.cursor()

    oldIdCardNameTables = [
        [0 for i in range(2)] for j in range(len(idCardNameTables))]

    notExistJpDbCardList = []

    index = 0

    print("idCardNameTables")
    print(idCardNameTables)
    print("---")

    index = 0

    for data in idCardNameTables:

        #        print("---")
        jpCardName = idCardNameTables[index][1]

        # カード名からカードIDを検索するSQLの作成
        sql = f"SELECT id, name FROM texts WHERE name = '{jpCardName}'"
#        print(sql)

        c.execute(sql)
        result = c.fetchall()

#        print("result")
#        print(result)
#        print(len(result))
#        print("---")

        if(0 != len(result)):
            #            print("exist")
            for row in result:
                oldIdCardNameTables[index][0] = row[0]
                oldIdCardNameTables[index][1] = row[1]
        else:
            print("---")
            print("not exist")
            print(sql)
            notExistJpDbCardList.append(jpCardName)

        index += 1

#    print("oldIdCardNameTables")
#    print(oldIdCardNameTables)
#    print("----------")
#    print("notExistJpDbCardList")
#    print(notExistJpDbCardList)
#    print("----------")

    c.close()


def updateCardIdBycardNameCorTablesWithId(idCardNameTables):
    # データベースに接続する
    conn = sqlite3.connect(FILE_NAME_JP_CARD_DB)
    c = conn.cursor()

    index = 0
    # IDの書き換え
    for idCardNameTable in idCardNameTables:
        cardId = idCardNameTable[index][0]
        jpCardName = idCardNameTable[index][1]

        sqlUpdateDatas = 'UPDATE datas SET id = ' + \
            cardId + ' WHERE name = ' + jpCardName
        c.execute(sqlUpdateDatas)

        sqlUpdateTexts = 'UPDATE texts SET id = ' + \
            cardId + ' WHERE name = ' + jpCardName
        c.execute(sqlUpdateDatas)

        index += 1

    # 挿入した結果を保存（コミット）する
    conn.commit()

    # データベースへのアクセスが終わったら close する
    conn.close()


createOldIdTables(FILE_NAME_JP_CARD_DB, createCardIdTables(
    FILE_NAME_CARDNAME_CORRESPONDENCE_TABLE_WITH_ID))
