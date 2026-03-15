from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load pretrained T5 model
try:
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
except Exception as e:
    print(f"Error loading T5 model: {e}")
    # Fallback or re-raise depending on requirements. For now let's assume it works or fails hard.
    raise e

def generate_recipe(ingredients, cuisine=None):
    prompt = f"Ingredients: {', '.join(ingredients)}"
    if cuisine:
        prompt += f". Cuisine: {cuisine}"
    prompt += " -> Recipe steps:"
    
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=300)
    recipe_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return recipe_text
