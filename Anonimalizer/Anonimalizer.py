import re
import pandas as pd
import numpy as np
from unidecode import unidecode
import csv
from collections import Counter

nombres_ = list(pd.read_csv('Nombres Argentina.csv')['nombres'])
apellidos_= list(pd.read_csv('apellidos_arg.csv')['0'])
# apellidos_ = list(set(list(AP['apellido'])))
provincias_ = list(pd.read_csv('provincias.csv')['nombre'])
municipios_ = list(pd.read_excel('localidades_bsas.xlsx')['Ciudad'])

nombres =[]
for nombre in nombres_:
	nombres.append(unidecode(nombre, 'utf-8'))
    
apellidos = []
for apellido in apellidos_:
	apellidos.append(unidecode(apellido, 'utf-8'))
    
provincias = []
prov_incias = []
for provincia in provincias_:
	provincias.append(unidecode(provincia, 'utf-8'))
	prov_incias.append(re.sub('\s', '_', provincia, flags = re.I))
    
municipios = []
muni_cipios = []
for municipio in municipios_:
	municipios.append(unidecode(municipio, 'utf-8'))
	muni_cipios.append(re.sub('\s', '_', municipio, flags = re.I))

def Anonimalizer(text, title): 
	text = unidecode(text, 'utf-8')
	replacements = []
	conditions = ['(\d*\.\d*\.\d{3})', '(\d*-\d*-\d*)', '\d{11}', '\d*-\d*\*\d{2}','(?<=legajo )(\d*)' , '(?<=domicilio en)(.*?)(?=\\bde\\b)', '( <=tiene domicilio)(.*?)(?=\\bde\\b)|[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+', '\d{2}/\d{2}/\d{4}', '\$\d*\.\d*,\d*', '\d{2}:\d{2}:\d{4}']
	for condition in conditions:
		reemplazo = re.findall(condition, text, re.I)
		if reemplazo != [''] and reemplazo != [('', ''), ('', '')] and reemplazo != []:
			replacements.append(reemplazo) 
		else:pass
	text = re.sub('\$\d*\.\d*,\d*', '$MONTO', text, flags = re.I)
	text = re.sub('(?<=domicilio en)(.*?)(?=\\bde\\b)|(?<=tiene domicilio)(.*?)(?=\\bde\\b)', ' DOMICILIO ', text, flags = re.I)
	text = re.sub('(\d*\.\d*\.\d{3})', ' XX.XXX.XXX', text, flags = re.I)
	text = re.sub('(\d*-\d*-\d*)', 'XX-XXXXXXXX-X', text, flags = re.I)
	text = re.sub('\d{11}', 'XXXXXXXXXXX', text, flags = re.I)
	text = re.sub('\d*-\d*\*\d{2}', 'XXXXXX-X*XX', text, flags = re.I)
	text = re.sub('(?<=legajo )(\d*)', 'XXXXXX-X*XX', text, flags = re.I)
	text = re.sub('\d{2}/\d{2}/\d{4}', 'dd/mm/aaaa', text, flags = re.I)
	text = re.sub('\d{2}:\d{2}:\d{4}', 'hh:mm:ss', text, flags = re.I)
	text = re.sub('[a-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+', 'MAIL', text, flags = re.I)

	
	for i in range(len(provincias)):
		text = re.sub(provincias[i], prov_incias[i], text, flags = re.I)
        
	for i in range(len(municipios)):
		text = re.sub(municipios[i], muni_cipios[i], text, flags = re.I)

		
	freq_apellidos = Counter(apellidos)
	freq_nombres = Counter(nombres)
	for i in re.split('\,|\s', text):
		if i in freq_nombres.keys() and len(i)>2:
			text = re.sub('\\b'+i+'\\b', 'NOMBRE', text, flags = re.I)
			replacements.append(i)
		if i in freq_apellidos.keys() and len(i)>2:
			text = re.sub('\\b'+i+'\\b', 'APELLIDO', text, flags = re.I)
			if i not in replacements:
				replacements.append(i)	
			
	# replacements = list(set(replacements))
	with open(title+'_anonimo.txt', 'w') as f:
		f.write(text)
	with open(title+'_reemplazos.csv','w') as g:
		writer = csv.writer(g)
		for element in replacements:
			if element != []:
				writer.writerow(element)
	return text, replacements
   


