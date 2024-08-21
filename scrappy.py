import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited = set()

def get_text_from_url(url, base_url):
    # Verificar si ya hemos visitado esta URL
    if url in visited:
        return ""
    
    # Marcar la URL como visitada
    visited.add(url)
    
    # Obtener el contenido de la página web
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return ""

    # Analizar el contenido HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extraer el texto de la página
    text = soup.get_text(separator='\n')

    # Recorrer todos los enlaces de la página y visitarlos recursivamente
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        full_url = urljoin(base_url, href)
        # Filtrar solo los enlaces que pertenecen al dominio original
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            text += "\n" + get_text_from_url(full_url, base_url)
    
    return text

def save_text_to_file(url, output_folder):
    base_url = url
    text = get_text_from_url(url, base_url)
    
    # Crear la carpeta "result" si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Nombre del archivo basado en el dominio de la URL
    domain = urlparse(url).netloc.replace('.', '_')
    output_file = os.path.join(output_folder, f"{domain}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"El texto de la web se ha guardado en {output_file}")

if __name__ == "__main__":
    url = input("Introduce la URL del sitio web: ")
    output_folder = "result"
    save_text_to_file(url, output_folder)
