# 0. Setup inicial y dependencias

## Librerías

import urllib.request
import gzip
import json
import pandas as pd
import requests
import re
import random 
import textwrap
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

## Configuraciones adicionales
line_width = 80



# 1. Funciones necesarias

def get_movie_details(id):

    """
    Obtiene los detalles de una película desde la API de The Movie Database (TMDb).

    Args:
        id (int): El ID de la película en TMDb.

    Returns:
        tuple: Un conjunto de valores que incluye el título, géneros, país de origen,
               sinopsis, fecha de lanzamiento, presupuesto, ingresos, duración y URL del póster.
    """

    # Obtener la API key desde las variables de entorno
    api_key = os.getenv("TMDB_API_KEY")
    
    # Usar la ID proporcionada para leer los datos de TMDB como JSON    
    url = f"https://api.themoviedb.org/3/movie/{id}?language=es"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.get(url, headers=headers)
    movie_details = json.loads(response.text)    

    # Validar y convertir la fecha de lanzamiento  
    if re.search(r"\d{4}-\d{2}-\d{2}", movie_details["release_date"]):
        release_date = datetime.strptime(movie_details["release_date"], "%Y-%m-%d").year
    else:
        release_date = None

    # Obtener el resto de detalles de la película
    title = movie_details["title"]
    genres = ", ".join([genre["name"] for genre in movie_details["genres"]])
    origin_country = movie_details["origin_country"][0]
    overview = movie_details["overview"]    
    budget = movie_details["budget"]
    revenue = movie_details["revenue"]
    runtime = movie_details["runtime"]
    poster_url = f"https://image.tmdb.org/t/p/original{movie_details["poster_path"]}"

    return title, genres, origin_country, overview, release_date, budget, revenue, runtime, poster_url



def obtain_movies_df(url, dificulty):
    """
    Descarga, descomprime y procesa un archivo JSON comprimido desde una URL para obtener detalles de películas.

    Args:
        url (str): La URL del archivo comprimido (gzip) que contiene los datos de películas en formato JSON.
        dificulty (int): El nivel de dificultad del juego elegido por el usuario.

    Returns:
        pandas.DataFrame: Un DataFrame con los detalles de las películas más populares, incluyendo columnas como 
                          Titulo, Generos, Pais origen, Resumen, Lanzamiento, Presupuesto, Recaudacion, Duracion y Url poster.
    """

    # URL del archivo comprimido, descargarlo y descomprimirlo
    response = urllib.request.urlopen(url)
    compressed_file = response.read()
    with gzip.GzipFile(fileobj=BytesIO(compressed_file)) as gz:
        data = gz.read()

    # Convertir los datos a una cadena y luego procesar línea por línea
    json_data = data.decode('utf-8')
    movies_ids_data = []
    for line in json_data.splitlines():
        line = line.strip()
        if line:
            try:
                movie = json.loads(line)
                movies_ids_data.append(movie)
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON en la línea: {line}")
                print(f"Error: {e}")

    # Convertir la lista de películas a un DataFrame de pandas y ordenar por popularidad (dificultad)
    movies_ids_df = pd.DataFrame(movies_ids_data)
    movies_ids_df.sort_values("popularity", ascending=False, inplace=True)

    # Obtener los detalles de las películas más populares
    cols = ["Titulo", "Generos", "Pais origen", "Resumen", "Lanzamiento", "Presupuesto", "Recaudacion", "Duracion", "Url poster"]
    movies_details_df = pd.DataFrame(columns=cols)

    # Filtrar por dificultad las películas según popularidad
    if dificulty == 1:
        selected_movies = movies_ids_df[:250].sample(50)
    elif dificulty == 2:
        selected_movies = movies_ids_df[1000:2000].sample(50)
    elif dificulty == 3:
        selected_movies = movies_ids_df[4000:6000].sample(50)
    elif dificulty == 4:
        selected_movies = movies_ids_df[8000:10000].sample(50)
    else:
        print("Algo ha ido mal. La dificultad debería ser un número entre 1 y 4.")

    # Obtener los detalles de las películas seleccionadas
    for movie_id in selected_movies["id"]:
        movies_details_df.loc[len(movies_details_df.index)] = get_movie_details(movie_id)

    # Filtrar películas de USA para los primeros niveles de dificultad
    if dificulty in [1, 2, 3]:
        movies_details_df = movies_details_df[movies_details_df["Pais origen"] == "US"]

    # Convertir la columna "Lanzamiento" a tipo entero (soportando valores nulos)
    movies_details_df["Lanzamiento"] = movies_details_df["Lanzamiento"].astype("Int64")

    return movies_details_df



def validate_answer():

    """
    Valida la respuesta del usuario asegurándose de que sea un número entre 1 y 4.

    Returns:
        int: La respuesta validada del usuario.
    """
    
    # Instanciar un bucle while que sólo se rompe cuando la respuesta es un número entre 1 y 4
    valid_answer = False
    while valid_answer == False:
        answer = input("\nIntroduce un número entre 1 y 4 para tu respuesta: ")
        if re.match(r"^\d$", answer):
            answer = int(answer)
            if answer in range(1, 5):
                valid_answer = True
            else:
                print(f"\n¡{answer} no es un número del 1 al 4!")
        else:
            print(f"\n¡{answer} no es un número del 1 al 4!")

    return answer



def question_release_date(movies_details_df, dificulty):

    """
    Genera una pregunta sobre un el año de lanzamiento de una película y valida la respuesta del usuario.

    Args:
        movies_details_df (pandas.DataFrame): Un DataFrame con los detalles de las películas.
        dificulty (int): El nivel de dificultad del juego elegido por el usuario.

    Returns:
        bool: True si la respuesta es correcta, False en caso contrario.
    """
    
    # Elegir aleatoriamente una película como la respuesta correcta
    correct_answer = movies_details_df.sample(1)
    correct_answer_title = correct_answer["Titulo"].item()
    correct_answer_release_date = correct_answer["Lanzamiento"].item()

    # Crear una lista de años, no superiores al actual ni iguales al correcto, en función del nivel de dificultad
    current_year = datetime.today().year
    years_list = list(range(correct_answer_release_date-int(64/dificulty**2), correct_answer_release_date+int(64/dificulty**2)))
    years_list = [year for year in years_list if (year <= current_year) & (year != correct_answer_release_date)]

    # Elegir cuatro años incluyendo el correcto y desordenarlos
    options_years = list(random.sample(years_list, 3))
    options_years.append(correct_answer_release_date)
    options_years = random.sample(options_years, len(options_years))

    # Mostrar al usuario la pregunta
    print("\nEL LANZAMIENTO OFICIAL\n")
    print(f"¿En qué año se estrenó '{correct_answer_title}'?")
    for i, year in enumerate(options_years):
        print(f"{i+1}. {year}")

    # Validar la respuesta del usuario y comprobar si es correcta
    answer = validate_answer()
    is_answer_correct = options_years[answer-1] == correct_answer["Lanzamiento"].item()

    # Mostrar mensaje de respuesta correcta/incorrecta y el póster completo
    if is_answer_correct:        
        print(f"\n¡¡¡CORRECTO!!! Efectivamente, '{correct_answer_title}' se estrenó en el año {correct_answer_release_date}.\n")
        return True
    else:
        print(f"\nIncorrecto... '{correct_answer_title}' no se estrenó en el año {options_years[answer-1]}, sino en el {correct_answer_release_date}.\n")
        return False



def question_overview(movies_details_df, line_width, dificulty):

    """
    Genera una pregunta sobre el resumen de una película y valida la respuesta del usuario.

    Args:
        movies_details_df (pandas.DataFrame): Un DataFrame con los detalles de las películas.
        line_width (int): Un entero que indica la longitud máxima de las filas de caracteres.
        dificulty (int): El nivel de dificultad del juego elegido por el usuario.

    Returns:
        bool: True si la respuesta es correcta, False en caso contrario.
    """
    
    # Seleccionar aleatoriamente cuatro opciones de películas
    four_options = movies_details_df.sample(4)

    # Elegir aleatoriamente una de las cuatro opciones como la respuesta correcta
    correct_answer = four_options.sample(1)
    correct_answer_title = correct_answer["Titulo"].item()
    correct_answer_overview = correct_answer["Resumen"].item()
    formatted_overview = textwrap.fill(correct_answer_overview, width=line_width)

    # Crear el resumen enmascarando las vocales con x's
    masked_overview = correct_answer_overview
    vowel_groups = [["A", "a", "á"], ["E", "e", "é"], ["I", "i", "í"], ["O", "o", "ó"], ["U", "u", "ú"]]
    for vowel_group in vowel_groups[:dificulty+1]:
        masked_overview = masked_overview.replace(vowel_group[0], "X").replace(vowel_group[1], "x").replace(vowel_group[2], "x")
    formatted_masked_overview = textwrap.fill(masked_overview, width=line_width)

    # Mostrar al usuario la pregunta y el resumen enmascarado
    print("\nEL RESUMEN ENMASCARADO\n")
    print(("¿A cuál de las siguientes 4 películas corresponde el siguiente resumen incompleto?\n\n"
        f"{formatted_masked_overview}\n"))
    for i in range(4):
        print(f"{i+1}. {four_options.iloc[i]['Titulo']}")

    # Validar la respuesta del usuario y comprobar si es correcta
    answer = validate_answer()
    is_answer_correct = four_options.iloc[answer-1]["Titulo"] == correct_answer["Titulo"].item()

    # Mostrar mensaje de respuesta correcta/incorrecta y el póster completo
    if is_answer_correct:        
        print((f"\n¡¡¡CORRECTO!!! Efectivamente, se trata del resumen de '{correct_answer_title}'.\n\n"
            f"Míralo completo:\n\n{formatted_overview}\n"))
        return True
    else:
        print((f"\nIncorrecto... Se trata del cartel de '{correct_answer_title}'.\n\n"
            f"Míralo completo:\n\n{correct_answer_overview}\n"))
        return False



def question_details(movies_details_df):

    """
    Genera una pregunta sobre los detalles de una película y valida la respuesta del usuario.

    Args:
        movies_details_df (pandas.DataFrame): Un DataFrame con los detalles de las películas.
        line_width (int): Un entero que indica la longitud máxima de las filas de caracteres.

    Returns:
        bool: True si la respuesta es correcta, False en caso contrario.
    """

    # Bucle while para comprobar que los detalles técnicos están presentes
    all_ok = False
    while all_ok == False:

        # Seleccionar aleatoriamente cuatro opciones de películas
        four_options = movies_details_df.sample(4)

        # Elegir aleatoriamente una de las cuatro opciones como la respuesta correcta y extraer sus detalles
        correct_answer = four_options.sample(1)
        correct_answer_title = correct_answer["Titulo"].item()
        correct_answer_genres = correct_answer["Generos"].item()
        correct_answer_release = correct_answer["Lanzamiento"].item()
        correct_answer_budget = correct_answer["Presupuesto"].item()
        correct_answer_revenue = correct_answer["Recaudacion"].item()
        correct_answer_runtime = correct_answer["Duracion"].item()

        # Comprueba que están los detalles técnicos
        all_ok = (len(correct_answer_genres) >= 1) & (correct_answer_budget > 0) & (correct_answer_revenue > 0) & (correct_answer_runtime > 0)

    # Mostrar al usuario la pregunta con los detalles de la película
    print("\nDETALLES DE PRODUCCIÓN\n")
    correct_answer_details = f""
    correct_answer_details += f"¿Cuál de las siguientes 4 películas se estrenó el {correct_answer_release}, "
    if (correct_answer_budget > 0) & (correct_answer_revenue > 0):
        correct_answer_details += f"con un presupuesto de {correct_answer_budget:,}$ y una recaudación de {correct_answer_revenue:,}$, que "
    correct_answer_details += f"podría enmaracarse dentro de {correct_answer_genres}, "
    correct_answer_details += f"y tiene una duración de {correct_answer_runtime} min?"    
    formatted_details = textwrap.fill(correct_answer_details, width=line_width)
    print(formatted_details)

    # Muestra las opciones
    for i in range(4):
        print(f"{i+1}. {four_options.iloc[i]['Titulo']}")

    # Validar la respuesta del usuario y comprobar si es correcta
    answer = validate_answer()
    is_answer_correct = four_options.iloc[answer-1]["Titulo"] == correct_answer["Titulo"].item()

    # Mostrar mensaje de respuesta correcta/incorrecta y el póster completo
    if is_answer_correct:        
        print(f"\n¡¡¡CORRECTO!!! Efectivamente, se trata de '{correct_answer_title}'.\n\n")
        return True
    else:
        print(f"\nIncorrecto... Se trata de '{correct_answer_title}'.\n\n")
        return False



def get_poster_part(url_poster, dificulty):

    """
    Obtiene una parte central del póster de la película desde la URL dada.

    Args:
        url_poster (str): La URL del póster de la película.
        dificulty (int): El nivel de dificultad del juego elegido por el usuario.

    Returns:
        None
    """

    # Cargar la imagen desde la URL y obtener sus dimensiones
    response = requests.get(url_poster)
    img = Image.open(BytesIO(response.content))
    width, height = img.size
    crop_perc = 0.3 / dificulty

    # Calcular el tamaño del recorte en función de la dificultad y sus coordenadas desde el centro
    crop_width = int(width * crop_perc)
    crop_height = int(height * crop_perc)
    left = (width - crop_width) / 2
    top = (height - crop_height) / 2
    right = (width + crop_width) / 2
    bottom = (height + crop_height) / 2

    # Recortar la imagen y convertir la imagen recortada a formato PNG en un buffer de memoria
    cropped_img = img.crop((left, top, right, bottom))
    buffered = BytesIO()
    cropped_img.save(buffered, format="PNG")
    buffered.seek(0)

    # Mostrar la imagen recortada
    cropped_img.show()

    return None



def question_poster_piece(movies_details_df, dificulty):

    """
    Genera una pregunta sobre un trozo de póster de película y valida la respuesta del usuario.

    Args:
        movies_details_df (pandas.DataFrame): Un DataFrame con los detalles de las películas.
        dificulty (int): El nivel de dificultad del juego elegido por el usuario.

    Returns:
        bool: True si la respuesta es correcta, False en caso contrario.
    """
    
    # Seleccionar aleatoriamente cuatro opciones de películas
    four_options = movies_details_df.sample(4)
    
    # Elegir aleatoriamente una de las cuatro opciones como la respuesta correcta
    correct_answer = four_options.sample(1)
    correct_answer_title = correct_answer["Titulo"].item()
    correct_answer_url_poster = correct_answer["Url poster"].item()
    
    # Mostrar al usuario la pregunta y el trozo del póster
    print("\nEL CARTEL ROTO\n")
    print("¿A cuál de las siguientes 4 películas corresponde el siguiente trozo de cartel?")
    for i in range(4):
        print(f"{i+1}. {four_options.iloc[i]['Titulo']}")
    get_poster_part(correct_answer_url_poster, dificulty)

    # Validar la respuesta del usuario y comprobar si es correcta
    answer = validate_answer()
    is_answer_correct = four_options.iloc[answer-1]["Titulo"] == correct_answer["Titulo"].item()

    # Cargar la imagen desde la URL y obtener sus dimensiones
    response = requests.get(correct_answer_url_poster)
    img = Image.open(BytesIO(response.content))

    # Convertir la imagen a formato PNG en un buffer de memoria
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)

    # Mostrar la imagen
    img.show()

    # Mostrar mensaje de respuesta correcta/incorrecta y el póster completo
    if is_answer_correct:        
        print(f"\n¡¡¡CORRECTO!!! Efectivamente, se trata del cartel de '{correct_answer_title}'.\n")
        return True
    else:
        print(f"\nIncorrecto... Se trata del cartel de '{correct_answer_title}'.\n")
        return False



def clear_screen():
    
    """
    Limpia la terminal en la que se ejecuta el juego.

    Args:
        None

    Returns:
        None
    """

    os.system('cls' if os.name == 'nt' else 'clear')



# 2. Proceso completo
## Prepara el inicio del juego
clear_screen()
dificulty_labels = {
    1: "1 - American Pie",
    2: "2 - Mi vecino Totoro",
    3: "3 - Los Vengadores",
    4: "4 - Pulp Fiction"
}
ranking = pd.read_csv(
    "./Ranking.txt", sep=";", header=None, index_col=0,
    names=["Jugador", "Dificultad", "Puntos"], encoding="ANSI"
    )

## Bienvenida al usuario y elegir dificultad
user_name = input("\n¡Hola! ¿Cómo te llamas?\n\n> ")
print((f"\n¡Hola, {user_name}!\n\n¡Bienvenido a Popcorn Quiz, el juego de preguntas sobre cine!\n\n"
       "Para jugar a Popcorn Quiz, tendrás que responder un total de 4 preguntas:\n"
       "1. Adivina el año de lanzamiento de una película.\n"
       "2. Adivina a qué película corresponde el resumen enmascarado.\n"
       "3. Adivina a qué película corresponden los detalles de producción.\n"
       "4. Adivina a qué película corresponde el trozo de cartel que te mostramos\n\n"
       "Además, puedes jugar en cuatro niveles de dificultad distintos. Cada nivel\n"
       "hace que juegues con películas más o menos populares, además de que\n"
       "en las distintas preguntas habrá matices para complicar más o menos el juego.\n\n"
       "¿En qué nivel te gustaría jugar? El 1 es el más fácil, y el 4 el más difícil.\n\n"
       "Recuerda que obtendrás puntos extra al final dependiendo del nivel de dificultad :)\n"))

for i in dificulty_labels:
    print(dificulty_labels[i])

dificulty = validate_answer()
dificulty_label = dificulty_labels[dificulty]

print(f"\nPerfecto, has elegido el nivel de dificultad {dificulty_label}. Dame un momento mientras preparo todo...")

## Obtener el dataframe con las películas
url = "http://files.tmdb.org/p/exports/movie_ids_05_15_2024.json.gz"
movies_details_df = obtain_movies_df(url, dificulty)

## Instancia el contador y comienza el juego
counter = 0
input("\n¡Todo listo! ¡Presiona 'Enter' cuando quieras empezar!")
clear_screen()

## Pregunta sobre año de lanzamiento
if question_release_date(movies_details_df, dificulty): counter += 1
input("Presiona 'Enter' para continuar\n")
clear_screen()

## Pregunta sobre resumen de la película
if question_overview(movies_details_df, line_width, dificulty): counter += 1
input("Presiona 'Enter' para continuar\n")
clear_screen()

## Pregunta sobre detalles de la película
if question_details(movies_details_df): counter += 1
input("Presiona 'Enter' para continuar\n")
clear_screen()

## Pregunta sobre trozo de póster
if question_poster_piece(movies_details_df, dificulty): counter += 1
input("Presiona 'Enter' para continuar\n")
clear_screen()

## Muestra contador de aciertos
dif_constant = 1 + (dificulty - 1) / 3
points = round(counter * dif_constant, 2)
print((f"\nHas acertado {counter} de 4 preguntas en el nivel de dificultad {dificulty}.\n\n"
       f"En este nivel de dificultad, cada pregunta vale {dif_constant:.2f} puntos, así que...\n\n"
       f"¡Eso hace un total de {points:.2f} puntos!\n"))

## Actualiza el ranking si fuese necesario y despide el juego
if points >= ranking.iloc[2, -1]:
    if points >= ranking.iloc[0, -1]:
        ranking.iloc[0] = [user_name, dificulty_label, points]
    elif points >= ranking.iloc[1, -1]:
        ranking.iloc[1] = [user_name, dificulty_label, points]
    else:
        ranking.iloc[2] = [user_name, dificulty_label, points]
    print("¡Guau, has conseguido entrar en el ranking de los 3 mejores jugadores de Popcorn Quiz! Míralo:\n")
    print(ranking)
    ranking.to_csv("./Ranking.txt", sep=";", header=None, encoding="ANSI")
else:
    print("Esta vez no has conseguido entrar en el ranking, ¡pero seguro que la próxima lo haces mejor!")

print(f"\n¡Ha sido un placer jugar contigo a Popcorn Quiz, {user_name}! ¡Vuelve cuando quieras! :)\n\n\n")