#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 02:07:40 2023

@author: pablo
"""


import lxml
import re
import unidecode
from wordsmagic import wordsMagic, exactMatcher, replacementSet
from parser import Notificacion

with open('apellidos_arg.csv', 'r') as f:
	apellidosArg = sorted([x.split(',')[1].strip('\n') for x in f.readlines()])

with open('nombres_arg.csv', 'r') as f:
	nombresArg = [x.split(',')[1].strip('\n') for x in f.readlines()]


def normalizarTexto(text):
	return ''.join( [ (unidecode.unidecode(x) if len(unidecode.unidecode(x))==1 else '?') for x in text ]  ).upper()


def contarMayusculas(texto):
	mayus = re.findall('[A-Z]', unidecode.unidecode( texto ) )
	return len(mayus)

def encontrarPalabrasMagicas(texto, PALABRAS, reemplazantes=('::::', '::::')):
	matchs, matchsErr = PALABRAS.match(texto)
	reemplazos = set()
	if matchs: #hits exactos
		for w in matchs.keys():
			ids = matchs[w]
			
			if len(w)<6: #palabras cortas: que haya al menos una mayúscula y estar aislado (non-char cerca), ej: " JUaN,"
				prioridad = 1
				for i,f in ids:
					#print(i,f, ' :: ', texto[i:f], '::', w)
					if contarMayusculas(texto[i:f])>=1 and ((i==0 or not texto[i-1].isalpha()) and (f==len(texto) or not texto[f].isalpha())):
						reemplazos.add( ((i,f), (reemplazantes[0], prioridad)) )
			else: #palabras largas: que haya al menos una mayúscula
				prioridad = 0
				for i,f in ids:
					if contarMayusculas(texto[i:f])>=1:
						reemplazos.add( ((i,f), (reemplazantes[0], prioridad)) )
				
	if matchsErr: #para los hits dudosos
		for w in matchsErr.keys():
			ids = matchsErr[w]
			if len(w)<6: #palabras cortas, hit dudoso: chau
				continue
			else: #palabras largas: baja prioridad...
				prioridad = 2
				for i,f in ids:
					#...al menos una mayúsculas y estar asilada
					if contarMayusculas(texto[i:f])>=1 and ((i==0 or not texto[i-1].isalpha()) and (f==len(texto) or not texto[f].isalpha())):
						reemplazos.add( ((i,f), (reemplazantes[1], prioridad)) )

	return reemplazos


def anonimizarTexto(texto):
	if len(texto)<4:
		return texto
	listaDeReemplazos = []
	
	if POSIBLESNOMBRES is not None:
		listaDeReemplazos += encontrarPalabrasMagicas(texto, POSIBLESNOMBRES, ('@EEE@', '#EEE#'))
	
	listaDeReemplazos +=  encontrarPalabrasMagicas(texto, APELLIDOSLAR, ('@APEL@', '#APEL#'))
	listaDeReemplazos +=  encontrarPalabrasMagicas(texto, NOMBRESLAR, ('@NOML@', '#NOML#'))
	
	listaDeReemplazos +=  encontrarPalabrasMagicas(texto, APELLIDOSCOR, ('@APEC@', '@APEC@'))
	listaDeReemplazos +=  encontrarPalabrasMagicas(texto, NOMBRESCOR, ('@NOMC@', '@NOMC@'))
	
	
	R = replacementSet( listaDeReemplazos )
	mejoresCoberturas = R.computeMaximumReplacementSet()
	
	if len(mejoresCoberturas)>1:
		# computar el reemplazo prioritario
		prioridades = [sum([intervalo[1][1] for intervalo in cobertura]) for cobertura in mejoresCoberturas]
		reemplazos = mejoresCoberturas[prioridades.index(min(prioridades))]
	elif len(mejoresCoberturas) == 1:
		reemplazos = mejoresCoberturas[0]
	else:
		reemplazos = []
	#print(reemplazos)
	#print(R.data)
	
	#if len(reemplazos)==1:
	#	return texto
	
	# rellenar baches
	if len(reemplazos) > 1:
		baches = []
		caracteresModificados = 0 #cuento para calcular el % de texto que liquidé
		cur = 0
		for i in range(len(reemplazos)):
			(a,b) = reemplazos[i][0]
			caracteresModificados += (b-a)
			
			if a-cur < 6 and a>cur:
				tachado = re.sub('[A-Z]', 'X', normalizarTexto(texto[cur:a]))
				baches.append(((cur,a), (tachado, 1)))
				caracteresModificados += (a-cur)
			cur=b
				
		reemplazos += baches
		
		# tachado global en caso de estar tachando más del 70% del string
		if caracteresModificados > 0.7*len(texto):
			texto = re.sub('[A-Z]', 'X', normalizarTexto(texto))
		
		reemplazos.sort(key=lambda x: x[0][0])
	
	cur = 0
	out = ''
	for (a,b),r in reemplazos:
		out += texto[cur:a] + r[0]
		cur = b
	
	out += texto[cur:]
	return out


noReemplazar = ' buenos aires direccion general de cultura y educacion de la provincia de buenos aires ley bs as suprema '
#noReemplazar+= 'DIRECCION GENERAL DE CULTURA Y EDUCACION DE LA PROV DE BS AS ley '
#noReemplazar+= 'SUPERINTENDENCIA DE RIESGOS DEL TRABAJO suprema corte organo calle '

NOMBRESLAR = wordsMagic([x for x in nombresArg if len(x)>=6], normalizarTexto)
match, matchErr = NOMBRESLAR.match(noReemplazar)
# quitar los match exactos
NOMBRESLAR.removeWords( list(match.keys()) + list(matchErr.keys()) )

# y agregar los parciales a la lista de nombres para macheo exacto
NOMBRESCOR = exactMatcher([x for x in nombresArg + list(matchErr.keys()) if len(x)>2 and len(x)<6], normalizarTexto) #Nombres de menos de tres letras :: AFUERA
match, matchErr = NOMBRESCOR.match(noReemplazar)
NOMBRESCOR.removeWords(list(match))

APELLIDOSLAR = wordsMagic([x for x in apellidosArg if len(x)>=6], normalizarTexto)
#idem nombres
match, matchErr = APELLIDOSLAR.match(noReemplazar)
# quitar los match exactos
APELLIDOSLAR.removeWords( list(match.keys()) + list(matchErr.keys()) )

APELLIDOSCOR = exactMatcher([x for x in apellidosArg + list(matchErr.keys()) if len(x)>2 and len(x)<6], normalizarTexto) #Apellidos de menos de tres letras :: AFUERA
match, matchErr = APELLIDOSCOR.match(noReemplazar)
APELLIDOSCOR.removeWords(list(match.keys()))

notificaciones = lxml.etree.parse('cedulas_demandas_utf8.xml')
out = lxml.etree.Element("Notificaciones")

for j,noti in enumerate(notificaciones.getroot()[:]):
	p = Notificacion(noti, anonimizarTexto)
	print(p.posiblesNombres)
	POSIBLESNOMBRES = exactMatcher( p.posiblesNombres, normalizarTexto )
	p.anonimizarCaratula()
	p.anonimizarTexto()
 	
	out.append(p.compilarXML())

with open('demandas_anonimas.xml', 'wb') as f:
 	f.write( lxml.etree.tostring(out, pretty_print=True) )