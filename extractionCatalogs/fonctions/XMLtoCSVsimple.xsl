<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    xmlns="http://www.tei-c.org/ns/1.0">
    <xsl:output method="text"/>

    <xsl:variable name="delimiter" select="';'"/>

    <!-- column's names -->
    <xsl:variable name="fieldArray">
        <field>Last name of the artist</field>
        
        <field>Biographical elements</field>
        
        <field>Number</field>
        <field>Title of artwork</field>
        <field>Subtitle</field>
        
    </xsl:variable>

    <xsl:param name="fields" select="document('')/*/xsl:variable[@name = 'fieldArray']/*"/>

    <xsl:template match="/">

        <!-- output the header row -->
        <xsl:for-each select="$fields">
            <xsl:if test="position() != 1">
                <xsl:value-of select="$delimiter"/>
            </xsl:if>
            <xsl:value-of select="."/>
        </xsl:for-each>

        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>

        <xsl:apply-templates select="//item"/>
    </xsl:template>

    <xsl:template match="item">
        <xsl:value-of select="preceding-sibling::desc/name/text()"/>
        <xsl:text>; ; ; ; </xsl:text>
        <xsl:value-of select="preceding-sibling::desc/trait/p/text()"/>
        <xsl:text>; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ;</xsl:text>
        <xsl:value-of select="num/text()"/>
        <xsl:value-of select="$delimiter"/>
        <xsl:value-of select="title/text()"/>
        <xsl:value-of select="$delimiter"/>
        <xsl:value-of select="desc/text()"/>
        <xsl:text>; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ;</xsl:text>
        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>

</xsl:stylesheet>
