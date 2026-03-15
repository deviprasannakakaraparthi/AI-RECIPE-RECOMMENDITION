package com.antigravity.food.ui.viewmodel

import androidx.compose.runtime.State
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

import com.antigravity.food.api.RecipeModel

data class RecipeUiState(
    val ingredients: List<String> = emptyList(),
    val recipes: List<RecipeModel> = emptyList(),
    val selectedRecipe: RecipeModel? = null,
    val isAnalyzing: Boolean = false,
    val detectedIngredients: List<String> = emptyList(),
    val errorMessage: String? = null
)

class RecipeViewModel : ViewModel() {
    private val _uiState = mutableStateOf(RecipeUiState())
    val uiState: State<RecipeUiState> = _uiState

    val mealType = mutableStateOf("Lunch")
    val cuisine = mutableStateOf("Indian")
    val spiceLevel = mutableStateOf("Medium")
    val foodStyle = mutableStateOf("Curry")

    fun addIngredient(ingredient: String) {
        if (ingredient.isNotBlank() && !_uiState.value.ingredients.contains(ingredient)) {
            _uiState.value = _uiState.value.copy(
                ingredients = _uiState.value.ingredients + ingredient,
                errorMessage = null
            )
        }
    }

    fun removeIngredient(ingredient: String) {
        _uiState.value = _uiState.value.copy(
            ingredients = _uiState.value.ingredients - ingredient
        )
    }

    fun selectRecipe(recipe: RecipeModel) {
        _uiState.value = _uiState.value.copy(selectedRecipe = recipe)
    }

    fun clearError() {
        _uiState.value = _uiState.value.copy(errorMessage = null)
    }

    fun analyzeImage(imageBytes: ByteArray) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isAnalyzing = true, errorMessage = null)
            try {
                val requestFile = imageBytes.toRequestBody("image/jpeg".toMediaTypeOrNull())
                val body = MultipartBody.Part.createFormData("file", "upload.jpg", requestFile)
                
                fun createPart(value: String) = value.toRequestBody("text/plain".toMediaTypeOrNull())

                val response = com.antigravity.food.api.RetrofitClient.apiService.analyzeImage(
                    body,
                    createPart(mealType.value),
                    createPart(cuisine.value),
                    createPart(spiceLevel.value),
                    createPart(foodStyle.value)
                )
                
                if (response.success && response.recipes.isNotEmpty()) {
                    _uiState.value = _uiState.value.copy(
                        detectedIngredients = response.detectedIngredients,
                        ingredients = (uiState.value.ingredients + response.detectedIngredients).distinct(),
                        recipes = response.recipes,
                        selectedRecipe = response.recipes.firstOrNull(),
                        isAnalyzing = false,
                        errorMessage = null
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        detectedIngredients = response.detectedIngredients,
                        ingredients = (uiState.value.ingredients + response.detectedIngredients).distinct(),
                        isAnalyzing = false,
                        errorMessage = "No recipes found for detected ingredients. Try adding more."
                    )
                }
            } catch (e: Exception) {
                e.printStackTrace()
                _uiState.value = _uiState.value.copy(
                    isAnalyzing = false,
                    errorMessage = "Could not connect to server. Make sure the backend is running."
                )
            }
        }
    }

    fun getRecommendation() {
        val currentIngredients = _uiState.value.ingredients
        if (currentIngredients.isEmpty()) return

        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isAnalyzing = true, errorMessage = null)
            try {
                val request = com.antigravity.food.api.RecipeRequest(
                    ingredients = currentIngredients,
                    mealType = mealType.value,
                    cuisine = cuisine.value,
                    spiceLevel = spiceLevel.value,
                    foodStyle = foodStyle.value
                )
                
                val response = com.antigravity.food.api.RetrofitClient.apiService.getRecipe(request)
                
                if (response.success && response.recipes.isNotEmpty()) {
                    _uiState.value = _uiState.value.copy(
                        recipes = response.recipes,
                        selectedRecipe = response.recipes.firstOrNull(),
                        isAnalyzing = false,
                        errorMessage = null
                    )
                } else {
                    _uiState.value = _uiState.value.copy(
                        isAnalyzing = false,
                        errorMessage = "No recipes found. Try different ingredients or preferences."
                    )
                }
            } catch (e: Exception) {
                e.printStackTrace()
                _uiState.value = _uiState.value.copy(
                    isAnalyzing = false,
                    errorMessage = "Could not connect to the Recipe Server. Please check your connection."
                )
            }
        }
    }
}
