import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
import os
import pickle
import logging
import random
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class RecipeIntelligence:
    def __init__(self, dataset_path=None, model_name='all-MiniLM-L6-v2'):
        # Dynamic path discovery
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        if dataset_path is None:
            # Try Docker path first, then local paths
            possible_paths = [
                os.path.join(base_dir, 'data', 'Cleaned_Indian_Food_Dataset.csv'),
                '/app/data/Cleaned_Indian_Food_Dataset.csv',
                os.path.join(base_dir, '..', 'recipes_cleaned.csv')
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    dataset_path = p
                    break
        
        self.dataset_path = dataset_path or os.path.join(base_dir, 'data', 'Cleaned_Indian_Food_Dataset.csv')
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        self.model = SentenceTransformer(model_name).to(self.device)
        self.recipes_df = None
        self.embeddings = None
        self.embedding_cache = os.path.join(base_dir, 'indian_recipe_embeddings.pkl')
        
        # Initialize Gemini
        self.gemini_active = False
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_active = True
                logger.info("Gemini AI is ACTIVE for premium recipe generation.")
            except Exception as e:
                logger.error(f"Failed to init Gemini: {e}")
        
        self.load_data()

    def load_data(self):
        if not self.dataset_path or not os.path.exists(self.dataset_path):
            logger.error(f"Dataset not found at {self.dataset_path}")
            return

        try:
            logger.info(f"Loading recipe dataset from {self.dataset_path}...")
            
            # Make cache name unique to dataset
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ds_name = os.path.basename(self.dataset_path).replace(".csv", "").replace("_cleaned", "")
            self.embedding_cache = os.path.join(base_dir, f"{ds_name}_embeddings.pkl")
            
            # Detect which dataset we are using and map columns accordingly
            if "Cleaned_Indian_Food_Dataset" in self.dataset_path:
                self.recipes_df = pd.read_csv(self.dataset_path)
                # Map to standard names
                self.recipes_df = self.recipes_df.rename(columns={
                    'TranslatedRecipeName': 'title',
                    'Cleaned-Ingredients': 'ingredients',
                    'TranslatedInstructions': 'instructions',
                    'Cuisine': 'cuisine'
                })
            else:
                self.recipes_df = pd.read_csv(
                    self.dataset_path, 
                    header=None, 
                    names=['id', 'title', 'ingredients', 'instructions', 'slug', 'ingredients_raw'],
                    on_bad_lines='skip',
                    engine='python'
                )
            
            # Cleaning and Validation
            self.recipes_df = self.recipes_df.dropna(subset=['title', 'instructions'])
            self.recipes_df['title'] = self.recipes_df['title'].astype(str).str.strip()
            self.recipes_df['instructions'] = self.recipes_df['instructions'].astype(str).str.strip()
            self.recipes_df['ingredients'] = self.recipes_df['ingredients'].astype(str).str.strip()
            
            if 'cuisine' in self.recipes_df.columns:
                self.recipes_df['cuisine'] = self.recipes_df['cuisine'].astype(str).str.strip()
            
            logger.info(f"Successfully loaded {len(self.recipes_df)} unique recipes.")

            if os.path.exists(self.embedding_cache):
                logger.info("Loading cached search embeddings...")
                with open(self.embedding_cache, 'rb') as f:
                    self.embeddings = pickle.load(f)
            else:
                logger.info("Computing embeddings for semantic search (one-time process)...")
                # Combine Title and Ingredients for the best search context
                texts = (self.recipes_df['title'] + " " + self.recipes_df['ingredients']).tolist()
                self.embeddings = self.model.encode(texts, convert_to_tensor=True, show_progress_bar=True)
                with open(self.embedding_cache, 'wb') as f:
                    pickle.dump(self.embeddings, f)
                logger.info("Embeddings cached.")

        except Exception as e:
            logger.error(f"Error loading recipe data: {e}")

    def recommend_recipe(self, detected_ingredients, cuisine="Indian", spice_level="Medium", meal_type="Lunch", food_style="Curry"):
        if self.recipes_df is None or len(self.recipes_df) == 0 or self.embeddings is None:
            logger.error("Dataset not loaded or empty. Cannot recommend.")
            return None

        # 1. Broad Filtering by Cuisine if applicable
        temp_df = self.recipes_df.copy()
        cuisine_lower = cuisine.lower()
        
        if cuisine_lower == "indian":
            keywords = [
                "masala", "curry", "paneer", "dal", "tadka", "aloo", "biryani", "roti", 
                "paratha", "chutney", "indian", "tikka", "korma", "bharta", "saag", 
                "raita", "naan", "samosa", "pakora", "ghosh", "mutter", "gobi"
            ]
            temp_df['is_match'] = temp_df['title'].str.lower().apply(lambda x: any(k in x for k in keywords))
            if temp_df['is_match'].sum() > 20: pass
        
        # 2. Semantic Search for Grounding
        query = f"Authentic {cuisine} {food_style} recipe using {', '.join(detected_ingredients)}. {meal_type} style, {spice_level} spice."
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # SAFETY CHECK: Ensure embeddings and dataframe are in sync
        if len(self.embeddings) != len(self.recipes_df):
            logger.error(f"Cache Size Mismatch! Embeddings: {len(self.embeddings)}, Recipes: {len(self.recipes_df)}")
            # If we are in sync, we can proceed. If not, we SHOULD recompute, but for now we just fail gracefully
            # to avoid the out-of-bounds error.
            return None

        cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]
        
        # 3. Combine Semantic Score with Ingredient Overlap Score
        user_ings_set = set([i.lower().strip() for i in detected_ingredients])
        
        # Get top 100 semantic matches
        top_k_indices = torch.topk(cos_scores, k=min(100, len(self.recipes_df))).indices.tolist()
        
        scored_results = []
        for idx in top_k_indices:
            try:
                if idx >= len(self.recipes_df): continue # Extra safety
                row = self.recipes_df.iloc[idx]
                title_lower = row['title'].lower()
                recipe_ings_text = str(row['ingredients']).lower()
                
                # Simple overlap score
                matches = sum(1 for ing in user_ings_set if ing in recipe_ings_text or ing in title_lower)
                overlap_score = matches / max(len(user_ings_set), 1)
                
                # Weighted final score
                final_score = (cos_scores[idx].item() * 0.5) + (overlap_score * 0.5)
                
                if food_style.lower() in title_lower: final_score += 0.15
                if cuisine_lower == "indian" and any(k in title_lower for k in ["masala", "curry", "dal", "paneer"]): 
                    final_score += 0.1
                    
                scored_results.append((final_score, idx))
            except Exception as e:
                logger.error(f"Error scoring index {idx}: {e}")
                continue
            
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_results:
            logger.warning("No recipes found in scored results loop.")
            return None
            
        best_idx = scored_results[0][1]
        best_score = scored_results[0][0]
        grounding_recipe = self.recipes_df.iloc[best_idx]

        
        # 4. Preparation for Generation
        if self.gemini_active:
            try:
                # Handle case where detected_ingredients might be empty
                ings_text = ', '.join(detected_ingredients) if detected_ingredients else "fresh seasonal ingredients"
                # Professional Prompt reflecting ALL user requirements
                prompt = (
                    f"Act as a World-Class Executive Chef. Create a UNIQUE, non-generic recipe based on the following context:\n"
                    f"DISH CONCEPT: {grounding_recipe['title']}\n"
                    f"DETECTED MAIN INGREDIENTS: {', '.join(detected_ingredients)}\n"
                    f"CUISINE: {cuisine}\n"
                    f"SPICE LEVEL: {spice_level}\n"
                    f"MEAL TYPE: {meal_type}\n"
                    f"FOOD STYLE: {food_style}\n\n"
                    f"STRICT RULES:\n"
                    f"1. ONLY use the 'Detected Main Ingredients' as the core of the dish. Do NOT add other main vegetables or meats.\n"
                    f"2. List common items like oil, salt, water, and basic spices separately under 'BASIC KITCHEN ITEMS NEEDED'.\n"
                    f"3. The recipe must be logically consistent with the ingredients. If ingredients are insufficient, pivot to the closest realistic dish.\n"
                    f"4. If the style is 'Juice' or 'Salad', skip all 'COOKING' steps and focus only on 'PREPARATION'.\n"
                    f"5. Ensure instructions are clear for absolute beginners (numbered, no jargon).\n"
                    f"6. Do NOT use a generic pattern; the instructions should reflect the specific textures and properties of the detected ingredients.\n\n"
                    f"OUTPUT FORMAT (STRICT):\n"
                    f"DISH NAME: [Unique Name]\n"
                    f"CUISINE TYPE: [e.g., {cuisine}]\n"
                    f"PREPARATION TIME: [Minutes]\n"
                    f"COOKING TIME: [Minutes or '0' for raw items]\n"
                    f"DIFFICULTY LEVEL: [Easy/Medium/Hard]\n"
                    f"INGREDIENTS USED: [The list from detected ingredients with specific measurements]\n"
                    f"BASIC KITCHEN ITEMS NEEDED: [Oil, salt, pepper, water, etc.]\n"
                    f"STEP-BY-STEP INSTRUCTIONS:\n1. [Step 1]\n2. [Step 2]\n...\n"
                    f"SERVING SUGGESTION: [How to plate/eat]\n"
                    f"NUTRITION ESTIMATE: [Optional calories/macros estimate]"
                )
                response = self.gemini_model.generate_content(prompt)
                ai_output = response.text
                
                # Accuracy Check
                hallucination_check = [ing for ing in detected_ingredients if ing.lower() not in ai_output.lower()]
                if len(hallucination_check) > len(detected_ingredients) / 2:
                    logger.warning("Gemini output seems to ignore many detected ingredients. Falling back to grounding.")
                    raise ValueError("Hallucination detected")

                title = grounding_recipe['title']
                if "DISH NAME:" in ai_output:
                    try:
                        title = ai_output.split("DISH NAME:")[1].split("\n")[0].strip()
                    except: pass
                
                return {
                    "title": title,
                    "ingredients": grounding_recipe['ingredients'],
                    "instructions": ai_output,
                    "score": best_score,
                    "is_ai_generated": True
                }
            except Exception as e:
                logger.error(f"Gemini generation or validation failed: {e}")

        # Fallback formatting for dataset recipes to match requested style roughly
        return {
            "title": grounding_recipe['title'],
            "ingredients": grounding_recipe['ingredients'],
            "instructions": f"DISH NAME: {grounding_recipe['title']}\nCUISINE TYPE: {cuisine}\nINGREDIENTS USED: {grounding_recipe['ingredients']}\n\nINSTRUCTIONS:\n{grounding_recipe['instructions']}",
            "score": best_score,
            "is_ai_generated": False
        }

    def generate_steps(self, recipe_name, ingredients):
        # Compatibility method
        pass

