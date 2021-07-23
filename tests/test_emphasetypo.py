from PIL import Image
from lxml import etree as ET

NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
chemin = "CatRouen_1860_bpt6k1181800p_28.xml"
chemin_image = "CatRouen_1860_bpt6k1181800p_28.JPEG"

alto = ET.parse(chemin)
token_list = alto.xpath("//alto:String", namespaces=NS)
image = Image.open(chemin_image)
for token in token_list:
    left_coordinate = int(token.xpath("@HPOS")[0])
    bottom_coordinate = int(token.xpath("@VPOS")[0])
    width = int(token.xpath("@WIDTH")[0])
    height = int(token.xpath("@HEIGHT")[0])
    right_coordinate = left_coordinate + width
    top_coordinate = bottom_coordinate + height
    print(left_coordinate, bottom_coordinate, right_coordinate, top_coordinate)
    image_crop = image.crop((left_coordinate, top_coordinate, right_coordinate, bottom_coordinate))