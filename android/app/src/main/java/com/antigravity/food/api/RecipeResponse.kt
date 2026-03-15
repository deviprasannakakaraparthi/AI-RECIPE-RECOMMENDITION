
package com.antigravity.food.api

import com.google.gson.annotations.SerializedName

data class RecipeResponse(
    @SerializedName("detected_ingredients") val detectedIngredients: List<String> = emptyList(),
    @SerializedName("recipes") val recipes: List<RecipeModel> = emptyList(),
    @SerializedName("success") val success: Boolean = false
)

data class RecipeModel(
    @SerializedName("title") val title: String,
    @SerializedName("style") val style: String? = null,
    @SerializedName("description") val description: String? = null,
    @SerializedName("prep_time") val prepTime: String? = null,
    @SerializedName("cook_time") val cookTime: String? = null,
    @SerializedName("serving_suggestion") val servingSuggestion: String? = null,
    @SerializedName("nutrition") val nutrition: String? = null,
    @SerializedName("video_link") val videoLink: String? = null,
    @SerializedName("ingredients") val ingredients: List<String>? = null,
    @SerializedName("instructions") val instructions: List<String>? = null,
    @SerializedName("user_ingredients_used") val userIngredientsUsed: List<String>? = null,
    @SerializedName("additional_ingredients_needed") val additionalIngredientsNeeded: List<String>? = null
)
