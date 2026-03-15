from sentence_transformers import SentenceTransformer, util
import pandas as pd
import os
import torch

# Load a high-quality model for semantic search
model = SentenceTransformer('all-MiniLM-L6-v2')

# Use the large cleaned dataset from root
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_PATH = os.path.join(base_dir, "recipes_cleaned.csv")

recipes_df = pd.DataFrame()
recipe_embeddings = None

# INDIAN BACKUP - Quality suggestions if search fails
INDIAN_CURATED = [
    {"title": "Paneer Butter Masala", "ingredients": "paneer, tomato, butter, ginger", "instructions": "1. Sauté ginger-garlic paste. 2. Add tomato puree and cook. 3. Add butter, cream and paneer cubes. 4. Simmer for 5 mins."},
    {"title": "Baingan Bharta", "ingredients": "brinjal, onion, tomato", "instructions": "1. Roast brinjal on flame. 2. Mash it. 3. Sauté onions and tomatoes. 4. Mix mashed brinjal and spices."},
    {"title": "Dal Tadka", "ingredients": "lentils, cumin, garlic, red chilli", "instructions": "1. Pressure cook dal with turmeric. 2. Heat oil, add cumin and garlic. 3. Pour tadka over dal. 4. Garnish with cilantro."}
]

def load_data():
    global recipes_df, recipe_embeddings
    
    # Try to load the big dataset
    if os.path.exists(DATA_PATH):
        try:
            # We use a very robust reading method because the CSV has messy quotes/newlines
            df = pd.read_csv(
                DATA_PATH,
                header=None,
                on_bad_lines='skip',
                engine='python',
                quotechar='"',
                skipinitialspace=True
            )
            
            # Identify columns by content
            # 0:ID, 1:Title, 2:Ingredients, 3:Instructions
            df = df[[1, 2, 3]].dropna()
            df.columns = ['title', 'ingredients', 'instructions']
            
            # Ensure titles and instructions are clean
            df['title'] = df['title'].astype(str).str.strip()
            df['instructions'] = df['instructions'].astype(str).str.strip()
            
            # Filter for Indian-style recipes (Broad filter)
            india_keywords = ['masala', 'curry', 'indian', 'paneer', 'dal', 'tadka', 'aloo', 'kerala', 'spiced', 'tikka']
            is_indian = df['title'].str.lower().str.contains('|'.join(india_keywords))
            india_df = df[is_indian].copy()
            
            # Combine with curated small list
            recipes_df = pd.concat([pd.DataFrame(INDIAN_CURATED), india_df], ignore_index=True)
            print(f"Loaded {len(recipes_df)} Indian-style recipes from dataset.")
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            recipes_df = pd.DataFrame(INDIAN_CURATED)
    else:
        recipes_df = pd.DataFrame(INDIAN_CURATED)

    if not recipes_df.empty:
        # Precompute embeddings on Titles + Ingredients for best matching
        recipes_df['search_text'] = recipes_df['title'] + " " + recipes_df['ingredients'].astype(str)
        recipe_embeddings = model.encode(recipes_df['search_text'].tolist(), convert_to_tensor=True)

# Load data on start
load_data()

def recommend_recipes_full(user_ingredients, target_name=None, top_k=5):
    """Returns full recipe objects (title + instructions)"""
    if recipe_embeddings is None or recipes_df.empty:
        return INDIAN_CURATED[:top_k]

    # If user provided a specific dish name, we weight it heavily
    if target_name:
        query = f"Recipe for {target_name} using {', '.join(user_ingredients)}"
    else:
        query = f"Recipe using {', '.join(user_ingredients)}"
        
    query_emb = model.encode([query], convert_to_tensor=True)
    
    # Calculate scores
    cosine_scores = util.cos_sim(query_emb, recipe_embeddings)[0]
    
    # Get top K
    top_results = torch.topk(cosine_scores, k=min(top_k, len(recipes_df)))
    
    final_recipes = []
    for idx in top_results.indices:
        recipe = recipes_df.iloc[idx.item()]
        # Verify it's a real recipe name
        if len(str(recipe['title']).split()) < 15:
            # Clean ingredients string (remove [], quotes)
            clean_ingredients = str(recipe['ingredients']).replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            
            final_recipes.append({
                "title": recipe['title'],
                "ingredients": clean_ingredients,
                "instructions": recipe['instructions']
            })
            
    return final_recipes

def recommend_recipes(user_ingredients, cuisine="Indian", top_k=5):
    """Old interface returning just titles for backward compatibility if needed"""
    results = recommend_recipes_full(user_ingredients, top_k=top_k)
    return [r['title'] for r in results]
