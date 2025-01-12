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
            if dname.get("lang") == "es":
                original_text = dname.text if dname.text else ""
                if dname.text and dname.text.startswith("M+ "):
                    rest_name = dname.text.replace("M+ ", "M. ", 1)
                    rest_name = remove_accents(rest_name)
                    original_text = rest_name
                if not original_text.startswith("ES: "):
                    dname.text = f"ES: {original_text}"

    # 4. Guardar la versión final con el nombre que necesitamos
    tree.write(FINAL_FILE, encoding="utf-8", xml_declaration=True)
    print(f"EPG modificado guardado como: {FINAL_FILE}")

if __name__ == "__main__":
    main()
