package com.antigravity.food

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.antigravity.food.ui.theme.FoodTheme
import com.antigravity.food.ui.navigation.RecipeNavGraph
import com.antigravity.food.ui.viewmodel.RecipeViewModel


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // In a production app, use Hilt or a Factory for the ViewModel
            val viewModel = remember { RecipeViewModel() }

            FoodTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    RecipeNavGraph(viewModel = viewModel)
                }
            }
        }
    }
}
