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
    # Use relative path for cross-platform compatibility
    dataset_path = os.path.join(os.getcwd(), 'recipes_cleaned.csv')
    if not os.path.exists(dataset_path):
        # Fallback to backend data folder if running from root
        dataset_path = os.path.join(os.getcwd(), 'backend', 'data', 'Cleaned_Indian_Food_Dataset.csv')

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
        
        if result and len(result) > 0:
            for r in result:
                print(f"Match Found: {r['title']} ({r.get('style', 'Generic')})")
                print(f"Score: {r.get('score', 0)}")
                if isinstance(r['instructions'], list):
                    print(f"Steps (Step 1): {r['instructions'][0]}...")
                else:
                    print(f"Steps (truncated): {r['instructions'][:200]}...")
                print("-" * 20)
        else:
            print("No match found.")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
