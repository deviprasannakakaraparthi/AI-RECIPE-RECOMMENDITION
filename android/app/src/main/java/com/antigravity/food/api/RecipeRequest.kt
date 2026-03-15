package com.antigravity.food.api

import com.google.gson.annotations.SerializedName

data class RecipeRequest(
    @SerializedName("ingredients") val ingredients: List<String>,
    @SerializedName("recipe_name") val recipeName: String? = null,
    @SerializedName("meal_type") val mealType: String = "Lunch",
    @SerializedName("cuisine") val cuisine: String = "Indian",
    @SerializedName("spice_level") val spiceLevel: String = "Medium",
    @SerializedName("food_style") val foodStyle: String = "Curry"
)
