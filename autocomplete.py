# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 10:09:50 2020

@author: bmart
"""

import sqlite3
from os import listdir
from os.path import isfile, join
import time
import random
import re

def deText(text):
    text = text.lower()
    trans = str.maketrans('áéíóúü', 'aeiouu')
    text = text.translate(trans) #remover tildes
    text = ''.join([i for i in text if not i.isdigit()]) #remover números
    text = re.sub('\W+', '', text)
    return text
#deText("-tamaño\n")

class db():
    def __init__(self):
        self.dbName = "palabras.db"
        self.tableName = "palabras"
        self.c = 0
        self.conn = 0
        self.createTable()
        
    def createTable(self):
        self.connectDB()
        sql = '''CREATE TABLE IF NOT EXISTS palabras (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      word TEXT NOT NULL,
                                                      uses NUMERIC NOT NULL DEFAULT 1)'''
        self.c.execute(sql)
        self.conn.commit()
        self.closeDB()
    
    def connectDB(self):
        self.conn = sqlite3.connect(self.dbName)
        self.c = self.conn.cursor()
    
    def closeDB(self):
        self.c.close()
        self.conn.close()

    def insertWord(self, word):
        #Verificar si la palabra existe
        exist = self.getWord(word)
        if not exist: #Si no existe la palabra
            self.connectDB()
            palabra = [word][0].lower()
            sql = '''INSERT INTO palabras (word) VALUES (?)'''
            self.c.execute(sql, [palabra])
            self.conn.commit()
            self.closeDB()
        else:
            raise Exception("Esta palabra ya existe (", word, ")")
    
    def getWordId(self, number):
        '''
        Obtener una palabra por el ID
        '''
        self.connectDB()
        sql = "SELECT * FROM palabras WHERE id==?"
        self.c.execute(sql, [str(number)])
        for word in self.c:
            print(word)
        self.conn.commit()
        self.closeDB()
        return word
    
    def getWord(self, word):
        '''
        Obtener si una palabra existe o no
        '''
        self.connectDB()
        sql = "SELECT EXISTS(SELECT * FROM palabras WHERE word = ? LIMIT 1)"
        self.c.execute(sql, [word.lower()])
        response = True
        for result in self.c:
            if result[0] == 1:
                response = True
            else:
                response = False
        self.conn.commit()
        self.closeDB()
        return response

    def getUsesWord(self, word):
        '''
        Obtener el número de usos de una palabra
        '''
        self.connectDB()
        sql = "SELECT uses FROM palabras WHERE word = ?"
        self.c.execute(sql, [word.lower()])
        for result in self.c:
            response = result[0]
        self.conn.commit()
        self.closeDB()
        return response
    
    def setUsesWord(self, word, uses):
        '''
        Cambiar el numero de usos de una palabra
        '''
        self.connectDB()
        sql = "UPDATE palabras SET uses=? WHERE word=?"
        self.c.execute(sql, [uses, word.lower()])
        self.conn.commit()
        self.closeDB()

    def setProbWord(self, word, prob):
        '''
        Cambiar la probabilidad de uso de una palabra
        '''
        self.connectDB()
        sql = "UPDATE palabras SET prob=? WHERE word=?"
        self.c.execute(sql, [prob, word.lower()])
        self.conn.commit()
        self.closeDB()
    
    def getWordInitials(self, initials):
        '''
        Obtener palabras por sus letras iniciales
        '''
        self.connectDB()
        sql = "select * from palabras where word like ? ORDER BY uses DESC"
        self.c.execute(sql, [initials.lower()+"%"])
        words = list()
        for word in self.c:
            words.append(word)
        self.conn.commit()
        self.closeDB()
        return words
    
    def getAllWords(self):
        '''
        Obtener TODAS las palabras
        '''
        self.connectDB()
        sql = "select * from palabras"
        self.c.execute(sql)
        words = list()
        for word in self.c:
            words.append(word[1])
        self.conn.commit()
        self.closeDB()
        return words
    
class wordManage():
    def __init__(self):
        self.files = list()
        
    def readAllFiles(self):
        self.files = [f for f in listdir("words") if isfile(join("words", f))]
    
    def getWordsList(self):
        wordsList = list()
        database = db()
        for file in self.files:
            with open("words/"+file, encoding = "utf-8", mode = 'r') as f:
                text = f.readlines()
                wordsList.append(text)
                numberWords = 0
        for wordList in wordsList:
            numberWords += len(wordList)
        print("Número de palabras aparante: ", numberWords)
        
        completed = 0;
        for wordList in wordsList:
            for word in wordList:
                try:
                    toSave = word.split(',')[0].rstrip()
                    toSave = deText(toSave)
                    database.insertWord(toSave)
                except Exception as error:
                    print(error)
                completed+=1
                print(str(completed)+"/"+str(numberWords)+"  --  "+str((completed/numberWords)*100)+"%", end="\r")

class AutoComplete(object):
    def __init__(self):
        pass

    def saveSentence(self, sentence):
        '''
        Guardar cada una de las palabras que tiene la oración
        '''
        #Tratamiento al texto
        sentence = deText(sentence)
        newWords = sentence.split(" ") #separar palabras
        database = db()
        words = list()
        words = database.getAllWords()#obtener las palabras actuales
        actualNumberWords = len(words)#obtener el # de palabras actuales

        newNumberWords = len(newWords)#obtener el # de palabras nuevas
        
        totalWords = list(set([*newWords, *words]))
        newTotalWords = len(totalWords) #obtener el número total de palabras

        for word in newWords:
            toSave = re.sub('\W+', '', word) #palabra a guardar
            try:
                if not len(toSave)==0:
                    database.insertWord(toSave)
                else:
                    continue
            except Exception as error:
                #Si la palabra existe, sumar un uso
                uses = database.getUsesWord(toSave)#Leer numero de usos
                uses+=1#Sumar 1 uso
                database.setUsesWord(toSave, uses)#Guardar numero de usos
        
        #self.calculateAndSaveProb() #Guardar probabilidad

    def calculateAndSaveProb(Self):
        '''
        Calcular y guardar la probabilidad de uso de cada palabra
        '''
        database = db()
        words = database.getAllWords() #obtener todas las palabras en la base de datos
        numberWords = len(words) #obtener su cantidad
        for word in words:
            uses = database.getUsesWord(word)
            prob = uses/numberWords #Hacer probabilidad de uso
            database.setProbWord(word, prob) #guardar probabilidad

    def showOptions(self, initials):
        '''
        Mostrar las 3 primeras opciones
        '''
        database = db()
        words = database.getWordInitials(initials)
        opciones = ["", "", ""]
        for i, option in enumerate(words[:3]):
            opciones[i] = option[1]
        
        #Ordenar opciones por probabilidad
        return opciones
    
    def listToSentence(self, lista):
        sentence = str()
        for word in lista:
            sentence+=word+" "
        return sentence

class corrector(object):
    '''Corrector de palabras utilizando la distancia de Levenshtein'''

def createDataBase():
    '''Create DataBase apartir del diccionario de palabras'''
    words = wordManage()
    words.readAllFiles()
    a = time.time()
    words.getWordsList()
    b = time.time()
    result = b-a
    print(result)

#createDataBase()



#Escribir una oración
#autocomplete = AutoComplete()
#oracion = "Dirigir empresas digitales exige formación multidisciplinar. Aprende las competencias necesarias en este Master."
#autocomplete.saveSentence(oracion)
