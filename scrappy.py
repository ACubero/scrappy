import os
import requests
import pdfkit
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
import re
from PyPDF2 import PdfMerger

visited = set()

# Especifica la ruta al ejecutable wkhtmltopdf si no está en el PATH
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Cambia esta ruta según tu instalación
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def sanitize_filename(name):
    # Reemplaza caracteres no válidos en un nombre de archivo
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Reemplaza puntos y otros caracteres no permitidos por guiones bajos
    name = name.replace('.', '_').replace('?', '_').replace(':', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    return name

def generate_breadcrumbs(url, base_url):
    # Genera la ruta de migas de pan basada en la estructura de la URL
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    breadcrumbs = ' > '.join(unquote(part.replace('-', ' ').title()) for part in path_parts)
    return f"{parsed_url.netloc} > {breadcrumbs}"

def save_page_as_pdf(url, base_url, output_folder, pdf_files):
    # Verificar si ya hemos visitado esta URL
    if url in visited:
        return
    
    # Marcar la URL como visitada
    visited.add(url)
    
    # Obtener el título de la página (usaremos el título para el nombre del archivo)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else 'Sin título'
    print(f"Procesando: {title}")
    
    # Sanitizar el nombre del archivo
    sanitized_title = sanitize_filename(title)
    
    # Si no hay título o el título es inválido, usar un nombre basado en la URL
    if not sanitized_title:
        sanitized_title = urlparse(url).path.replace('/', '_').strip('_')
    
    # Crear el nombre del archivo PDF
    output_file = os.path.join(output_folder, f"{sanitized_title}.pdf")

    # Verificar si el archivo existe y agregar un contador si es necesario
    counter = 1
    while os.path.exists(output_file):
        output_file = os.path.join(output_folder, f"{sanitized_title}_{counter}.pdf")
        counter += 1

    # Generar el PDF desde la URL
    try:
        pdfkit.from_url(url, output_file, configuration=config)
        print(f"El PDF de la página se ha guardado en {output_file}")
        pdf_files.append(output_file)  # Agregar el PDF generado a la lista
    except Exception as e:
        print(f"Error al generar el PDF para {url}: {e}")

    # Recorrer todos los enlaces de la página y visitarlos recursivamente
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        full_url = urljoin(base_url, href)
        # Filtrar solo los enlaces que pertenecen al dominio especificado
        if full_url.startswith('https://help.kriter.net/secciones/erp'):
            save_page_as_pdf(full_url, base_url, output_folder, pdf_files)

def save_all_pages_to_files(url, output_folder):
    base_url = url
    
    # Crear la carpeta "result" si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Lista para almacenar los nombres de los archivos PDF generados
    pdf_files = []

    # Iniciar el proceso de generación de PDFs
    save_page_as_pdf(url, base_url, output_folder, pdf_files)

    # Fusionar todos los archivos PDF en uno solo
    merge_pdfs(pdf_files)

def merge_pdfs(pdf_files):
    # Crear la carpeta "gpt-doc" si no existe
    output_folder = "gpt-doc"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Nombre del archivo PDF final
    merged_pdf_path = os.path.join(output_folder, "kriter-help-database.pdf")

    # Inicializar el objeto PdfMerger
    merger = PdfMerger()

    # Agregar cada archivo PDF al merger
    for pdf in pdf_files:
        merger.append(pdf)

    # Escribir el PDF fusionado en el archivo de salida
    merger.write(merged_pdf_path)
    merger.close()

    print(f"Todos los PDFs han sido fusionados en {merged_pdf_path}")

if __name__ == "__main__":
    url = "https://help.kriter.net/secciones/erp"
    output_folder = "result"
    save_all_pages_to_files(url, output_folder)
