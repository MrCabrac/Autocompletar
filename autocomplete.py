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
        self.wordsDictionaryTableName = "palabras_dict"
        self.sentencesDictonaryTableName = "sentences_dict"
        self.c = 0
        self.conn = 0
        self.createTables()
        
    def createTables(self):
        self.connectDB()
        sql = '''CREATE TABLE IF NOT EXISTS {} (word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      word TEXT NOT NULL,
                                                      uses NUMERIC NOT NULL DEFAULT 1)'''.format(self.wordsDictionaryTableName)
        sql2 = '''CREATE TABLE IF NOT EXISTS {} (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      word TEXT NOT NULL,
                                                      word_id TEXT NOT NULL,
                                                      uses NUMERIC NOT NULL DEFAULT 1,
                                                      FOREIGN KEY (word_id) REFERENCES {}(word_id))'''.format(self.sentencesDictonaryTableName, self.wordsDictionaryTableName)
        self.c.execute(sql)
        self.c.execute(sql2)
        self.conn.commit()
        self.closeDB()
    
    def connectDB(self):
        self.conn = sqlite3.connect(self.dbName)
        self.c = self.conn.cursor()
    
    def closeDB(self):
        self.c.close()
        self.conn.close()

    def insertWord(self, word):
        '''
        Agregar una palabra al diccionario de la base de datos
        '''
        exist = self.getWord(word)#Verificar si la palabra existe
        if not exist: #Si no existe la palabra
            self.connectDB()
            palabra = deText([word][0])
            sql = '''INSERT INTO {} (word) VALUES (?)'''.format(self.wordsDictionaryTableName)
            self.c.execute(sql, [palabra])
            self.conn.commit()
            self.closeDB()
        else:
            raise Exception("Esta palabra ya existe (", word, ")")
    
    def insertRelationedWords(self, word1, word2):
        '''
        Insertar una relacion de palabras para autocompletar en la base de datos
        '''
        print("insertRelationedWords>iniciando")
        info = self.getRelationedWords(word1, word2)
        self.connectDB()
        if not info[0]: #Si la relacion no existe
            print("insertRelationedWords>Guardar")
            wordId = self.getIdFromWord(word2)
            sql = "INSERT INTO {} (word, word_id) VALUES (?, ?)".format(self.sentencesDictonaryTableName)
            self.c.execute(sql, [deText(word1), wordId])
        else:#Sumar a su uso
            print("insertRelationedWords>guardar+1")
            sql = "UPDATE {} SET uses=? WHERE word=?".format(self.sentencesDictonaryTableName)
            self.c.execute(sql, [int(info[1])+1, word1])
        self.conn.commit()
        self.closeDB()   

    def getWordId(self, number):
        '''
        Obtener una palabra por el ID
        '''
        self.connectDB()
        sql = "SELECT * FROM {} WHERE word_id==?".format(self.wordsDictionaryTableName)
        self.c.execute(sql, [str(number)])
        for word in self.c:
            pass
        self.conn.commit()
        self.closeDB()
        return word

    def getIdFromWord(self, word):
        self.connectDB()
        sql = "SELECT * FROM {} WHERE word = ?".format(self.wordsDictionaryTableName, word)
        self.c.execute(sql, [word])
        for response in self.c:
            pass
        return response[0]

    def getWord(self, word):
        '''
        Obtener si una palabra existe o no
        '''
        self.connectDB()
        sql = "SELECT EXISTS(SELECT * FROM {} WHERE word = ? LIMIT 1)".format(self.wordsDictionaryTableName)
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
    
    def getRelationedWords(self, word1, word2):
        '''
        Obterner si la relación de palabras existe o no
        '''
        #Buscar palabra1
        self.connectDB()
        sql = "SELECT * from {} join {} WHERE {}.word_id = {}.word_id".format(self.sentencesDictonaryTableName, self.wordsDictionaryTableName, self.sentencesDictonaryTableName, self.wordsDictionaryTableName)
        self.c.execute(sql)
        complementWords = list()
        inWords = [deText(word1), deText(word2)]
        uses = list()
        for result in self.c:
            complementWords.append([result[1], result[5]])
            uses.append(result[3])
        self.conn.commit()
        self.closeDB()
        try:
            index = complementWords.index(inWords)
        except:
            index = 0
        if inWords in complementWords:
            return (True, uses[index])
        else:
            return (False, index)

    def getUsesWord(self, word):
        '''
        Obtener el número de usos de una palabra
        '''
        self.connectDB()
        sql = "SELECT uses FROM {} WHERE word = ?".format(self.wordsDictionaryTableName)
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
        sql = "UPDATE {} SET uses=? WHERE word=?".format(self.wordsDictionaryTableName)
        self.c.execute(sql, [uses, word.lower()])
        self.conn.commit()
        self.closeDB()

    def getWordInitials(self, initials):
        '''
        Obtener palabras por sus letras iniciales
        '''
        self.connectDB()
        sql = "select * from {} where word like ? ORDER BY uses DESC".format(self.wordsDictionaryTableName)
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
        sql = "select * from {}".format(self.wordsDictionaryTableName)
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
        print("getWordsList>Número de palabras aparante: ", numberWords)
        
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

    def saveRelationatedWords(self, wordsList):
        '''
        Guardar las relaciones entre palabras
        '''
        print("wordsList:", wordsList)
        database = db()
        complements = list()#Obtener todos los pares
        for i, palabra in enumerate(wordsList):
            if i<len(wordsList)-1:
                complements.append([palabra, wordsList[i+1]])
            else:
                break
        #guardar cada complemento
        print("complements:", complements)
        for complement in complements:
            database.insertRelationedWords(complement[0], complement[1])

    def showOptions(self, initials):
        '''
        Mostrar las 3 primeras opciones
        '''
        database = db()
        words = database.getWordInitials(initials)
        opciones = ["", "", ""]
        for i, option in enumerate(words[:3]):
            opciones[i] = option[1]
        print("opciones:", opciones)
        #Ordenar opciones por probabilidad
        return opciones
    
    def showRelationaledWords(self, preWord):
        '''
        Muestra las palabras siguientes que podrían ir
        '''
        db2 = db()
        db2.connectDB()
        sql = "SELECT * FROM {} JOIN {} WHERE {}.word_id = {}.word_id AND {}.word = ? ORDER BY {}.uses DESC".format(db2.sentencesDictonaryTableName,
        db2.wordsDictionaryTableName, db2.sentencesDictonaryTableName, db2.wordsDictionaryTableName, db2.sentencesDictonaryTableName, db2.sentencesDictonaryTableName)
        db2.c.execute(sql, [deText(preWord)])
        opciones = ["", "", ""]
        for i, response in enumerate(db2.c):
            opciones[i] = response[5]
        db2.conn.commit()
        db2.closeDB()
        return opciones

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


#autocomplete = AutoComplete()
#oracion = "hola como estas el dia de hoy"
#autocomplete.saveSentence(oracion)
#oracion = "mama tengo hambre"
#autocomplete.saveSentence(oracion)
#oracion = "mama estoy"
#autocomplete.saveSentence(oracion)