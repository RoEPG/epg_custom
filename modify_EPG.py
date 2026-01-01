import requests
import xml.etree.ElementTree as ET

URL_XMLTV = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"

ORIGINAL_FILE = "guiatv_original.xml"
FINAL_FILE    = "guiatv.xml"   # <-- Nombre final para subir al repo

def remove_accents(text):
    """Reemplaza tildes y eñes en minúsculas y mayúsculas."""
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text

# Modifica canales estilo Movistar Accion
def modify_M_channels(text):
    rest_name = text.replace("M+ ", "M. ", 1)
    rest_name = remove_accents(rest_name)
    modified_text = rest_name
    return modified_text

#Modifica el Movistar Plus
def modify_Movistar_Plus(text):
    modified_text = text.replace("Movistar", "M.", 1)
    if "+" in text:
        modified_text = modified_text.replace("+", "")
        return modified_text
    else:
        return modified_text

# Modifica Canal Holywood
def modify_Hollywood(text):
    modified_text = text.replace("Canal ", "")
    return modified_text

# Modifica FDF
def modify_FDF(text):
    modified_text = text.replace("Factoría de Ficción", "FDF")
    return modified_text

# Modifica AXN White. Pasa a llamarse AXN Movies
def modify_AXN_White(text):
    modified_text = text.replace("AXN Movies", "AXN White")
    return modified_text
    
# Modifica Star
def modify_Star(text):
    modified_text = text.replace("STAR Channel", "Star")
    return modified_text

def main():
    # 1. Descargar el archivo original
    print(f"Descargando EPG desde: {URL_XMLTV}")
    r = requests.get(URL_XMLTV)
    if r.status_code != 200:
        print(f"Error al descargar: código {r.status_code}")
        return
    
    with open(ORIGINAL_FILE, "wb") as f:
        f.write(r.content)
    print(f"Archivo original guardado como: {ORIGINAL_FILE}")

    # 2. Parsear el archivo original
    tree = ET.parse(ORIGINAL_FILE)
    root = tree.getroot()

    
    for channel in root.findall("channel"):
        for dname in channel.findall("display-name"):
            #if dname.get("lang") == "es":
            text = dname.text if dname.text else ""
            text = remove_accents(text)
            #Modifico la mayoria de canales de movistar. Los que aparecen como M+
            if text and text.startswith("M+ "):
                text = modify_M_channels(text)
                # Modifico Movistar Espanol
                if "Espanol" in text:
                    text = text.replace("Espanol", "N")
            if "Movistar" in text:
                text = modify_Movistar_Plus(text)
            if "Factoría de Ficción" in text:
                text = modify_FDF(text)
            if "Hollywood" in text and "Canal " in text:
                text = modify_Hollywood(text)
            if "STAR Channel" in text:
                text = modify_Star(text)
            if "AXN Movies" in text:
                text = modify_AXN_White(text)
            if not text.startswith("ES: "):
                dname.text = f"ES: {text}"

    # 4. Guardar la versión final con el nombre que necesitamos
    tree.write(FINAL_FILE, encoding="utf-8", xml_declaration=True)
    print(f"EPG modificado guardado como: {FINAL_FILE}")

if __name__ == "__main__":
    main()
