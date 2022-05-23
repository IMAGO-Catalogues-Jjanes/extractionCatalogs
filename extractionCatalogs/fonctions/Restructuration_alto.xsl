<?xml version="1.0" encoding="UTF-8"?>
     <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
         xmlns:xs="http://www.w3.org/2001/XMLSchema" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xmlns:a="http://www.loc.gov/standards/alto/ns-v4#"
         xmlns="http://www.loc.gov/standards/alto/ns-v4#"
         version="1.0">
        <xsl:output method="xml" indent="yes" encoding="UTF-8"/>
        
        <xsl:template match="/">
            <alto xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns="http://www.loc.gov/standards/alto/ns-v4#"
                xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-2.xsd">
                <xsl:copy>
                    <xsl:copy-of select=".//a:Description"/>
                    <xsl:copy-of select=".//a:Tags"/>
                </xsl:copy>
                <Layout>
                    <xsl:element name="Page">
                        <xsl:attribute name="WIDTH">
                            <xsl:value-of select=".//a:Page/@WIDTH"/>                    
                        </xsl:attribute>
                        <xsl:attribute name="HEIGHT">
                            <xsl:value-of select=".//a:Page/@HEIGHT"/>                    
                        </xsl:attribute>
                        <xsl:attribute name="PHYSICAL_IMG_NR">
                            <xsl:value-of select=".//a:Page/@PHYSICAL_IMG_NR"/>                    
                        </xsl:attribute>
                        <xsl:attribute name="ID">
                            <xsl:value-of select=".//a:Page/@ID"/>                    
                        </xsl:attribute>
                        <xsl:element name="PrintSpace">
                            <xsl:attribute name="HPOS">
                                <xsl:value-of select=".//a:PrintSpace/@HPOS"/>                    
                            </xsl:attribute>
                            <xsl:attribute name="VPOS">
                                <xsl:value-of select=".//a:PrintSpace/@VPOS"/>                    
                            </xsl:attribute>
                            <xsl:attribute name="WIDTH">
                                <xsl:value-of select=".//a:PrintSpace/@WIDTH"/>                    
                            </xsl:attribute>
                            <xsl:attribute name="HEIGHT">
                                <xsl:value-of select=".//a:PrintSpace/@HEIGHT"/>                    
                            </xsl:attribute>
                            <xsl:apply-templates select=".//a:TextBlock">
                                <xsl:sort select="@VPOS" data-type="number"/>
                            </xsl:apply-templates>
                        </xsl:element>
                        </xsl:element>
                </Layout>
            </alto>
        </xsl:template>
         
         <xsl:template match="a:TextBlock">
             <xsl:element name="TextBlock">
                 <xsl:attribute name="HPOS">
                     <xsl:value-of select="@HPOS"/>                    
                 </xsl:attribute>
                 <xsl:attribute name="VPOS">
                     <xsl:value-of select="@VPOS"/>                    
                 </xsl:attribute>
                 <xsl:attribute name="WIDTH">
                     <xsl:value-of select="@WIDTH"/>                    
                 </xsl:attribute>
                 <xsl:attribute name="HEIGHT">
                     <xsl:value-of select="@HEIGHT"/>                    
                 </xsl:attribute>
                 <xsl:attribute name="ID">
                     <xsl:value-of select="@ID"/>                    
                 </xsl:attribute>
                 <xsl:attribute name="TAGREFS">
                     <xsl:value-of select="@TAGREFS"/>                    
                 </xsl:attribute>                 
                 <xsl:copy-of select="./a:Shape"/>
                 <xsl:apply-templates select="./a:TextLine">
                    <xsl:sort select="./a:String/@VPOS" data-type="number"/>
                 </xsl:apply-templates>
             </xsl:element>
         </xsl:template>
        
         <xsl:template match="@*|node()">
             <xsl:copy>
                 <xsl:apply-templates select="@*|node()"/>
             </xsl:copy>
         </xsl:template>
</xsl:stylesheet>