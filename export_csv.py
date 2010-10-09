#-*- coding: UTF-8 -*-
"""Script permettant la génération d'une carte de france découpé en région
avec la quantité de cd vendu par région
Usage
 python generate_map.py fichier.csv
 ou
 python generate_map.py mesVente.csv maCarte.svg

 """
from operator import itemgetter
from itertools import groupby
from xml.dom import minidom
import csv
import sys
import os

#Libellé des champs du csv
field_cp = "CP"
field_pays = "Pays"
fields_product = ["UB-20CD-1004", "UB-CD-1004"]
path_static = os.path.join(os.path.dirname(__file__), 'static')
#nom du fichier de la carte générée
path_save_map = "vente_by_region.svg"

def get_list_vente(path):
    """List des ventes obtenue à partir du fichier csv
    fournit en argument"""
    csvfile = open(path_csv)
    dialect = csv.Sniffer().sniff(csvfile.read(1024))
    csvfile.seek(0)
    return csv.DictReader(csvfile, dialect = dialect)


def get_map_departement_region():
    """Dictionnaire permettant d'avoir la correspondance entre département
    et région française"""
    path_departement_region = os.path.join(path_static, 'departement_region.csv')
    obj_file = open(path_departement_region)
    csv_obj = csv.DictReader(obj_file)
    return dict([(item['departement'], item['region']) for item in csv_obj])

def get_template_carte():
    file_svg_file = open(os.path.join(path_static, 'region.svg'))
    document = minidom.parse(file_svg_file)
    file_svg_file.close()
    return document

if __name__ == '__main__':
    if not len(sys.argv) in ( 2, 3):
        print "Vous devez specifier un fichier csv"
        sys.exit(0)
    if len(sys.argv) == 3:
        path_save_map = sys.argv[2]
    path_csv = sys.argv[1]
    list_vente = get_list_vente(path_csv)
    map_departement_region = get_map_departement_region()

    list_vente_france = []
    for item in list_vente:
        if item[field_pays] == 'France':
            cp = item[field_cp]
            if len(cp) == 5:
                departement = cp[0:2]
                if departement.startswith('0'):
                    departement = departement[1]
                item['region'] =  map_departement_region[departement]
                list_vente_france.append(item)

    #Calcule du nombre de cd par région
    list_vente_france.sort(key = itemgetter('region'))
    vente_by_region = {}
    for region, list_item in groupby(list_vente_france, key = itemgetter('region')):
      list_item = list(list_item)
      new_item = {}
      for product in fields_product:
        new_item['nb_cd_%s' % product] = sum(
            [int(element[product]) for element
                  in list_item if element[product]])
      vente_by_region[region] = new_item['nb_cd_UB-20CD-1004'] * 20 + new_item['nb_cd_UB-CD-1004']

    #Génération d'une carte avec les valeurs du nombre de cd par région
    document = get_template_carte()
    #Couche text
    layer_text = None
    for item in document.getElementsByTagName('g'):
      value_id = item.getAttributeNode('id').value
      if value_id == 'layer_text':
        layer_text = item
        break
    if layer_text:
        for item in layer_text.getElementsByTagName('text'):
          value_id = item.getAttributeNode('id').value
          if value_id and value_id.startswith('text_'):
            region = value_id.split('text_')[1]
              #if region in vente_by_region:
            tspan = [element for element in
                        item.getElementsByTagName('tspan') if element.firstChild][0]
            nb_cd = vente_by_region.get(region, 0)
            if nb_cd == 0:
                layer_text.removeChild(item)
            else:
                tspan.firstChild.nodeValue = nb_cd
    #Couche logo
    layer_logo = None
    list_region = set(map_departement_region.values())
    for item in document.getElementsByTagName('g'):
      value_id = item.getAttributeNode('id').value
      if value_id == 'layer_logo':
        layer_logo = item
        break
    if layer_logo:
        for item in layer_logo.getElementsByTagName('g'):
          value_id = item.getAttributeNode('id').value
          if value_id and value_id.startswith('logo_'):
              region = value_id.split('logo_')[1]
              if vente_by_region.get(region, 0) == 0:
                  layer_logo.removeChild(item)
    save_file = open(path_save_map, 'w')
    save_file.write(document.toxml('utf-8'))
    save_file.close()




