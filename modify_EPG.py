import requests
import xml.etree.ElementTree as ET

URL_XMLTV   = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"
ORIGINAL    = "guiatv_original.xml"
FINAL       = "guiatv.xml"   # Nombre final tras modificar

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
    print(f"Descargando archivo EPG desde: {URL_XMLTV}")
    r = requests.get(URL_XMLTV)
    if r.status_code != 200:
        print(f"Error al descargar: código {r.status_code}")
        return
    
    with open(ORIGINAL, "wb") as f:
        f.write(r.content)
    print(f"Archivo original guardado como: {ORIGINAL}")

    # Parsear el archivo original
    tree = ET.parse(ORIGINAL)
    root = tree.getroot()

    # Convertimos en listas para evitar iteraciones "dinámicas"
    all_channels = list(root.findall("channel"))
    all_programs = list(root.findall("programme"))

    for channel in all_channels:
        original_id = channel.get("id")
        new_base_name = None
        for dname in channel.findall("display-name"):
            if dname.text and dname.text.startswith("M+ "):
                rest_name = dname.text.replace("M+ ", "M. ", 1)  # Reemplazar solo la primera ocurrencia
                rest_name = remove_accents(rest_name)           
                dname.text = rest_name
                new_base_name = rest_name  # Guardamos para replicar en HD/FHD
                break  

        # Si no se modificó el canal (no empieza por "M+ "), pasamos de largo
        if not new_base_name:
            continue

        # Ahora creamos los IDs y nombres para HD y FHD
        hd_id  = f"{original_id}_hd"
        fhd_id = f"{original_id}_fhd"

        hd_name  = f"{new_base_name} HD"
        fhd_name = f"{new_base_name} FHD"

        # --- Clonar la etiqueta <channel> para HD ---
        new_channel_hd = ET.Element("channel", id=hd_id)
        for child in channel:
            if child.tag == "display-name":
                # Reemplazamos por "M. X HD"
                new_dname = ET.SubElement(new_channel_hd, "display-name")
                # Si en el original había varios <display-name>, puedes personalizar si deseas copiarlos todos
                new_dname.text = hd_name
            else:
                # Para <icon>, <url> y otros subelementos, copiamos tal cual
                c_copy = ET.SubElement(new_channel_hd, child.tag, child.attrib)
                c_copy.text = child.text
        root.append(new_channel_hd)

        # --- Clonar la etiqueta <channel> para FHD ---
        new_channel_fhd = ET.Element("channel", id=fhd_id)
        for child in channel:
            if child.tag == "display-name":
                new_dname = ET.SubElement(new_channel_fhd, "display-name")
                new_dname.text = fhd_name
            else:
                c_copy = ET.SubElement(new_channel_fhd, child.tag, child.attrib)
                c_copy.text = child.text
        root.append(new_channel_fhd)

        # --- Duplicar la programación para esos nuevos canales ---
        for prog in all_programs:
            # Si el programa pertenece al canal original
            if prog.get("channel") == original_id:
                # Copia HD
                hd_prog = ET.Element("programme",
                                     start=prog.get("start"),
                                     stop=prog.get("stop"),
                                     channel=hd_id)
                for c in prog:
                    c_new = ET.SubElement(hd_prog, c.tag)
                    c_new.text = c.text
                root.append(hd_prog)

                # Copia FHD
                fhd_prog = ET.Element("programme",
                                      start=prog.get("start"),
                                      stop=prog.get("stop"),
                                      channel=fhd_id)
                for c in prog:
                    c_new = ET.SubElement(fhd_prog, c.tag)
                    c_new.text = c.text
                root.append(fhd_prog)

    # Guardar en el archivo final
    tree.write(FINAL, encoding="utf-8", xml_declaration=True)
    print(f"EPG modificado y guardado en: {FINAL}")

if __name__ == "__main__":
    main()
