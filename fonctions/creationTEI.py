"""
Création du TEIheader pour le catalogue d'exposition
D'après un programme récupérant ces mêmes types d'informations réalisées par Claire Jahan.
En commentaires les balises dont les données se sont pas encore ajoutées
Author: Juliette Janes
Date: 18/06/21
"""

from lxml import etree as ET

def creation_header():
    """
    Fonction permettant, pour un catalogue, de créer les balises du teiheader.
    => lister les param nécessaires + questions
    :return: tei_header_xml
    :rtype: lxml.etree._ElementTree
    """
    tei_header_xml = ET.Element("teiHeader")

    # création du fileDesc
    fileDesc_xml = ET.SubElement(tei_header_xml, "fileDesc")
    # titleStmt => informations à récupérer
    titleStmt_xml = ET.SubElement(fileDesc_xml, "titleStmt")
    title_xml = ET.SubElement(titleStmt_xml, "title")
    editor_metadata_xml = ET.SubElement(titleStmt_xml, "editor", role="metadata")
    persName_editor_metadata_xml = ET.SubElement(editor_metadata_xml, "persName")
    editor_data_xml = ET.SubElement(titleStmt_xml, "editor", role="data")
    persName_editor_data_xml = ET.SubElement(editor_data_xml, "persName")
    # publicationStmt
    publicationStmt_xml = ET.SubElement(fileDesc_xml, "publicationStmt")
    publisher_xml = ET.SubElement(publicationStmt_xml, "publisher")
    name_publisher_xml = ET.SubElement(publisher_xml, "name")
    name_publisher_xml.text = "VISUAL CONTAGIONS"
    persName_publisher = ET.SubElement(publisher_xml, "persName", type="director")
    persName_publisher.text = "Béatrice Joyeux-Prunel"
    orgname_xml = ET.SubElement(publisher_xml, "orgName")
    orgname_xml.text = "UNIGE"
    address_xml = ET.SubElement(publisher_xml, "address")
    addrLine_xml = ET.SubElement(address_xml, "addrLine")
    addrLine_xml.text = "5 rue des Battoirs 7"
    postCode_xml = ET.SubElement(address_xml, "postCode")
    postCode_xml.text = "1205"
    settlement_xml = ET.SubElement(address_xml, "settlement")
    settlement_xml.text = "Genève"
    date_xml = ET.SubElement(publicationStmt_xml, "date", when="2021")
    availability = ET.SubElement(publicationStmt_xml, "availability")
    licence_text_xml = ET.SubElement(availability, "licence", target="https://creativecommons.org/licenses/by/4.0/")
    licence_text_xml.text = "CC-BY"
    licence_image_xml = ET.SubElement(availability, "licence",
                                      target="https://gallica.bnf.fr/html/und/conditions-dutilisation-des-contenus-de-gallica")

    """ sourceDesc => informations à récupérer"""
    sourceDesc_xml = ET.SubElement(fileDesc_xml, "sourceDesc")
    bibl_xml = ET.SubElement(sourceDesc_xml, "bibl", type="exhibition_catalog")
    title_source_xml = ET.SubElement(bibl_xml, "title")
    author_source_xml = ET.SubElement(bibl_xml, "author")
    publisher_source_xml = ET.SubElement(bibl_xml, "publisher")
    pubPlace_source_xml = ET.SubElement(bibl_xml, "pubPlace")
    date_source_xml = ET.SubElement(bibl_xml, "date")
    # date_source_xml.set(when, ) ajout de l'attribut when dans date
    relatedItem_xml = ET.SubElement(bibl_xml, "relatedItem")
    msDesc_xml = ET.SubElement(relatedItem_xml, "msDesc")
    msIdentifier_xml = ET.SubElement(msDesc_xml, "msIdentifier")
    repository_xml = ET.SubElement(msIdentifier_xml, "repository")
    additional_xml = ET.SubElement(relatedItem_xml, "additional")
    surrogates_xml = ET.SubElement(additional_xml, "surrogates")
    ref_xml = ET.SubElement(surrogates_xml, "ref")
    # ajout attribut facs avec lien vers version numérisée
    name_dig_xml = ET.SubElement(additional_xml, "name", role="digitisation")
    extent_xml = ET.SubElement(bibl_xml, "extent")

    listEvent_xml = ET.SubElement(sourceDesc_xml, "listEvent")
    event_xml = ET.SubElement(listEvent_xml, "event", type="", subtype="")
    event_xml.attrib["from"] = ""
    event_xml.attrib["to"] = ""
    head_event_xml = ET.SubElement(event_xml, "head")
    head_event_type_xml = ET.SubElement(event_xml, "head", type="")


    profileDesc_xml = ET.SubElement(tei_header_xml, "profileDesc")
    # langUsage_xml = ET.SubElement(profileDesc_xml, "langUsage")
    # attribut avec langue du document
    encodingDesc_xml = ET.SubElement(tei_header_xml, "encodingDesc")
    # encodingDesc_xml.attrib["{http://www.w3.org/XML/1998/namespace}ns:tei"]="http://www.tei-c.org/ns/1.0"
    # encodingDesc_xml.attrib["{http://www.w3.org/XML/1998/namespace}ns:s"]="http://purl.oclc.org/dsdl/schematron"
    samplingDesc_xml = ET.SubElement(encodingDesc_xml, "samplingDecl")
    p_samplingDesc_xml = ET.SubElement(samplingDesc_xml, "p")
    p_samplingDesc_xml.text = """This electronic version of the catalog only reproduces the entries that
                            correspond to exhibited works. All text preceding or succeeding the list
                            of documents is not reproduced below."""

    appInfo_xml = ET.SubElement(encodingDesc_xml, "appInfo")
    application_xml = ET.SubElement(appInfo_xml, "application")
    # Kraken ou eScriptorium?
    revisionDesc_xml = ET.SubElement(tei_header_xml, "revisionDesc")
    """change_xml = ET.SubElement(revisionDesc_xml, "change", who="nom")"""

    return tei_header_xml

