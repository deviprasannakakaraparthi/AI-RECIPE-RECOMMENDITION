import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';
import '../models/recipe.dart';

class ApiService {
  static String get baseUrl {
    if (kIsWeb) {
      // On web, use the relative path since frontend is served by backend
      return "";
    }
    // Fallback for mobile testing
    return "https://real-hounds-double.loca.lt";
  }

  /// Upload image bytes (works on web & mobile)
  Future<RecipeResponse?> analyzeImageBytes(
    Uint8List bytes,
    String fileName, {
    String mealType = "Lunch",
    String cuisine = "Indian",
    String spiceLevel = "Medium",
    String foodStyle = "Curry",
  }) async {
    try {
      var request =
          http.MultipartRequest('POST', Uri.parse('$baseUrl/analyze'));
      
      request.headers['User-Agent'] = 'Flutter-App';

      request.files.add(http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: fileName,
      ));

      request.fields['meal_type'] = mealType;
      request.fields['cuisine'] = cuisine;
      request.fields['spice_level'] = spiceLevel;
      request.fields['food_style'] = foodStyle;

      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return RecipeResponse.fromJson(jsonDecode(response.body));
      } else {
        print("API Error: ${response.statusCode} - ${response.body}");
        return null;
      }
    } catch (e) {
      print("Network Error: $e");
      return null;
    }
  }

  Future<RecipeResponse?> generateRecipe({
    required List<String> ingredients,
    String mealType = "Lunch",
    String cuisine = "Indian",
    String spiceLevel = "Medium",
    String foodStyle = "Curry",
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/recipes/generate'),
        headers: {
            "Content-Type": "application/json",
            "User-Agent": "Flutter-App"
        },
        body: jsonEncode({
          "ingredients": ingredients,
          "meal_type": mealType,
          "cuisine": cuisine,
          "spice_level": spiceLevel,
          "food_style": foodStyle,
        }),
      );

      if (response.statusCode == 200) {
        return RecipeResponse.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print("Network Error: $e");
      return null;
    }
  }
}
