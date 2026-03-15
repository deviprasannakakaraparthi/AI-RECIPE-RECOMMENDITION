class RecipeMatch {
  final String title;
  final String? style;
  final String? description;
  final String? prepTime;
  final String? cookTime;
  final String? servingSuggestion;
  final String? nutrition;
  final String? videoLink;
  final List<String> ingredients;
  final List<String> instructions;

  RecipeMatch({
    required this.title,
    this.style,
    this.description,
    this.prepTime,
    this.cookTime,
    this.servingSuggestion,
    this.nutrition,
    this.videoLink,
    required this.ingredients,
    required this.instructions,
  });

  factory RecipeMatch.fromJson(Map<String, dynamic> json) {
    List<String> parseList(dynamic val) {
      if (val is List) return val.map((e) => e.toString()).toList();
      if (val is String)
        return val.split('\n').where((s) => s.trim().isNotEmpty).toList();
      return [];
    }

    return RecipeMatch(
      title: json['title'] ?? 'Unknown Recipe',
      style: json['style'],
      description: json['description'],
      prepTime: json['prep_time'],
      cookTime: json['cook_time'],
      servingSuggestion: json['serving_suggestion'],
      nutrition: json['nutrition'],
      videoLink: json['video_link'],
      ingredients: parseList(json['ingredients']),
      instructions: parseList(json['instructions']),
    );
  }
}

class RecipeResponse {
  final bool success;
  final List<String> detectedIngredients;
  final List<RecipeMatch> recipes;

  RecipeResponse({
    required this.success,
    required this.detectedIngredients,
    required this.recipes,
  });

  factory RecipeResponse.fromJson(Map<String, dynamic> json) {
    final recipesList = (json['recipes'] as List? ?? [])
        .map((r) => RecipeMatch.fromJson(r as Map<String, dynamic>))
        .toList();

    return RecipeResponse(
      success: json['success'] ?? false,
      detectedIngredients:
          List<String>.from(json['detected_ingredients'] ?? []),
      recipes: recipesList,
    );
  }
}
