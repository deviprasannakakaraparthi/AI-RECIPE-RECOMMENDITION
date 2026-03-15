
package com.antigravity.food.api

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface ApiService {
    @Multipart
    @POST("analyze")
    suspend fun analyzeImage(
        @Part image: MultipartBody.Part,
        @Part("meal_type") mealType: RequestBody,
        @Part("cuisine") cuisine: RequestBody,
        @Part("spice_level") spiceLevel: RequestBody,
        @Part("food_style") foodStyle: RequestBody
    ): RecipeResponse

    @POST("recipes/generate")
    suspend fun getRecipe(
        @Body request: RecipeRequest
    ): RecipeResponse
}
