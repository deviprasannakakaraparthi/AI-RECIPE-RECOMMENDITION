package com.antigravity.food.data.network

import okhttp3.MultipartBody
import retrofit2.http.*

data class DetectionResponse(
    val ingredients: List<String>
)

data class RecipeResponse(
    val recipe_name: String,
    val ingredients: List<String>,
    val instructions: String
)

interface RecipeApiService {
    @Multipart
    @POST("detect")
    suspend fun detectIngredients(
        @Part file: MultipartBody.Part
    ): DetectionResponse

    @POST("recommend")
    suspend fun recommendRecipe(
        @Body ingredients: List<String>
    ): RecipeResponse
}
