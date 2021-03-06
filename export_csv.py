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
list_version = ("1004", "1010", "1104", "1110", "1204")
path_static = os.path.join(os.path.dirname(__file__), 'static')
#nom du fichier de la carte générée
path_save_french = "vente_by_region_%s.svg"
path_save_world = "vente_by_country_%s.svg"
dict_country = {'Alg\xc3\xa9rie': 'algerie',
                 'Allemagne': 'allemagne',
                 'Austria': 'austria',
                 'Belgique': 'belgique',
                 'B\xc3\xa9nin': 'benin',
                 'Bosnia-Herzegovina': 'bosnie',
                 'Burkina Faso': 'burkina_faso',
                 'Cameroun': 'cameroun',
                 'Canada': 'canada',
                 'Colombia': 'colombie',
                 "C\xc3\xb4te d'Ivoire": 'cote_ivoire',
                 'Espagne': 'espagne',
                 'France': 'france',
                 'Finland': 'finland',
                 'Gr\xc3\xa8ce - \xce\x95\xce\xbb\xce\xbb\xce\xac\xce\xb4\xce\xb1': 'grece',
                 'Inde': 'inde',
                 'Indonesia': 'indonesia',
                 'Ireland': 'irelande',
                 'Italie': 'italie',
                 'Luxembourg': 'luxembourg',
                 'Madagascar': 'madagascar',
                 'Mali': 'mali',
                 'Maroc': 'maroc',
                 'Martinique': 'martinique',
                 'Monaco': 'monaco',
                 'Morocco': 'maroc',
                 'Netherlands': 'netherlands',
                 'New Caledonia': 'new_caledonia',
                 'Philippines': 'philippines',
                 'Reunion': 'reunion',
                 'Romania': 'roumanie',
                 "R\xc3\xa9publique D\xc3\xa9mocratique du Congo": 'rep_dem_congo',
                 'Senegal': 'senegal',
                 'Switzerland': 'switzerland',
                 'Taiwan': 'taiwan',
                 'Tchad': 'tchad',
                 'Thailand': 'thailand',
                 'Tunisia': 'tunisie',
                 'T\xc3\xbcrkiye': 'turquie',
                 'United Kingdom': 'united_kingdom',
                 'United States': 'usa'}

def get_list_vente(path):
    """List des ventes obtenue à partir du fichier csv
    fournit en argument"""
    csvfile = open(path_csv)
    dialect = csv.Sniffer().sniff(csvfile.read(1024))
    csvfile.seek(0)
    result = list(csv.DictReader(csvfile, dialect = dialect))
    for item in result:
        for version in list_version:
            fields_product = ["UB-10CD-%s" % version, "UB-CD-%s" % version]
            for product in fields_product:
                item.setdefault(product, '')
    return result


def get_map_departement_region():
    """Dictionnaire permettant d'avoir la correspondance entre département
    et région française"""
    path_departement_region = os.path.join(path_static, 'departement_region.csv')
    obj_file = open(path_departement_region)
    csv_obj = csv.DictReader(obj_file)
    return dict([(item['departement'], item['region']) for item in csv_obj])

def get_template_carte(filename):
    file_svg_file = open(os.path.join(path_static, filename))
    document = minidom.parse(file_svg_file)
    file_svg_file.close()
    return document

def calcul_nb_cd(record, fields_product):
    total = 0
    for product in fields_product:
        if record[product]:
            if "10CD" in product:
                total += int(record[product]) * 10
            else:
                total += int(record[product])
    return  total

def check_map(path_template):
    #Génération d'une carte avec les valeurs du nombre de cd par région
    document = get_template_carte(path_template)
    #Couche text
    layer_text = None
    for item in document.getElementsByTagName('g'):
      value_id = item.getAttributeNode('id').value
      if value_id == 'layer_text':
        layer_text = item
        break
    if layer_text:
        l_obj_text = []
        for item in layer_text.getElementsByTagName('text'):
            value_id = item.getAttributeNode('id').value
            if value_id and value_id.startswith('text_'):
                key = value_id.split('text_')[1]
                l_obj_text.append(key)
    layer_logo = None
    for item in document.getElementsByTagName('g'):
      value_id = item.getAttributeNode('id').value
      if value_id == 'layer_logo':
        layer_logo = item
        break
    if layer_logo:
        l_obj_img =  []
        for item in layer_logo.getElementsByTagName('g'):
          value_id = item.getAttributeNode('id').value
          if value_id and value_id.startswith('logo_'):
              key = value_id.split('logo_')[1]
              l_obj_img.append(key)
    l_key = dict_country.values()
    l_img_absent = []
    l_text_absent = []
    for key in l_key:
      if not key in l_obj_img:
        l_img_absent.append(key)
      if not key in l_obj_text:
        l_text_absent.append(key)
    import pprint
    print "Image absente"
    pprint.pprint(l_img_absent)
    print "Text absent"
    pprint.pprint(l_text_absent)

def generation_svg_document(datas, path_template,  path_dest):
    #Génération d'une carte avec les valeurs du nombre de cd par région
    document = get_template_carte(path_template)
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
                key = value_id.split('text_')[1]
                tspan = [element for element in
                            item.getElementsByTagName('tspan')
                            if element.firstChild][0]
                nb_cd = datas.get(key, 0)
                if nb_cd == 0:
                    layer_text.removeChild(item)
                else:
                    tspan.firstChild.nodeValue = nb_cd
        for item in layer_text.getElementsByTagName('path'):
            value_id = item.getAttributeNode('id').value
            if value_id and value_id.startswith('ligne_'):
                key = value_id.split('ligne_')[1]
                nb_cd = datas.get(key, 0)
                if nb_cd == 0:
                    layer_text.removeChild(item)
    else:
        print "Absence du calque text"
        print layer_text
    #Couche logo
    layer_logo = None
    for item in document.getElementsByTagName('g'):
      value_id = item.getAttributeNode('id').value
      if value_id == 'layer_logo':
        layer_logo = item
        break
    if layer_logo:
        for item in layer_logo.getElementsByTagName('g'):
          value_id = item.getAttributeNode('id').value
          if value_id and value_id.startswith('logo_'):
              key = value_id.split('logo_')[1]
              if datas.get(key, 0) == 0:
                  layer_logo.removeChild(item)
    else:
        print "Absence du calque logo"
        print layer_logo
    save_file = open(path_dest, 'w')
    save_file.write(document.toxml('utf-8'))
    save_file.close()

if __name__ == '__main__':
    if not len(sys.argv) in (1,2):
        print "Vous devez specifier un fichier csv"
        sys.exit(0)
    path_csv = sys.argv[1]
    if path_csv == 'check':
        check_map('world.svg')
        sys.exit(0)
    list_vente = list(get_list_vente(path_csv))
    map_departement_region = get_map_departement_region()
    l_pays_inconnu = set()
    l_departement_inconnu = set()
    for version in list_version:
        fields_product = ["UB-10CD-%s" % version, "UB-CD-%s" % version]
        list_vente_france = []
        map_pays_vente = {}
        for item in list_vente:
            if item[field_pays] == 'France':
                cp = item[field_cp]
                if len(cp) == 5:
                    departement = cp[0:2]
                    if departement.startswith('0'):
                        departement = departement[1]
                    if departement in map_departement_region:
                        region =  map_departement_region[departement]
                        item['region'] = region
                        list_vente_france.append(item)
                    else:
#print "Département inconnu"
#print item
                        l_departement_inconnu.add(departement)
            if item[field_pays] in dict_country:
                key_country = dict_country[item[field_pays]]
                map_pays_vente.setdefault(key_country, 0)
                map_pays_vente[key_country] += calcul_nb_cd(item, fields_product)
            else:
#               print "Pays inconnu"
#               print item
                l_pays_inconnu.add(item[field_pays])



        #Calcule du nombre de cd par région
        list_vente_france.sort(key = itemgetter('region'))
        vente_by_region = {}
        for region, list_item in groupby(list_vente_france, key = itemgetter('region')):
          list_item = list(list_item)
          new_item = {}
          for product in fields_product:
            new_item[product] = sum(
                [int(element[product]) for element
                      in list_item if element[product]])
          vente_by_region[region] = calcul_nb_cd(new_item, fields_product)

        generation_svg_document(vente_by_region, 'region.svg',  path_save_french % version)
        generation_svg_document(map_pays_vente, 'world.svg', path_save_world % version)
        import pprint
        pprint.pprint(l_pays_inconnu)





