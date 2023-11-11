#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 03:17:47 2023

@author: pablo
"""

# parsers
import lxml
from bs4 import BeautifulSoup
from bs4.element import NavigableString

# tools
import re
from copy import deepcopy

from wordsmagic import exactMatcher


textParsers = [lambda x: BeautifulSoup(x,  'html5lib'), lambda x: BeautifulSoup(x,  features="xml")]
#textParsers = [lambda x: BeautifulSoup(x,  'html5lib')]

def anonimizarEmail(direccion, reemplazo):
	dominio = direccion.strip().split('@')[1]
	return f'{reemplazo}@{dominio}'


def modifyBSText(obj, func):
	if isinstance(obj, NavigableString):
		obj.replaceWith( func(obj.string) )
	else:
		try:
			for child in obj.contents:
				modifyBSText(child, func)
		except:
			None

def generarNombresUsandoString(testString):
	lista = set([])
	lista.add(testString.strip())
	
	testString = ''.join([(c if c.isalpha() else ' ') for c in testString]).strip()
	
	palabras = testString.split(' ')
	
	for i,w in enumerate(palabras):
		w = w.strip()
		if len(w)>4 and ( 'OTR' not in w.upper() ): # nombre o apellido de largo razonable
			lista.add(w)
			continue

	return lista


class Notificacion:
	def __init__(self, xmlTreeInput, funcionAnonimizarTexto):
		
		self.organismo = deepcopy( xmlTreeInput.find('Organismo') )
		self.caratula =  deepcopy( xmlTreeInput.find('Caratula') )
		self.destinatario = deepcopy( xmlTreeInput.find('Destinatario') )
		self.numeroCausaOrganismo = deepcopy( xmlTreeInput.find('NumeroCausaOrganismo') )
		self.fechaNotificacion = deepcopy( xmlTreeInput.find('FechaNotificacion') )
		
		self.fechaPrimeraFirma = deepcopy( xmlTreeInput.find('TextoNotificado').find('TextoFirmado').find('FechaPrimeraFirma') )
		texto = xmlTreeInput.find('TextoNotificado').find('TextoFirmado').find('Texto').text
		
		parseLen = 0
		for func in textParsers:
			try:
				if len( func(texto).text ) > parseLen:
					self.texto = func( texto )
					parseLen = len( func(texto).text )
				#break
			except:
					print('ALTA CAGA')
					continue
	
	
		## OPCIONALES :: a veces aparecen metadatos de donde pueden sacarse los nombres, ej. en Referencias y en Carátula
		posiblesNombres = []
		
		# referencias
		self.referencias = deepcopy( xmlTreeInput.find('TextoNotificado').find('TextoFirmado').find('Referencias') )
		
		if self.referencias is not None:
			keyIncluye = ['APELLIDO', 'NOMBRE'] # aparece mucho la key "APELLIDO y NOMBRE del Abogado"
			buscarKeys = ['ABOGADO']
			excluirSiAparece = ['BUENOS', 'AIRES', 'DIRECCION', 'GENERAL', 'PROVINCIA', 'BS', 'AS']
			for R in self.referencias:
				clave = R.get('nombre').upper()
				valor = R.get('valor').upper()
				
				claveTienePotencial = any([k in clave for k in keyIncluye])
				claveEsBuscada      = any([k in clave for k in buscarKeys])
				aparecenExcluidos   = any([val in valor for val in excluirSiAparece])
				
				if claveTienePotencial and claveEsBuscada and not aparecenExcluidos:
 					posiblesNombres.append( R.get('valor') )


		#en caratula
		if 'C/' in self.caratula.text.upper():
			stringPosibleNombre = self.caratula.text.split('C/')[0]
			posiblesNombres.append( stringPosibleNombre )
			
		
		self.posiblesNombres = []
		for S in posiblesNombres:
			self.posiblesNombres += generarNombresUsandoString(S)
		
		
		#Funciones para anonimizar texto
		self.moreMatchs = exactMatcher( self.posiblesNombres, lambda x: x.upper() )
		self.funcionAnonimizarTexto = funcionAnonimizarTexto
		
		
	def anonimizarOrganismo(self):
		orgKeys = [k for k in self.organismo.keys() if 'idorg' in k.lower()]
		for k in orgKeys:
			self.organismo.set(k, '0')
			self.organismo.text = 'ORGANISMO'
	
	def anonimizarCaratula(self):
		self.caratula.text = self.funcionAnonimizarTexto( self.caratula.text )
	
	def anonimizarDestinatario(self):
		destinatarios = []
		for d,destinatario in enumerate(self.destinatario.text.split(',')):
			if '@' in destinatario:
				destinatarios.append(anonimizarEmail(destinatario, f'DESTINATARIO{d+1}'))
			else:
				destinatarios.append(f'DESTINATARIO{d+1}')
		
		self.destinatario.text = ', '.join(destinatarios)
			
	def anonimizarNumeroCausaOrganismo(self):
		for k in self.numeroCausaOrganismo.keys():
			self.numeroCausaOrganismo.set(k, '0'*len(self.numeroCausaOrganismo.get(k)) )
		
		self.numeroCausaOrganismo.text = '0'*len(self.numeroCausaOrganismo.text)
	
	def anonimizarFechaNotificacion(self):
		self.fechaNotificacion.text = re.sub(r'\d', 'D', self.fechaNotificacion.text)
	
	def anonimizarFechaPrimeraFirma(self):
		self.fechaPrimeraFirma.text = re.sub(r'\d', 'D', self.fechaPrimeraFirma.text)
	
	def anonimizarTexto(self):
		modifyBSText(self.texto, self.funcionAnonimizarTexto)
	
	def compilarXML(self, filename=None):
		root = lxml.etree.Element("Notificacion")
		for elem in [self.organismo, self.caratula, self.numeroCausaOrganismo, self.destinatario, self.fechaNotificacion]:
			if (elem is not None):
				root.append( elem )
		
		textoNotificado = lxml.etree.Element("TextoNotificado")
		textoFirmado = lxml.etree.Element("TextoFirmado")
		if (self.fechaPrimeraFirma is not None):
			textoFirmado.append( self.fechaPrimeraFirma )
		if (self.texto is not None):
			Texto = lxml.etree.Element("Texto")
			Texto.text = self.texto.decode()
			textoFirmado.append( Texto )
		
		textoNotificado.append(textoFirmado)
		root.append(textoNotificado)
		
		if filename:
			with open(filename, 'wb') as f:
			    f.write( lxml.etree.tostring(root, pretty_print=True) )
		
		return root
		
	
	def anonimizarTodo(self):
		if self.organismo is not None:
			self.anonimizarNumeroCausaOrganismo()
		if self.caratula is not None:
			self.anonimizarCaratula()
		if self.numeroCausaOrganismo is not None:
			self.anonimizarNumeroCausaOrganismo()
		if self.destinatario is not None:
			self.anonimizarDestinatario()
		if self.fechaNotificacion is not None:
			self.anonimizarFechaNotificacion()
		
		if self.fechaPrimeraFirma is not None:
			self.anonimizarFechaPrimeraFirma()
		if self.texto is not None:
			self.anonimizarTexto()