import requests
from bs4 import BeautifulSoup
import mysql.connector

# Connexion à MySQL
config = {
  'user': 'fulgure',
  'password': 'p9Ek6vB7H3i6Gz',
  'host': 'localhost',
  'database': 'fulgure',
  'raise_on_warnings': True
}
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Fonction pour ajouter une URL à la base de données si elle n'y est pas déjà
def add_url(url):
    cursor.execute('SELECT url FROM urls WHERE url=%s', (url,))
    if not cursor.fetchone():
        try:
            cursor.execute('INSERT INTO urls (url, explored) VALUES (%s, 0)', (url,))
            conn.commit()
        except mysql.connector.errors.IntegrityError:
            # Dupliqué, donc ne rien faire
            pass

# Fonction pour récupérer la première URL non explorée
def get_next_unexplored_url():
    cursor.execute('SELECT url FROM urls WHERE explored=0 LIMIT 1')
    row = cursor.fetchone()
    print(row)
    return row[0] if row else None

# Fonction pour marquer une URL comme explorée
def mark_as_explored(url):
    cursor.execute('UPDATE urls SET explored=1 WHERE url=%s', (url,))
    conn.commit()

# Crawler
def crawler(url):
    
    try:
        response = requests.get(url, timeout=10)  # Ajout d'un timeout de 10 secondes
    except requests.Timeout:
        print(f"Timeout pour l'URL: {url}")
        mark_as_explored(url)
        return
    except requests.RequestException as e:
        print(f"Erreur de requête pour l'URL {url}:", e)
        mark_as_explored(url)
        return

    soup = BeautifulSoup(response.text, 'html.parser')  # Utilisez response.text pour gérer l'encodage comme mentionné précédemment

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']

        if href.startswith('http://') or href.startswith('https://'):
            add_url(href)

    mark_as_explored(url)


# Point de départ
start_url = "https://www.google.com/"
add_url(start_url)

# Boucle principale
while True:
    next_url = get_next_unexplored_url()
    if not next_url:
        break
    print(next_url)
    try:
        crawler(next_url)
    except Exception as e:
        print(f"Erreur lors de l'exploration de {next_url}:", e)
        mark_as_explored(next_url)  # Marquer comme exploré même en cas d'erreur pour éviter de rester bloqué dessus

conn.close()
