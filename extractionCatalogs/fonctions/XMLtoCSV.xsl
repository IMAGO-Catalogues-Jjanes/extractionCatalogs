<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    xmlns="http://www.tei-c.org/ns/1.0">
    <xsl:output method="text"/>

    <xsl:variable name="delimiter" select="';'"/>



    <!-- codes  -->
    <xsl:variable name="codeArray">
        <field>0</field>
        <field>1</field>
        <field>2</field>
        <field>4</field>
        <field>5</field>
        <field>65</field>
        <field>66</field>
        <field>67</field>
        <field>68</field>
        <field>69</field>
        <field>70</field>
        <field>72</field>
        <field>73</field>
        <field>78</field>
        <field>79</field>
        <field>80</field>
        <field>81</field>
        <field>82</field>
        <field>83</field>
        <field>84</field>
        <field>86</field>
        <field>87</field>
        <field>92</field>
        <field>3</field>
        <field>101</field>
        <field>6</field>
        <field>9</field>
        <field>10</field>
        <field>11</field>
        <field>12</field>
        <field>13</field>
        <field>14</field>
        <field>23</field>
        <field>26</field>
        <field>27</field>
        <field>28</field>
        <field>29</field>
        <field>30</field>
        <field>31</field>
        <field>41</field>
        <field>40</field>
        <field>43</field>
        <field>42</field>
        <field>53</field>
        <field>54</field>
        <field>55</field>
        <field>56</field>
        <field>57</field>
        <field>58</field>
        <field>59</field>
        <field>60</field>
        <field>61</field>
        <field>62</field>
        <field>63</field>
        <field>46</field>
        <field>44</field>
        <field>45</field>
        <field>47</field>
        <field>48</field>
        <field>51</field>
        <field>49</field>
        <field>50</field>
        <field>59</field>
        <field>60</field>
        <field>61</field>
        <field>98</field>
        <field>99</field>
        <field>52</field>
    </xsl:variable>

    <xsl:param name="codes" select="document('')/*/xsl:variable[@name = 'codeArray']/*"/>



    <!-- column's names -->
    <xsl:variable name="fieldArray">
        <field>Nom artiste</field>
        <field>Prénom artiste</field>
        <field>Sexe artiste (F/M/FM/vide)</field>
        <field>Appartenance à un groupe</field>
        <field>Éléments biographiques</field>
        <field>Adresse complète de l'artiste telle qu'elle apparaît dans le catalogue</field>
        <field>Pays de l'artiste</field>
        <field>État de l'artiste</field>
        <field>Ville de l'artiste</field>
        <field>Identifiant WikiData ville de l'artiste</field>
        <field>Coordonnées ville de l'artiste</field>
        <field>N adresse de l'artiste</field>
        <field>Voie adresse de l'artiste</field>
        <field>Complément d'adresse de l'artiste</field>
        <field>Adresse complète de l'artiste 2 telle qu'elle apparaît dans le catalogue</field>
        <field>Pays de l'artiste 2</field>
        <field>État de l'artiste 2</field>
        <field>Ville de l'artiste 2</field>
        <field>Identifiant WikiData ville de l'artiste 2</field>
        <field>Coordonnées ville de l'artiste 2</field>
        <field>N adresse de l'artiste 2</field>
        <field>Voie adresse de l'artiste 2</field>
        <field>Complément d'adresse de l'artiste 2</field>
        <field>Nationalité artiste</field>
        <field>Élève de</field>
        <field>Année de naissance</field>
        <field>Adresse complète de naissance telle qu'elle apparaît dans le catalogue</field>
        <field>Pays de naissance</field>
        <field>État de naissance</field>
        <field>Ville de naissance</field>
        <field>Identifiant WikiData ville de naissance</field>
        <field>Coordonnées ville de naissance</field>
        <field>Année de mort</field>
        <field>Adresse complète de mort telle qu'elle apparaît dans le catalogue</field>
        <field>Pays de mort</field>
        <field>État de mort</field>
        <field>Ville de mort</field>
        <field>Identifiant WikiData ville de mort</field>
        <field>Coordonnées ville de mort</field>
        <field>numéro</field>
        <field>Titre oeuvre</field>
        <field>Sous-titre</field>
        <field>Traduction titre</field>
        <field>Année de début de conception</field>
        <field>Mois de début de conception</field>
        <field>Jour de début de conception</field>
        <field>Année de fin de conception</field>
        <field>Mois de fin de conception</field>
        <field>Jour de fin de conception</field>
        <field>Pays de conception</field>
        <field>État de conception</field>
        <field>Ville de conception</field>
        <field>Identifiant WikiData ville de conception</field>
        <field>Coordonnées ville de conception</field>
        <field>Dimensions</field>
        <field>Catégories</field>
        <field>Medium</field>
        <field>Salle</field>
        <field>Chapitre du catalogue</field>
        <field>reproduit dans catalogue ?</field>
        <field>Prix</field>
        <field>Localisation / Propriétaire</field>
        <field>Pays du propriétaire</field>
        <field>État du propriétaire</field>
        <field>Ville du propriétaire</field>
        <field>Identifiant WikiData ville du propriétaire</field>
        <field>Coordonnées ville du propriétaire</field>
        <field>Notes</field>
    </xsl:variable>

    <xsl:param name="fields" select="document('')/*/xsl:variable[@name = 'fieldArray']/*"/>





    <xsl:template match="/">
        <xsl:text>catalogue_expo;136;3</xsl:text>
        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>



        <xsl:text>Exposition:;COLLER ICI LE NOM DE L'EXPOSITION</xsl:text>
        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>

        <xsl:text>Utilisateur:;COLLER ICI LE NOM UTILISATEUR</xsl:text>
        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>
        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>


        <!-- code zone -->

        <xsl:for-each select="$codes">
            <xsl:if test="position() != 1">
                <xsl:value-of select="$delimiter"/>
            </xsl:if>
            <xsl:value-of select="."/>
        </xsl:for-each>

        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>


        <!-- output the header row -->
        <xsl:for-each select="$fields">
            <xsl:if test="position() != 1">
                <xsl:value-of select="$delimiter"/>
            </xsl:if>
            <xsl:value-of select="."/>
        </xsl:for-each>

        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>

        <xsl:apply-templates select="//tei:item"/>
    </xsl:template>

    <xsl:template match="tei:item">
        <xsl:value-of select="preceding-sibling::tei:desc/tei:name/text()"/>
        <xsl:text>; ; ; ; </xsl:text>
        <xsl:value-of select="preceding-sibling::tei:desc/tei:trait/tei:p/text()"/>
        <xsl:text>; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ;</xsl:text>
        <xsl:value-of select="tei:num/text()"/>
        <xsl:value-of select="$delimiter"/>
        <xsl:value-of select="tei:title/text()"/>
        <xsl:value-of select="$delimiter"/>
        <xsl:value-of select="tei:desc/text()"/>
        <xsl:text>; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ; ;</xsl:text>
        <!-- output newline -->
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>

</xsl:stylesheet>
