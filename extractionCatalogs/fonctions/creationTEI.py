"""
Création du TEIheader pour le catalogue d'exposition
D'après un programme récupérant ces mêmes types d'informations réalisées par Claire Jahan.
Author:
Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""

from lxml import etree as ET
from ..variables import contenu_TEI


def creation_header():
    """
    Fonction permettant, pour un catalogue, de créer les balises du teiHeader. Elle récupère des valeurs textuelles
    signalées dans les gabarits du dossier variables
    :return: tei_header
    :rtype: lxml.etree._ElementTree
    """

    tei_header = ET.Element("teiHeader")

    fileDesc = ET.SubElement(tei_header, "fileDesc")
    titleStmt = ET.SubElement(fileDesc, "titleStmt")
    title = ET.SubElement(titleStmt, "title")
    editor_metadata = ET.SubElement(titleStmt, "editor", role="metadata")
    persName_editor_metadata = ET.SubElement(editor_metadata, "persName")
    editor_data = ET.SubElement(titleStmt, "editor", role="data")
    persName_editor_data = ET.SubElement(editor_data, "persName")
    publicationStmt = ET.SubElement(fileDesc, "publicationStmt")
    publisher = ET.SubElement(publicationStmt, "publisher")
    name_publisher = ET.SubElement(publisher, "name")
    commentaire = ET.Comment(' === Nom du projet, directeur/directrice, organisme et adresse === ')
    publisher.insert(0, commentaire)
    name_publisher.text = contenu_TEI.name
    persName_publisher = ET.SubElement(publisher, "persName", type="director")
    persName_publisher.text = contenu_TEI.persName
    orgName = ET.SubElement(publisher, "orgName")
    orgName.text = contenu_TEI.orgName
    address = ET.SubElement(publisher, "address")
    addrLine = ET.SubElement(address, "addrLine")
    addrLine.text = contenu_TEI.addrLine
    postCode = ET.SubElement(address, "postCode")
    postCode.text = contenu_TEI.postCode
    settlement = ET.SubElement(address, "settlement")
    settlement.text = contenu_TEI.settlement
    date = ET.SubElement(publicationStmt, "date", when=contenu_TEI.date)
    date.text = contenu_TEI.date
    availability = ET.SubElement(publicationStmt, "availability")
    licence_text = ET.SubElement(availability, "licence", target=contenu_TEI.licence_target)
    licence_text.text = contenu_TEI.licence
    sourceDesc = ET.SubElement(fileDesc, "sourceDesc")
    bibl = ET.SubElement(sourceDesc, "bibl", type="exhibition_catalog")
    title_source = ET.SubElement(bibl, "title")
    author_source = ET.SubElement(bibl, "author")
    publisher_source = ET.SubElement(bibl, "publisher")
    pubPlace_source = ET.SubElement(bibl, "pubPlace")
    date_source = ET.SubElement(bibl, "date")
    relatedItem = ET.SubElement(bibl, "relatedItem")
    msDesc = ET.SubElement(relatedItem, "msDesc")
    commentaire = ET.Comment(" === organisme conservant l'objet numérisé === ")
    msDesc.insert(0, commentaire)
    msIdentifier = ET.SubElement(msDesc, "msIdentifier")
    repository = ET.SubElement(msIdentifier, "repository")
    repository.text = contenu_TEI.repository
    additional = ET.SubElement(msDesc, "additional")
    surrogates = ET.SubElement(additional, "surrogates")
    ref = ET.SubElement(surrogates, "ref")
    name_dig = ET.SubElement(surrogates, "name", role="digitisation")
    extent = ET.SubElement(bibl, "extent")
    listEvent = ET.SubElement(sourceDesc, "listEvent")
    commentaire = ET.Comment(" === informations sur l'événement référé par le catalogue. Attributs obligatoires === ")
    listEvent.insert(0, commentaire)
    event = ET.SubElement(listEvent, "event", type="exhibition", subtype=contenu_TEI.event_subtype)
    event.attrib["from"] = contenu_TEI.event_from
    event.attrib["to"] = contenu_TEI.event_to
    head_event = ET.SubElement(event, "head", type=contenu_TEI.event_head_type)
    p_event = ET.SubElement(event, "p")
    profileDesc = ET.SubElement(tei_header, "profileDesc")
    encodingDesc = ET.SubElement(tei_header, "encodingDesc")
    # encodingDesc.attrib["{http://www.w3.org/XML/1998/namespace}ns:tei"]="http://www.tei-c.org/ns/1.0"
    # encodingDesc.attrib["{http://www.w3.org/XML/1998/namespace}ns:s"]="http://purl.oclc.org/dsdl/schematron"
    samplingDesc = ET.SubElement(encodingDesc, "samplingDecl")
    p_samplingDesc = ET.SubElement(samplingDesc, "p")
    p_samplingDesc.text = """This electronic version of the catalog only reproduces the entries that
                            correspond to exhibited works. All text preceding or succeeding the list
                            of documents is not reproduced below."""
    appInfo = ET.SubElement(encodingDesc, "appInfo")
    commentaire = ET.Comment(" === logiciel utilisé pour la transcription. Attributs obligatoires === ")
    appInfo.insert(0, commentaire)
    application = ET.SubElement(appInfo, "application", version=contenu_TEI.application_version, ident=contenu_TEI.application_ident)
    label = ET.SubElement(application, "label")
    label.text = contenu_TEI.application_ident
    ptr = ET.SubElement(application, "ptr", target=contenu_TEI.application_pointer)
    revisionDesc = ET.SubElement(tei_header, "revisionDesc")

    return tei_header
