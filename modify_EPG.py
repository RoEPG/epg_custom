import requests
import xml.etree.ElementTree as ET

URL_XMLTV = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"

ORIGINAL_FILE = "guiatv_original.xml"
MODIFIED_FILE = "guiatv.xml"

def main():
    print(f"Descargando archivo EPG desde: {URL_XMLTV}")
    r = requests.get(URL_XMLTV)
    if r.status_code != 200:
        print(f"Error al descargar: código {r.status_code}")
        return

    # Guardar el archivo original
    with open(ORIGINAL_FILE, "wb") as f:
        f.write(r.content)
    print(f"Archivo original guardado como: {ORIGINAL_FILE}")

    # Parsear el XML
    tree = ET.parse(ORIGINAL_FILE)
    root = tree.getroot()

    # Recorremos todos los <channel> y dentro cada <display-name lang="es">
    for channel in root.findall("channel"):
        for dname in channel.findall("display-name"):
            # Verificamos que tenga lang="es"
            if dname.get("lang") == "es":
                # Obtén el texto actual
                original_text = dname.text if dname.text else ""
                
                # Modifica a tu gusto. Aquí, anteponemos "ES: " al nombre original
                if not original_text.startswith("ES: "):
                    dname.text = f"ES: {original_text}"

    # Guardar el resultado en un nuevo archivo
    tree.write(MODIFIED_FILE, encoding="utf-8", xml_declaration=True)
    print(f"EPG modificado guardado como: {MODIFIED_FILE}")

if __name__ == "__main__":
    main()
