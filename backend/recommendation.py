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
            # Try multiple variations to be safe
            possible_paths = [
                os.path.join(base_dir, 'data', 'Cleaned_Indian_Food_Dataset.csv'),
                os.path.join(base_dir, 'Cleaned_Indian_Food_Dataset.csv'),
                os.path.join(os.getcwd(), 'data', 'Cleaned_Indian_Food_Dataset.csv'),
                'data/Cleaned_Indian_Food_Dataset.csv',
                'Cleaned_Indian_Food_Dataset.csv'
            ]
            logger.info(f"Searching for dataset in: {possible_paths}")
            for p in possible_paths:
                if os.path.exists(p):
                    dataset_path = p
                    logger.info(f"FOUND dataset at: {p}")
                    break
        
        if not dataset_path:
             logger.error("Could not find Cleaned_Indian_Food_Dataset.csv in any expected location.")

        self.dataset_path = dataset_path
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        self.model = SentenceTransformer(model_name).to(self.device)
        self.recipes_df = None
        self.embeddings = None
        self.embedding_cache = None
        
        # Initialize Gemini
        self.gemini_active = False
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                
                # Use standard model names with latest variants
                model_names = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro-latest', 'gemini-pro']
                self.gemini_model = None
                
                for m_name in model_names:
                    try:
                        self.gemini_model = genai.GenerativeModel(m_name)
                        # Test if the model actually works with a tiny prompt
                        # self.gemini_model.generate_content("test", generation_config={"max_output_tokens": 1})
                        logger.info(f"Targeting Gemini model: {m_name}")
                        break
                    except Exception as e:
                        logger.warning(f"Could not init model {m_name}: {e}")
                
                if self.gemini_model:
                    self.gemini_active = True
                    logger.info("Gemini AI is ACTIVE for premium recipe generation.")
                else:
                    logger.error("Failed to initialize any Gemini model.")
            except Exception as e:
                logger.error(f"Failed to init Gemini: {e}")
        
        self.load_data()

    def load_data(self):
        if not self.dataset_path or not os.path.exists(self.dataset_path):
            logger.error(f"FATAL: Dataset path invalid or not found: {self.dataset_path}")
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
                logger.info(f"Loading cached search embeddings from {self.embedding_cache}...")
                try:
                    with open(self.embedding_cache, 'rb') as f:
                        self.embeddings = pickle.load(f)
                except Exception as e:
                    logger.warning(f"Cached embeddings corrupted or incompatible ({e}). Regenerating...")
                    self.embeddings = None
            
            if self.embeddings is None:
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
        if self.recipes_df is None:
            logger.error("Recommend Failed: self.recipes_df is None")
            return []
        if len(self.recipes_df) == 0:
            logger.error("Recommend Failed: self.recipes_df is Empty")
            return []
        if self.embeddings is None:
            logger.error("Recommend Failed: self.embeddings is None")
            return []

        # 1. INGREDIENT-FIRST SEARCH
        # Build user ingredient set
        user_ings_set = set([i.lower().strip() for i in detected_ingredients])
        cuisine_lower = cuisine.lower()
        
        logger.info(f"Searching recipes for ingredients: {user_ings_set}, cuisine={cuisine}, style={food_style}")
        
        # Pass 1: Direct ingredient matching — find ALL recipes containing user ingredients
        ingredient_matched_indices = []
        for idx in range(len(self.recipes_df)):
            row = self.recipes_df.iloc[idx]
            recipe_ings_text = str(row['ingredients']).lower()
            title_lower = str(row['title']).lower()
            
            matches = sum(1 for ing in user_ings_set if ing in recipe_ings_text or ing in title_lower)
            if matches > 0:
                ingredient_matched_indices.append((matches / max(len(user_ings_set), 1), idx))
        
        # Sort by overlap ratio descending
        ingredient_matched_indices.sort(key=lambda x: x[0], reverse=True)
        
        # Variety Injection: Take top 300 but then randomly sample 100 from them
        # to ensure we don't always look at the exact same "best" pool
        top_slice = ingredient_matched_indices[:300]
        if len(top_slice) > 100:
             sampled_slice = random.sample(top_slice, 100)
        else:
             sampled_slice = top_slice
             
        ingredient_pool = set(idx for _, idx in sampled_slice)
        
        logger.info(f"Pass 1: Found {len(ingredient_matched_indices)} recipes. Pooled 100 for variety.")
        
        # 2. Semantic Search — INGREDIENT-focused query (not style-focused)
        # Put ingredients first and prominently in the query
        ings_str = ', '.join(detected_ingredients)
        query = f"Recipe made with {ings_str}. {cuisine} {food_style} {meal_type}."
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # SAFETY CHECK
        if len(self.embeddings) != len(self.recipes_df):
            logger.error(f"Cache Size Mismatch! Embeddings: {len(self.embeddings)}, Recipes: {len(self.recipes_df)}")
            return []

        cos_scores = util.cos_sim(query_embedding, self.embeddings)[0]
        
        # Get top 200 semantic matches
        top_k_indices = torch.topk(cos_scores, k=min(200, len(self.recipes_df))).indices.tolist()
        
        # Merge both pools
        all_candidate_indices = ingredient_pool.union(set(top_k_indices))
        
        # 3. Score ALL candidates — INGREDIENT OVERLAP IS KING (70/30 split)
        scored_results = []
        for idx in all_candidate_indices:
            try:
                if idx >= len(self.recipes_df): continue
                row = self.recipes_df.iloc[idx]
                title_lower = str(row['title']).lower()
                recipe_ings_text = str(row['ingredients']).lower()
                
                # Ingredient overlap score (THE PRIMARY SIGNAL)
                matches = sum(1 for ing in user_ings_set if ing in recipe_ings_text or ing in title_lower)
                overlap_score = matches / max(len(user_ings_set), 1)
                
                # REMOVED HARD FILTER: Let semantic search work even if 0 hard matches
                # if matches == 0:
                #     continue
                
                # Semantic similarity score (secondary signal)
                semantic_score = cos_scores[idx].item()
                
                # Weighted final score — ingredients dominate
                final_score = (overlap_score * 0.70) + (semantic_score * 0.30)
                
                # Add a tiny bit of randomness for variety in results
                final_score += random.uniform(0, 0.02)
                
                # STRONG style/cuisine boost (User requested style MUST be prioritized)
                style_lower = food_style.lower()
                if style_lower in title_lower: 
                    final_score += 0.25 # Significant boost for style match
                
                # Special handling for 'Soup' which is often called 'Shorba' or 'Rasam' in Indian cuisine
                if style_lower == "soup":
                    if any(word in title_lower for word in ["soup", "shorba", "rasam", "stew", "broth", "porridge"]):
                        final_score += 0.30
                
                # Special handling for 'Dessert'
                if any(k in style_lower for k in ["dessert", "sweet"]):
                    if any(k in title_lower for k in ["sweet", "kheer", "halwa", "laddu", "payasam", "ice cream", "cake", "pudding", "shrikhand"]):
                        final_score += 0.30
                
                scored_results.append((final_score, idx))
            except Exception as e:
                logger.error(f"Error scoring index {idx}: {e}")
                continue
            
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_results:
            logger.warning("No recipes found in scored results loop. Relying entirely on AI generation.")
            best_indices = []
        else:
            # Get top N distinct grounding recipes with randomization for variety
            seen_titles = set()
            candidates = []
            # Sort current results by score to find the truly best ones first
            scored_results.sort(key=lambda x: x[0], reverse=True)
            
            for s, idx in scored_results[:150]:  # Consider top 150
                title = self.recipes_df.iloc[idx]['title']
                title_clean = title.lower().strip()
                if title_clean not in seen_titles:
                    seen_titles.add(title_clean)
                    candidates.append((s, idx))
                if len(candidates) >= 30:
                    break
            
            # Randomly sample from candidates for variety
            if len(candidates) > 4:
                # We skip the absolute best one sometimes to provide variety
                # but keep it in the pool.
                selected = random.sample(candidates, 4)
                best_indices = [idx for _, idx in selected]
            else:
                best_indices = [idx for _, idx in candidates]
        
        grounding_recipes = [self.recipes_df.iloc[i] for i in best_indices]
        
        # Build reference dishes string for better grounding
        ref_dishes = ", ".join([r['title'] for r in grounding_recipes[:3]]) if grounding_recipes else f"Innovative {cuisine} {food_style}"

        # 4. Preparation for AI Generation
        if self.gemini_active:
            try:
                # Handle case where detected_ingredients might be empty
                ings_text = ', '.join(detected_ingredients) if detected_ingredients else "fresh seasonal ingredients"
                
                # AI-Powered Prompt — generates 4 UNIQUE recipes
                # KEY FEATURE: Strictly adheres to user ingredients, especially for small lists.
                prompt = (
                    f"Act as a World-Class Executive Chef specializing in 'Resourceful Cooking'.\n"
                    f"USER'S AVAILABLE INGREDIENTS: [{ings_text}]\n\n"
                    
                    f"CRITICAL INGREDIENT RULES (STRICT):\n"
                    f"1. THE MAIN STAR MUST BE THE USER'S INGREDIENTS. If the user only has 'Tomato', do NOT suggest 'Tomato Chicken' or 'Paneer Tomato'. Suggest 'Tomato Soup', 'Tomato Chutney', 'Gazpacho', or 'Roasted Tomatoes'.\n"
                    f"2. PROTEIN RULE: NEVER add major proteins like Chicken, Meat, Paneer, Tofu, or Fish if the user did not provide them. This is a deal-breaker.\n"
                    f"3. STAPLE RULE: You may ONLY add basic pantry staples that most people have: Oil/Ghee, Salt, Water, Sugar, Pepper, and basic dry spices (Cumin, Turmeric, Chili powder). If you add anything else (like garlic, onion, or cream), it MUST be marked as 'optional suggested' and listed in 'additional_ingredients_needed'.\n"
                    f"4. SENSITIVITY: If the user provides only 1-2 ingredients, focus on recipes that specifically showcase those items (e.g., a simple salad, a concentrated sauce, or a roasted appetizer).\n\n"
                    
                    f"Create FOUR DISTINCT and UNIQUE recipe options:\n"
                    f"Option 1: 'The Purest Form' — The best possible dish using ONLY the user's ingredients + salt/oil.\n"
                    f"Option 2: 'Chef's Minimalist Special' — A gourmet version with 1-2 extra spices/staples.\n"
                    f"Option 3: 'Resourceful & Creative' — A surprising way to use these specific items.\n"
                    f"Option 4: 'Quick & Healthy' — A light preparation focusing on the natural flavors.\n\n"
                    
                    f"SETTINGS:\n"
                    f"CUISINE: {cuisine}\n"
                    f"SPICE LEVEL: {spice_level}\n"
                    f"MEAL TYPE: {meal_type}\n"
                    f"STYLE: {food_style}\n"
                    f"REFERENCE (for inspiration only): {ref_dishes}\n\n"
                    
                    f"STRICT OUTPUT RULES:\n"
                    f"1. Return ONLY valid JSON. No markdown, no text before or after.\n"
                    f"2. JSON must be a list of FOUR objects.\n"
                    f"3. Keys: 'title', 'style', 'description', 'prep_time', 'cook_time', 'ingredients' (list), 'instructions' (list), 'serving_suggestion', 'nutrition', 'user_ingredients_used', 'additional_ingredients_needed'.\n"
                    f"4. In the 'description', emphasize that this recipe is optimized for the user's limited ingredients.\n"
                    f"5. Each recipe title must be UNIQUE and DIFFERENT from the others.\n"
                    f"6. Steps must be numbered, detailed, and clear. Be professional.\n"
                    f"7. Include approximate calorie count in the 'nutrition' field.\n"
                    f"8. The description should mention that the recipe is a {food_style} version using the user's ingredients.\n"
                )
                
                response = self.gemini_model.generate_content(prompt)
                ai_output = response.text.replace("```json", "").replace("```", "").strip()
                
                import json
                recipes = json.loads(ai_output)
                
                # Validate and format
                final_recipes = []
                seen = set()
                for r in recipes:
                    # Ensure minimal fields and unique titles
                    if 'title' in r and 'instructions' in r:
                        title_key = r['title'].lower().strip()
                        if title_key in seen:
                            continue  # Skip duplicate titles
                        seen.add(title_key)
                        
                        r['is_ai_generated'] = True
                        # Ensure instructions is a list
                        if isinstance(r['instructions'], list):
                             pass 
                        elif isinstance(r['instructions'], str):
                             r['instructions'] = [step.strip() for step in r['instructions'].split('\n') if step.strip()]
                        
                        # Ensure ingredients is a list
                        if isinstance(r['ingredients'], str):
                            r['ingredients'] = [x.strip() for x in r['ingredients'].split(',') if x.strip()]
                        
                        # Ensure the new fields exist with defaults
                        if 'user_ingredients_used' not in r:
                            r['user_ingredients_used'] = list(detected_ingredients)
                        if 'additional_ingredients_needed' not in r:
                            r['additional_ingredients_needed'] = [
                                ing for ing in (r.get('ingredients') or [])
                                if '(additional)' in ing.lower()
                            ]
                        
                        final_recipes.append(r)
                
                if len(final_recipes) >= 1:
                    logger.info(f"AI generated {len(final_recipes)} recipes using [{ings_text}] + additional suggestions")
                    return final_recipes

            except Exception as e:
                logger.error(f"Gemini generation or validation failed: {e}")
                # Fallthrough to fallback

        # Fallback: Return dataset recipes with variety
        fallback_results = []
        styles = ["Authentic/Homestyle", "Restaurant Recommendation", "Quick Alternative", "Classic Recipe"]
        
        # Grounding recipes is defined in the previous pass
        for i, row in enumerate(grounding_recipes):
            fallback_results.append({
                "title": row['title'],
                "style": styles[i] if i < len(styles) else "Alternative",
                "description": f"A classic {row['title']} recipe from our curated collection.",
                "prep_time": "15-20 mins",
                "cook_time": "30-40 mins",
                "ingredients": [x.strip() for x in str(row['ingredients']).split(',')],
                "instructions": [x.strip() for x in str(row['instructions']).split('.') if len(x) > 10],
                "serving_suggestion": "Served hot with rice or bread.",
                "nutrition": "Approx. 300-400 kcal",
                "is_ai_generated": False
            })

        if not fallback_results:
             # Final absolute fallback if even grounding_recipes was empty
             fallback_results.append({
                "title": f"Chef's Custom {cuisine} Surprise",
                "style": "Chef's Special",
                "description": f"An innovative {food_style} tailored to your unique ingredient list.",
                "prep_time": "10 mins",
                "cook_time": "20 mins",
                "ingredients": detected_ingredients,
                "instructions": [
                    f"Clean and prepare your {', '.join(detected_ingredients[:3])}.",
                    "Saute with oil and your favorite spices.",
                    f"Cook until tender in a {food_style} style.",
                    "Garnish and serve hot!"
                ],
                "serving_suggestion": "Enjoy this custom creation!",
                "nutrition": "Approx. 250 kcal",
                "is_ai_generated": True
             })
             
        logger.info(f"Returning {len(fallback_results)} fallback recipes.")
        return fallback_results

    def generate_steps(self, recipe_name, ingredients):
        # Compatibility method
        pass

