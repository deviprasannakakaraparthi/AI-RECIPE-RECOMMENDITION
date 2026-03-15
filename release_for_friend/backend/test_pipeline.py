import sys
import os
import pandas as pd

# Add current dir to path
sys.path.append(os.getcwd())

from recommendation import RecipeIntelligence
from detection import IngredientDetector
import logging

logging.basicConfig(level=logging.INFO)

def test():
    print("--- Initializing Engines ---")
    dataset_path = '/Users/jarnox/FOOD/recipes_cleaned.csv'
    print(f"Dataset exists? {os.path.exists(dataset_path)}")
    
    try:
        rec = RecipeIntelligence(dataset_path=dataset_path)
        if rec.recipes_df is not None:
            print(f"Loaded {len(rec.recipes_df)} recipes.")
        else:
            print("Recipes DF is None!")
            
        det = IngredientDetector()
        
        print("\n--- Testing Recommendation ---")
        test_ings = ["tomato", "onion", "garlic"]
        result = rec.recommend_recipe(test_ings, cuisine="Indian")
        
        if result:
            print(f"Match Found: {result['title']}")
            print(f"Score: {result['score']}")
            print(f"Steps (truncated): {result['instructions'][:200]}...")
        else:
            print("No match found.")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
