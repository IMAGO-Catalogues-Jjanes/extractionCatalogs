from shapely.geometry import Polygon
""" Vérifier que les blocks entrées sont bien construits => test?
Idée: récupérer les coordonnées des entrées textblock et les coordonnées des lignes et les associer
pour chaque TextBlock(entrée) get coordonnées
    pour TextBlock main: 
        pour chaque ligne
            get coordonnées
            si coordonnées lignes dans coordonnées textligne alors ajouter à liste


for el in document.xpath("//alto:TextBlock[@TAGREFS='TYPE_7']", namespaces=NS):
    # récupérer les coordonnées
    coord_V_block = int(el.xpath("@VPOS")[0])
    coord_H_block = int(el.xpath("@HPOS")[0])
    coord_width_block = int(el.xpath("@WIDTH")[0])
    coord_height_block = int(el.xpath("@HEIGHT")[0])
    # créer le polygone correspondant
    coord_block= [(coord_V_block, coord_H_block),(coord_V_block, coord_H_block + coord_width_block), (coord_V_block + coord_height_block, coord_H_block), (coord_V_block + coord_height_block, coord_H_block + coord_width_block)]
    poly_block = Polygon(coord_block)
    for ligne in document.xpath("//alto:TextLine", namespaces=NS):
        # récupérer les coordonnées de la ligne
        coord_V_line = int(ligne.xpath("@VPOS")[0])
        coord_H_line = int(ligne.xpath("@HPOS")[0])
        coord_width_line = int(ligne.xpath("@WIDTH")[0])
        coord_height_line = int(ligne.xpath("@HEIGHT")[0])
        #créer le polygone correspondant
        coord_line = [(coord_V_line, coord_H_line), (coord_V_line, coord_H_line + coord_width_line), (coord_V_line + coord_height_line, coord_H_line), (coord_V_line + coord_height_line, coord_H_line + coord_width_line)]
        poly_line = Polygon(coord_line)
        if poly_block.contains(poly_line):
            print('ok')
"""