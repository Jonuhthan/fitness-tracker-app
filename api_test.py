import requests
import json

# OpenFoodFacts API
endpoint = "https://world.openfoodfacts.org/api/v0/product/"
barcode = '0078742136035'
url = f"{endpoint}{barcode}.json"
response = requests.get(url)
data = response.json()

nutrients = data['product']['nutriments'] 

# Want data organized as dictionary, with keys as nutrients and values as tuple (amount, unit)

relevant_data = {
    'Calories': (nutrients['energy-kcal_serving'], nutrients['energy-kcal_unit']),
    'Total Fat':(nutrients['fat_serving'], nutrients['fat_unit']),
    'Saturated Fat':(nutrients['saturated-fat_serving'], nutrients['saturated-fat_unit']),
    'Trans-fat':(nutrients['trans-fat_serving'], nutrients['trans-fat_unit']),
    'Cholesterol':(nutrients['cholesterol_serving'], nutrients['cholesterol_unit']),
    'Sodium':(nutrients['sodium_serving'], nutrients['sodium_unit']),
    'Total Carbohydrate':(nutrients['carbohydrates_serving'], nutrients['carbohydrates_unit']),
    'Fiber':(nutrients['fiber_serving'], nutrients['fiber_unit']),
    'Sugar':(nutrients['sugars_serving'], nutrients['sugars_unit']),
    'Protein':(nutrients['proteins_serving'], nutrients['proteins_unit'])
}

print(relevant_data)