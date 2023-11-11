#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 01:33:51 2023

@author: pablo
"""
import lxml
from collections import Counter
from parser import Notificacion
import pickle


# #no está codificado en utf-8
# demandas = open('cedulas_demandas.xml', 'r', encoding='latin-1').read()
# with open('cedulas_demandas_utf8.xml', 'w', encoding='utf-8') as f:
# 	f.write(demandas)


notificaciones = lxml.etree.parse('cedulas_demandas_utf8.xml')
out = lxml.etree.Element("Notificaciones")

def removerNoAlfanumericos(texto):
	return ''.join([(c if c.isalnum() else  ' ') for c in texto])

palabrasTotales = Counter()
for j,noti in enumerate(notificaciones.getroot()[:]):
	p = Notificacion(noti, lambda x: x)
	palabras = [x.strip() for x in removerNoAlfanumericos(p.texto.text).split(' ') if len(x)>0]
	
	palabrasTotales += Counter(palabras)


with open('palabrasTotales.pkl', 'wb') as f:
	pickle.dump(palabrasTotales, f)