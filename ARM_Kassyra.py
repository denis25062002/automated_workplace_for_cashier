import sqlite3
import PySimpleGUI as sg
import sys
import time

db = sqlite3.connect("shop.db")
cursor = db.cursor()

barcodeItemCode_1 = 20
barcodeItemCode_2 = 28

cursor.execute("""CREATE TABLE IF NOT EXISTS Store (
                storeID INTEGER PRIMARY KEY AUTOINCREMENT,  
                zipCode INTEGER NOT NULL CHECK(zipCode > 0 AND zipCode < 1000000),
                region TEXT NOT NULL,
                city TEXT NOT NULL,
                street TEXT NOT NULL,
                building TEXT NOT NULL
                )
            """)

cursor.execute("""CREATE TABLE IF NOT EXISTS Item (
                storeID INTEGER,  
                itemName TEXT,
                itemBarcode INTEGER,
                itemAmount REAL,
                itemPrice REAL,
                itemDiscount REAL,
                FOREIGN KEY (storeID) REFERENCES Store (storeID)
                )
            """)

cursor.execute("""CREATE TABLE IF NOT EXISTS Cashier (
                lastName TEXT,
                firstName TEXT,
                patronymic TEXT,
                cashierID INTEGER PRIMARY KEY AUTOINCREMENT,
                cashierPswd TEXT,
                storeID INTEGER,
                FOREIGN KEY (storeID) REFERENCES Store (storeID)
                )
            """)

cursor.execute("""CREATE TABLE IF NOT EXISTS CashReceipt (
                time TEXT,
                date TEXT,
                storeID INTEGER,
                cashierName TEXT,
                itemNameAll TEXT,
                itemBarcodeAll TEXT,
                itemAmountAll TEXT,
                itemPriceAll TEXT,
                itemDiscountAll TEXT,
                itemTotalAll TEXT,
                totalMoney REAL,
                cardNumber INTEGER
                )
            """)

class Cashier:
    def __init__(self, lastName, firstName, patronymic, cashierID, cashierPswd, storeID):
        self.__lastName = lastName
        self.__firstName = firstName
        self.__patronymic = patronymic
        self.__cashierID = cashierID
        self.__cashierPswd = cashierPswd
        self.__storeID = storeID
              
    def print(self):
        info1 = "Кассир " + str(self.__lastName) + " " + str(self.__firstName) + " " + str(self.__patronymic) + "\nНомер сотрудника " + str(self.__cashierID).zfill(6)
        return info1
       
    def getStoreID(self):
        return self.__storeID
    
    def auth(self, getCashierID, getCashierPswd):
        cursor.execute("SELECT lastName, firstName, patronymic, storeID FROM Cashier WHERE cashierID = ?", (getCashierID, ))
        self.__lastName, self.__firstName, self.__patronymic, self.__storeID = cursor.fetchone()
        self.__cashierID = getCashierID
        self.__cashierPswd = getCashierPswd
        
    def getName(self):
        return (str(self.__lastName) + " " + str(self.__firstName) + " " + str(self.__patronymic))

class Store:
    def __init__(self, storeID, zipCode, region, city, street, building):
        self.__storeID = storeID
        self.__zipCode = zipCode
        self.__region = region
        self.__city = city
        self.__street = street
        self.__building = building
     
    def authStore(self, getStoreID):
        cursor.execute("SELECT zipCode, region, city, street, building FROM Store WHERE storeID = ?", (getStoreID, ))    
        curTemp = cursor.fetchone()
        self.__storeID = getStoreID
        self.__zipCode = curTemp[0]
        self.__region = curTemp[1]
        self.__city = curTemp[2]
        self.__street = curTemp[3]
        self.__building = curTemp[4]

    def print(self):
        return("Адрес: " + str(self.__street) + ", " + 
               str(self.__building) + ", " + 
               str(self.__city) + ", " + 
               str(self.__region) + ", " + 
               str(self.__zipCode) + 
               "\nМагазин № " + str(self.__storeID))
        
class Item:
    def __init__(self, storeID, itemBarcode, itemName, itemPrice, itemAmount, itemDiscount, itemTotal):
        self.storeID = storeID
        self.itemBarcode = itemBarcode
        self.itemName = itemName
        self.itemPrice = itemPrice
        self.itemAmount = itemAmount
        self.itemDiscount = itemDiscount
        self.itemTotal = self.itemPrice * self.itemAmount * (1 - (self.itemDiscount / 100)) 
       
    def getList(self):
        return( [self.itemBarcode, self.itemName, self.itemPrice, self.itemAmount, self.itemDiscount, round(self.itemTotal, 2)] )
    
    def isItemExists(self, inputBarcode):
        if inputBarcode == self.itemBarcode:
            return True
        else:
            return False
        
    def updateAmount(self, inputAmount):
        self.itemAmount += inputAmount
        self.itemTotal = self.itemPrice * self.itemAmount * (1 - (self.itemDiscount / 100))

def scanBarcode():
    inputLayout = [  [sg.Text('Введите штрих-код')],
            [sg.InputText()],
            [sg.Button('Ввод'),  sg.Button('Отмена')] ]
    window = sg.Window('Ввод штрих-кода', inputLayout)
    
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Отмена': 
            return -1
        
        if event == 'Ввод':
            try:
                barcode = int(values[0])
                
                if ((int(barcode / pow(10, 11))) == barcodeItemCode_1) or ((int(barcode / pow(10, 11))) == barcodeItemCode_2):
                    if isBarcodeCRCCorrect(barcode) == True:
                        window.close()
                        return barcode
                
                else:
                    sg.popup_ok("Некорректный ввод",  title="Ошибка")

            except ValueError:
                sg.popup_ok("Некорректный ввод",  title="Ошибка")
                     
def isBarcodeCRCCorrect(bc):
    cet = (int(bc/pow(10,11))%10+ # суммируем цифры на четных позициях и умножаем рез-т на 3
          int((bc/pow(10,9))%10)+
          int((bc/pow(10,7))%10)+
          int((bc/pow(10,5))%10)+
          int((bc/pow(10,3))%10)+
          int((bc/pow(10,1))%10)) * 3 
    necet =(int(bc/pow(10,12))%10+ # суммируем цифры на нечетных позициях
          int((bc/pow(10,10))%10)+
          int((bc/pow(10,8))%10)+
          int((bc/pow(10,6))%10)+
          int((bc/pow(10,4))%10)+
          int((bc/pow(10,2))%10))
    crc = (int((cet + necet)/10) + 1)*10 - (cet + necet)
    # контрольное число - разница между окончательной суммой и ближайшим к ней наибольшим числом, кратным десяти
    if int((bc/pow(10,0))%10) == crc:
        return True
    else:
        sg.popup_ok("Неверная контрольная сумма!",  title="Ошибка")
    
def makeBarcodeWithCRC(bc_12):
    cet=(int(bc_12/pow(10,10))%10+
          int((bc_12/pow(10,8))%10)+
          int((bc_12/pow(10,6))%10)+
          int((bc_12/pow(10,4))%10)+
          int((bc_12/pow(10,2))%10)+
          int((bc_12/pow(10,0))%10))*3
    necet=(int(bc_12/pow(10,11))%10+
          int((bc_12/pow(10,9))%10)+
          int((bc_12/pow(10,7))%10)+
          int((bc_12/pow(10,5))%10)+
          int((bc_12/pow(10,3))%10)+
          int((bc_12/pow(10,1))%10))
    crc = (int((cet + necet)/10) + 1)*10 - (cet + necet)
    bc_13 = bc_12 * 10 + crc
    return bc_13

def isItemWeight(barcode):
    if int(barcode/pow(10,11)) == barcodeItemCode_1:
        return False
    else:
        return True

def authCashier():
    loginLayout = [ [sg.Text('Введите свой идентификатор и пароль в поля ниже и нажмите "Ввод".')],
                   [sg.Text('ID:         '), sg.Input(key='-ID-')],
                   [sg.Text('Пароль: '), sg.Input(key='-Pswd-')],
                   [sg.Button('Ввод')]
                   ]
    loginWindow = sg.Window('Авторизация', loginLayout)
    
    while True:
        event, values = loginWindow.read()
        
        if event == sg.WIN_CLOSED: 
            sys.exit(1)
        
        if event == 'Ввод':
            cursor.execute("SELECT cashierPswd FROM Cashier WHERE cashierID = ?", ((int(values['-ID-'])), ))
            getPswd = cursor.fetchone()
            
            if getPswd:
                if values['-Pswd-'] != '':
                    if int(getPswd[0]) == int(values['-Pswd-']):
                        successPopup = sg.popup_ok("Авторизация прошла успешно",  title="Успех!")
                        currCashier.auth(int(values['-ID-']), int(values['-Pswd-']))
                        loginWindow.close()
                        currStore.authStore(currCashier.getStoreID())
                        mainCheckout()
                        return 0
                    else:
                        errorPopup = sg.popup_ok("Неправильный логин и/или пароль!",  title="Ошибка")
                        
            else:
                 errorPopup = sg.popup_ok("Неправильный логин и/или пароль!",  title="Ошибка")

def returnWeight(barcode):
    weight = ((int(barcode / 10)) % pow (10, 5))
    return weight

def makeBarcodeFromWeight(barcode):
    barcode = str(int(barcode / pow(10, 6))) + "00000"
    barcode = makeBarcodeWithCRC(int(barcode))
    return barcode

def getCardNumber():
    cardNumber = sg.popup_get_text('Введите номер карты:')
    try:
        int(cardNumber)
        if len(cardNumber) == 16:
            cardNumberOutput = int(cardNumber)
        else:
            errorPopup = sg.popup_ok("Некорректный ввод!",  title="Ошибка")
            cardNumberOutput = None
    except:
        errorPopup = sg.popup_ok("Некорректный ввод!",  title="Ошибка")
        cardNumberOutput = None
    finally:
        return cardNumberOutput

def enterWeigthLastItem(isItemWeight):
    outputWeight = sg.popup_get_text('Укажите количество товара:')
    try:
        if isItemWeight == True:
            outputWeight = float(outputWeight)
            if outputWeight <= 0:
                outputWeight = None
        if isItemWeight == False:
            outputWeight = int(outputWeight)
            if outputWeight <= 0:
                outputWeight = None
    except:
        errorPopup = sg.popup_ok("Некорректный ввод!",  title="Ошибка")
        outputWeight = None
    finally:
        return outputWeight

def printCashReceipt(getTime, getDate, getStoreID):
    cursor.execute("""SELECT cashierName,
                   itemNameAll,
                   itemAmountAll,
                   itemPriceAll,
                   itemDiscountAll,
                   itemTotalAll,
                   totalMoney,
                   cardNumber
                   FROM CashReceipt WHERE time = ? AND date = ? AND storeID = ?""", 
                   (getTime, getDate, getStoreID ))
    curTemp = cursor.fetchone()
    cursor.execute("""SELECT zipCode, region, city, street, building from Store WHERE storeID = ?""", (getStoreID, ))
    curTempName = cursor.fetchone()
    storeName = str(curTempName[0]) + ", " + curTempName[1] + ", " + curTempName[2] + "\n" + curTempName[3] + ", " + curTempName[4]
    
    print("Кассовый чек\n")
    print(storeName)
    print("-"*20)
    print("Дата:" + " " * 15 + getDate + " " + getTime)
    print("Кассир:" + " " * 13 + curTemp[0])
    print("Банковская карта:" + " " * 3 + "*" + str(curTemp[7] % 10000))
    print("-"*20)
    
    itemNameAll = curTemp[1].strip('][').split(', ')
    itemNameAll = [s[1:-1] for s in itemNameAll]
    itemAmountAll = curTemp[2].strip('][').split(', ')
    itemPriceAll = curTemp[3].strip('][').split(', ')
    itemDiscountAll = curTemp[4].strip('][').split(', ')
    itemTotalAll = curTemp[5].strip('][').split(', ')

    for i in range(len(itemNameAll)):
        itemPriceWithDiscount = str(float('{:.2f}'.format( float(itemPriceAll[i]) * (1 - float(itemDiscountAll[i]) * 0.01) )))
        itemAmountAll[i] = str(float('{:.2f}'.format( float(itemAmountAll[i]) )))
        print("   ", (i + 1), itemNameAll[i])
        print(itemAmountAll[i] + " X " + str(itemPriceWithDiscount) + " руб.")
        print("    = " + str(itemTotalAll[i]) + " руб.")
        print("-" * 20)
        
    print("Итог:", curTemp[6], "руб.")
   
def mainCheckout():

    tableData = []
    itemList = []
    headings = ['Штрих-код','Наименование','Цена, руб.','Кол-во','Скидка, %','Сумма, руб.']
    totalMoney = 0
    totalMoneyString = 'Сумма: ' + "{:.2f}".format(totalMoney) + ' руб.'
    currTime = time.strftime('%H:%M:%S')
    currDate = time.strftime('%a, %d %b %Y')
    
    def updateTable():
        tableData = [] 
        totalMoney = 0
        for i in range(len(itemList)):
            tableData.append(itemList[i].getList())
            totalMoney += itemList[i].getList()[5]
        totalMoneyString = 'Сумма: ' + "{:.2f}".format(totalMoney) + ' руб.'
        mainWindow['mainTable'].update(tableData)
        mainWindow['totalMoneyString'].update(totalMoneyString)
        return tableData

    mainLayout = [
        [sg.Text(currCashier.print(), font = ('Any, 25')), sg.Text(' ' * 50),
         sg.Text('', key='currentTime', font = ('Any, 25')), sg.Push(), sg.Button('Очистить всё', font = ('Any, 20'), button_color = 'red')],
        [sg.Table(tableData, headings, key = 'mainTable', font = ('Any, 15'), auto_size_columns = False, col_widths = [15, 25, 10, 10, 10, 10], num_rows = 25),
         sg.Button('Ввести штрих-код', font = ('Any, 20'))],
        [sg.Text(currStore.print(), font = ('Any, 15')), sg.Push(), sg.Button('Кол-во', font = ('Any, 20')), sg.Button('Удалить позицию', font = ('Any, 20'))],
        [sg.Text(totalMoneyString, font = ('Any, 25'), key='totalMoneyString'), sg.Push(), sg.Button('Оплата', button_color = 'green', font = ('Any, 20'))]
        ]
    mainWindow = sg.Window('Касса', mainLayout, finalize=True)
    mainWindow['currentTime'].update(time.strftime('%H:%M:%S'))
    
    while True:
        event, values = mainWindow.read(timeout=10)
        
        if event == sg.WIN_CLOSED:
            return 0

        if event == 'Ввести штрих-код':
            currBarcode = scanBarcode()
              
            # если товар весовой
            currItemAmount = 1
            if isItemWeight(currBarcode) == True: 
                currItemAmount = returnWeight(currBarcode) * 0.001
                currBarcode = makeBarcodeFromWeight(currBarcode)
                
            # считываем товар из базы
            itemTemp = Item(0, 0, 0, 0, 0, 0, 0)    
            cursor.execute("SELECT storeID, itemName, itemPrice, itemAmount, itemDiscount FROM Item WHERE itemBarcode = %d AND storeID = %d" % 
                           (currBarcode, currCashier.getStoreID()))
            curTemp = cursor.fetchone()
            if curTemp != None:
                itemTemp = Item(curTemp[0], currBarcode, curTemp[1], curTemp[2], currItemAmount, curTemp[4], 0) 
            
            # проверка на наличие товара в данном магазине
            if (itemTemp.storeID != currCashier.getStoreID()) or (itemTemp.itemAmount > curTemp[3]):
                sg.popup_ok("Товара нет в наличии в данном магазине или некорректный ввод!",  title="Ошибка") 

            else :
               
               # проверка, есть ли данный товар уже в списке
               isItemExistsCheck = False 
               existItemPointer = 0
               for i in range(len(itemList)):
                   if itemList[i].isItemExists(currBarcode) == True:
                       isItemExistsCheck = True
                       existItemPointer = i
                       
               # если нет, то добавляем товар
               if (len(itemList) == 0) or (isItemExistsCheck == False):       
                   itemList.append(itemTemp)  
                   
               # если существует, то добавляем количество
               if isItemExistsCheck == True:  
                   itemList[existItemPointer].updateAmount(currItemAmount)
               tableData = updateTable()
               
        if event == 'Удалить позицию' and len(itemList) != 0 and sg.popup_yes_no('Вы уверены, что хотите удалить последнюю позицию?') == 'Yes': 
            itemList.pop()
            tabbleData = updateTable()
                
        if event == 'Очистить всё' and len(itemList) != 0 and sg.popup_yes_no('Вы уверены, что хотите очистить весь список?') == 'Yes':
            itemList = []
            tableData = updateTable()
                
        if event == 'Кол-во' and len(itemList) != 0:
            enterWeight = enterWeigthLastItem(isItemWeight(itemList[len(itemList) - 1].itemBarcode))
            if enterWeight != None:
                itemList[len(itemList) - 1].itemAmount = enterWeight
                itemList[len(itemList) - 1].itemTotal = itemList[len(itemList) - 1].itemPrice * itemList[len(itemList) - 1].itemAmount * (1 - (itemList[len(itemList) - 1].itemDiscount / 100))
                tableData = updateTable()
                
        if event == 'Оплата' and len(itemList) != 0:
            cardNumber = getCardNumber()
            if cardNumber != None:
                
                currTime = time.strftime('%H:%M:%S')
                currDate = time.strftime('%a, %d %b %Y')

                cashReceiptParam = """INSERT INTO CashReceipt
                (time, date,
                storeID, cashierName,
                itemNameAll,
                itemBarcodeAll,
                itemAmountAll,
                itemPriceAll,
                itemDiscountAll,
                itemTotalAll,
                totalMoney,
                cardNumber)          
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                
                cashReceiptValues = ( currTime, currDate,
                (currCashier.getStoreID()), (currCashier.getName()),
                str([sublist[1] for sublist in tableData]),
                str([sublist[0] for sublist in tableData]),
                str([sublist[3] for sublist in tableData]),
                str([sublist[2] for sublist in tableData]),
                str([sublist[4] for sublist in tableData]),
                str([sublist[5] for sublist in tableData]),
                str(sum(sublist[5] for sublist in tableData)),
                cardNumber )
                
                # создаём запись об операции в базе
                cursor.execute(cashReceiptParam, cashReceiptValues)
                db.commit()
                
                # изменяем количество товара в базе
                currStoreID = currCashier.getStoreID()
                for i in range(len(itemList)):
                  
                    cursor.execute("SELECT itemAmount FROM Item WHERE itemBarcode = %d AND storeID = %d" % 
                    (itemList[i].getList()[0], currStoreID))
                    
                    curTemp = cursor.fetchone()
                    amountToChange = curTemp[0] - itemList[i].getList()[3]
                    
                    cursor.execute("UPDATE Item  SET itemAmount = %f WHERE itemBarcode = %d AND storeID = %d" %
                    (amountToChange, itemList[i].getList()[0], currCashier.getStoreID()))
                    
                    db.commit()
                    
                sg.popup_no_titlebar("Операция завершена успешно!")
                printCashReceipt(currTime, currDate, currCashier.getStoreID())
                itemList = []
                totalMoney = 0
                tableData = updateTable()
        
        mainWindow['currentTime'].update(time.strftime('%H:%M:%S') + "\n" + time.strftime('%a, %d %b %Y'))  
                                             
currStore = Store(0, 123456, 'Регион', 'г. Город', 'ул. Улица', 'д. 1')        
currCashier = Cashier("Фамилия", "Имя", "Отчество", 1, 1, 1)
authCashier()
    
db.close()